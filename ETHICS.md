# AfiliaML — Política de Ética, Privacidade e Transparência

## 1. Visão Geral

O AfiliaML é uma plataforma de automação para afiliados do Mercado Livre. Este documento descreve as práticas éticas adotadas no projeto, em conformidade com a LGPD (Lei Geral de Proteção de Dados — Lei nº 13.709/2018), os Termos de Serviço do Mercado Livre, e boas práticas de engenharia de software.

---

## 2. Dados Coletados

### 2.1 Dados de Navegação (ClickEvents)
- **O que coletamos:** Hash SHA-256 do endereço IP (nunca o IP real), User-Agent do navegador, canal de origem (WhatsApp, Instagram, etc.), timestamp do clique.
- **Finalidade:** Análise de performance das campanhas de afiliados — identificar quais canais e produtos geram mais engajamento.
- **Anonimização:** O IP é imediatamente transformado em hash irreversível (SHA-256 com salt) antes de ser persistido. O IP original **nunca é armazenado**.

### 2.2 Dados de Compartilhamento (ShareEvents)
- **O que coletamos:** ID do produto, canal de compartilhamento, mensagem gerada, timestamp.
- **Finalidade:** Métricas de taxa de conversão (compartilhamentos vs. cliques).

### 2.3 Dados de Produtos
- **O que coletamos:** Informações públicas de produtos do Mercado Livre (título, preço, imagem, URL, avaliação, quantidade vendida).
- **Fonte:** Web scraping de páginas públicas e/ou API oficial do Mercado Livre.
- **Finalidade:** Exibir catálogo, gerar links de afiliado, analisar tendências de preço.

---

## 3. Tempo de Retenção

| Tipo de Dado         | Retenção Recomendada | Justificativa                         |
| -------------------- | -------------------- | ------------------------------------- |
| ClickEvents          | 90 dias              | Análise de campanhas recentes         |
| ShareEvents          | 90 dias              | Métricas de conversão                 |
| PriceHistory         | 180 dias             | Análise de tendência de preços        |
| Dados de Produtos    | Enquanto ativo       | Catálogo operacional                  |
| Tokens OAuth (Redis) | Até expiração        | Autenticação com API do ML            |

> **Nota:** A implementação de limpeza automática (TTL/cron) para dados expirados é recomendada e deve ser implementada em versões futuras.

---

## 4. Transparência sobre Links de Afiliado

Todas as mensagens de compartilhamento geradas pelo AfiliaML incluem automaticamente um **disclaimer de afiliado** ao final:

> *Link de afiliado — posso ganhar comissão sem custo adicional para você.*

Este disclaimer:
- É **obrigatório** e não pode ser removido pelo usuário.
- É **configurável** via variável de ambiente `AFFILIATE_DISCLAIMER`.
- Segue as diretrizes do Código de Defesa do Consumidor sobre transparência em relações comerciais.

---

## 5. Conformidade com os Termos de Serviço do Mercado Livre

### 5.1 Uso da API Oficial
- O AfiliaML utiliza preferencialmente a **API oficial do Mercado Livre** para obtenção de dados estruturados.
- O web scraping é utilizado como **fallback** apenas para dados públicos de ofertas.
- As credenciais OAuth são armazenadas de forma segura no Redis e renovadas automaticamente.

### 5.2 Rate Limiting
- Todas as chamadas à API do ML respeitam um limite de **1 requisição a cada 300ms** (≈200 req/min), abaixo do limite permitido pela API.

### 5.3 Programa de Afiliados
- Os links gerados seguem o modelo oficial do Programa de Afiliados do Mercado Livre.
- As comissões são rastreadas via parâmetros oficiais (`matt_tool`, `matt_word`).

---

## 6. Segurança

- **Hashing de IPs:** SHA-256 com salt configurável (variável `IP_HASH_SALT`).
- **Tokens OAuth:** Armazenados em Redis, não em arquivos ou código-fonte.
- **Variáveis sensíveis:** Mantidas em `.env` (excluído do Git via `.gitignore`).
- **Sem dados pessoais identificáveis:** O sistema não coleta nomes, e-mails, CPFs ou qualquer dado pessoal dos usuários finais.

---

## 7. Direitos dos Usuários (LGPD)

Embora o AfiliaML não colete dados pessoais identificáveis dos usuários finais (compradores), o operador da plataforma (afiliado) deve:
- Informar aos seus seguidores que utiliza links de afiliado (garantido pelo disclaimer automático).
- Não utilizar os dados analíticos para identificar indivíduos.
- Manter este documento atualizado conforme novas funcionalidades forem implementadas.

---

## 8. Contato

Para questões sobre privacidade e ética neste projeto:
- Abra uma issue no repositório do projeto.
- Entre em contato com o mantenedor principal.

---

*Última atualização: Abril 2026*
