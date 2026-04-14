# Estágio 1: Builder
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# Estágio 2: Nginx server
FROM nginx:alpine

# Copiar build gerado
COPY --from=builder /app/dist /usr/share/nginx/html

# Copiar configuração customizada
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
