# ============================================
# AfiliaML — Scraper de Mercado Livre
# Extrai ofertas e detalhes de produtos
# ============================================

import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import asyncio
from app.repositories.product_repo import product_repository
from app.repositories.price_history_repo import price_history_repository
from app.utils.slugify import gerar_slug

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}


async def extrair_detalhes_ml(url: str) -> dict | None:
    """Acessa a página do produto e extrai detalhes adicionais."""
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                return None
            
            soup = BeautifulSoup(resp.text, "lxml")
            
            # Tentar pegar imagem de alta resolução do script ou meta tag
            img_url = None
            meta_img = soup.find("meta", property="og:image")
            if meta_img:
                img_url = meta_img.get("content")
            
            if not img_url:
                img = soup.select_one(".ui-pdp-gallery__figure__image, .ui-pdp-image, img.ui-pdp-image")
                if img:
                    img_url = img.get("data-zoom") or img.get("data-src") or img.get("src")
            
            desc_el = soup.select_one(".ui-pdp-description__content")
            description = desc_el.get_text(strip=True)[:500] if desc_el else ""
            
            return {
                "imageUrl": img_url,
                "description": description
            }
    except Exception as e:
        print(f"Erro ao extrair detalhes de {url}: {e}")
        return None


def limpar_preco(item_soup) -> float:
    """Extrai e limpa o preço lidando com centavos e separadores brasileiros."""
    try:
        # Tenta os seletores padrão
        fraction_el = item_soup.select_one(".andes-money-amount__fraction, .ui-pdp-price__part--fraction")
        cents_el = item_soup.select_one(".andes-money-amount__cents, .ui-pdp-price__part--cents")
        
        if fraction_el:
            fraction = fraction_el.get_text(strip=True).replace(".", "")
            cents = cents_el.get_text(strip=True) if cents_el else "00"
            return float(f"{fraction}.{cents}")
            
        # Fallback: Regex no texto completo do container
        import re
        text = item_soup.get_text(separator=" ", strip=True)
        # Procura padrões como "R$ 1.234,56" ou "1234,56"
        match = re.search(r'(?:R\$\s*)?(\d+(?:\.\d+)*),(\d{2})', text)
        if match:
            fraction = match.group(1).replace(".", "")
            cents = match.group(2)
            return float(f"{fraction}.{cents}")
            
        return 0.0
    except Exception as e:
        print(f"Erro ao limpar preço: {e}")
        return 0.0


async def scraper_mercadolivre_ofertas(url: str) -> int:
    """Scraper principal de ofertas do Mercado Livre."""
    print(f"Iniciando scraper ML Ofertas: {url}")
    
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                print(f"Erro ao acessar ofertas ML: {resp.status_code}")
                return 0
            
            soup = BeautifulSoup(resp.text, "lxml")
            # Seletores variam conforme o layout da página de ofertas
            items = soup.select(".promotion-item, .ui-search-result, .poly-card, .ui-recommendations-card")
            
            total_processados = 0
            
            for item in items[:24]:
                try:
                    title_el = item.select_one(".promotion-item__title, .ui-search-item__title, .poly-component__title, .ui-recommendations-card__title")
                    link_el = item.select_one(".promotion-item__link-container, a")
                    
                    if not title_el or not link_el:
                        continue
                        
                    title = title_el.get_text(strip=True)
                    href = link_el.get("href")
                    
                    if not href or "mercadolivre.com.br" not in href:
                        continue
                    
                    # Preço usando a nova lógica
                    price = limpar_preco(item)
                    
                    # Verificar preço antigo (para calcular desconto)
                    old_price = 0.0
                    old_price_container = item.select_one(".andes-money-amount--previous, .ui-search-price__part--metadata")
                    if old_price_container:
                        old_price = limpar_preco(old_price_container)
                    
                    # Imagem com suporte a lazy loading
                    img_el = item.select_one("img")
                    image_url = None
                    if img_el:
                        image_url = (
                            img_el.get("data-src") or 
                            img_el.get("data-srcset") or 
                            img_el.get("src")
                        )
                        if image_url and image_url.startswith("data:"): # Se ainda for base64/placeholder
                            image_url = img_el.get("data-src")
                    
                    # Verificar se já existe
                    existentes = await product_repository.listar_todos()
                    ja_existe = next((p for p in existentes if p.get("title") == title), None)
                    
                    if ja_existe:
                        pid = ja_existe["id"]
                        updates = {}
                        if float(ja_existe.get("price", 0)) != price:
                            updates["price"] = price
                            if old_price: updates["oldPrice"] = old_price
                            await price_history_repository.registrar(pid, price, old_price or None)
                        
                        if not ja_existe.get("imageUrl") and image_url:
                            updates["imageUrl"] = image_url
                            
                        if updates:
                            await product_repository.atualizar(pid, updates)
                            print(f"Atualizado: {title[:30]}...")
                    else:
                        # Se não pegou imagem no card, tenta nos detalhes
                        if not image_url or "placeholder" in image_url:
                            detalhes = await extrair_detalhes_ml(href)
                            if detalhes:
                                image_url = detalhes.get("imageUrl")
                        
                        await product_repository.criar({
                            "title": title,
                            "originalUrl": href,
                            "price": price,
                            "oldPrice": old_price if old_price > 0 else None,
                            "imageUrl": image_url,
                            "store": "mercadolivre",
                            "category": "Ofertas"
                        })
                        total_processados += 1
                        print(f"Novo produto: {title[:30]}...")
                        await asyncio.sleep(1)
                
                except Exception as e:
                    print(f"Erro ao processar item: {e}")
                    
            print(f"Scraper ML finalizado. {total_processados} novos produtos.")
            return total_processados
            
    except Exception as e:
        print(f"Erro fatal no scraper ML: {e}")
        return 0
