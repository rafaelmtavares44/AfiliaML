# ============================================
# AfiliaML — Scraper de Vitrine Social ML
# ============================================

import httpx
from bs4 import BeautifulSoup
import json
import re
from app.repositories.product_repo import product_repository

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

async def sincronizar_vitrine():
    profile_url = "https://www.mercadolivre.com.br/social/rafaelmachadotavares/lists"
    print(f"🔄 Sincronizando Vitrine Social: {profile_url}")
    
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(profile_url)
            if resp.status_code != 200:
                print(f"❌ Erro vitrine: {resp.status_code}")
                return 0
            
            soup = BeautifulSoup(resp.text, "lxml")
            
            # 1. Tentar extrair do JSON injetado (Tática 1 do TS)
            items = []
            script_tag = soup.find("script", id="__NORDIC_RENDERING_CTX__")
            if script_tag:
                try:
                    content = script_tag.string
                    # Limpeza bruta do script
                    json_str = re.sub(r'^_n\.ctx\.r=', '', content)
                    json_str = re.sub(r';[^;]*$', '', json_str)
                    data = json.loads(json_str)
                    
                    components = data.get("appProps", {}).get("pageProps", {}).get("data", {}).get("components", [])
                    
                    def walk(nodes):
                        for n in nodes:
                            if n.get("recommendation_data", {}).get("polycards"):
                                cards = n["recommendation_data"]["polycards"]
                                for c in cards:
                                    meta = c.get("metadata", {})
                                    title = next((cmp.get("title", {}).get("text") for cmp in c.get("components", []) if cmp.get("type") == "title"), "")
                                    price = next((cmp.get("price", {}).get("current_price", {}).get("value") for cmp in c.get("components", []) if cmp.get("type") == "price"), 0)
                                    pic_id = c.get("pictures", {}).get("pictures", [{}])[0].get("id")
                                    
                                    if title and meta.get("url"):
                                        url = meta["url"]
                                        if not url.startswith("http"): url = "https://" + url
                                        if meta.get("url_params"): url += meta["url_params"]
                                        
                                        items.append({
                                            "title": title,
                                            "href": url,
                                            "price": price,
                                            "image": f"https://http2.mlstatic.com/D_NQ_NP_{pic_id}-O.webp" if pic_id else None
                                        })
                            if n.get("tabs"): walk(n["tabs"])
                            if n.get("components"): walk(n["components"])
                    
                    walk(components)
                except Exception as e:
                    print(f"Erro ao parsear JSON vitrine: {e}")

            # 2. Tática 2: Fallback DOM
            if not items:
                cards = soup.select(".poly-card")
                for card in cards:
                    title_el = card.select_one(".poly-component__title")
                    if title_el:
                        title = title_el.get_text(strip=True)
                        href = title_el.get("href")
                        img_el = card.select_one(".poly-component__picture")
                        img = img_el.get("src") or img_el.get("data-src") if img_el else None
                        
                        items.append({
                            "title": title,
                            "href": href,
                            "image": img,
                            "price": 0 # Preço extrair via regex é complexo no DOM, no JSON é melhor
                        })

            total = 0
            for item in items:
                await sincronizar_item_vitrine(item)
                total += 1
                
            return total

    except Exception as e:
        print(f"❌ Erro fatal vitrine: {e}")
        return 0

async def sincronizar_item_vitrine(item):
    try:
        title = item["title"]
        url = item["href"]
        
        # Buscar match por similaridade de título (Prio 3 palavras chave)
        produtos = await product_repository.listar_todos()
        keywords = [w.lower() for w in re.findall(r'\w{4,}', title)]
        
        match = None
        for p in produtos:
            p_title = p.get("title", "").lower()
            matches = sum(1 for k in keywords if k in p_title)
            if matches >= 3:
                match = p
                break
        
        if match:
            # Vincula link de afiliado ao produto existente
            await product_repository.atualizar(match["id"], {
                "affiliateUrl": url,
                "status": "vinculado_vitrine"
            })
            print(f"   🔗 Vinculado: {title[:20]}...")
        elif item.get("image"):
            # Cria novo se tiver imagem
            await product_repository.criar({
                "title": title,
                "originalUrl": url,
                "affiliateUrl": url,
                "imageUrl": item["image"],
                "price": item.get("price", 0),
                "store": "mercadolivre",
                "category": "Vitrine",
                "status": "vinculado_vitrine"
            })
            print(f"   ✨ Novo (Vitrine): {title[:20]}...")
            
    except Exception as e:
        print(f"Erro item vitrine: {e}")
