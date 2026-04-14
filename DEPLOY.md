# Deploy do Projeto AfiliaML (Fase 3 Final)

Este guia cobre a containerização completa e os passos necessários para colocar o AfiliaML no ar. Toda a arquiteura foi desenhada para subir com um único comando usando Docker.

---

## 🛠️ Pré-requisitos
- [Docker](https://docs.docker.com/get-docker/) instalado
- [Docker Compose](https://docs.docker.com/compose/install/) instalado

---

## 🚀 Rodando Localmente com Docker

1. **Configuração Inicial**
   Acesse a pasta `backend` e preencha as variáveis de produção caso queira conectar o app na API oficial do Mercado Livre (no arquivo `.env.production`).

2. **Subindo a Aplicação**
   No terminal, ainda dentro da pasta `backend`, execute o comando:
   ```bash
   docker-compose up --build -d
   ```
   > Este comando baixa as imagens (Node, Postgres, Redis, Nginx), compila o backend e o frontend, e sobe todos os serviços conectados em uma rede interna.

3. **Rodando as Migrations (Primeira Vez)**
   Com os containers no ar, precisamos criar as tabelas no PostgreSQL que acabou de nascer limpo. Execute a migration _por dentro do container_ do backend:
   ```bash
   docker exec -it afiliaml-backend npx prisma migrate deploy
   ```

Tudo pronto!
- **Frontend (Painel)**: [http://localhost](http://localhost) (Porta 80 padrão)
- **Backend (API)**: [http://localhost:3333](http://localhost:3333)
- **Monitoramento Redis**: [http://localhost:8081](http://localhost:8081)

---

## 🔄 Atualizando a Aplicação

Se você alterou o código (seja frontend ou backend) e deseja atualizar o ambiente Docker _sem_ derrubar os bancos de dados:

```bash
# Atualiza apenas o backend
docker-compose up --build -d --no-deps backend

# Atualiza apenas o frontend
docker-compose up --build -d --no-deps frontend
```

---

## ☁️ Deploy na Nuvem (Railway / Render / AWS)

Como o AfiliaML usa Node, Postgres e Redis, a plataforma **Railway** é altamente recomendada pelas facilidades nativas.

### Passo a Passo no Railway
1. Crie uma conta no [Railway.app](https://railway.app/).
2. Clique em **New Project** -> **Provision PostgreSQL**.
3. Clique em **New Project** -> **Provision Redis**.
4. Conecte seu repositório do GitHub (ou use a CLI do Railway).
5. Nos _Settings_ do serviço Backend, preencha as `Environment Variables` usando os links internos mágicos do Railway (`DATABASE_URL` e `REDIS_URL`).
6. Configure a porta `3333` no backend, e a porta `80` no frontend (se separado) ou use Vercel para o frontend apontando as chamadas para o domínio gerado no backend.

> ⚠️ Atenção em Produção: Use HTTPS para garantir a segurança da API e altere a váriável `IP_HASH_SALT` para não comprometer a anonimização dos logs de clique das campanhas.
