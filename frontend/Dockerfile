# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copia package.json
COPY package.json ./

# Instala dependências
RUN npm install

# Copia código fonte
COPY . .

# Define variáveis de ambiente para build
ENV REACT_APP_API_URL=http://localhost:8000

# Build da aplicação
RUN npm run build

# Production stage
FROM nginx:alpine

# Copia arquivos build
COPY --from=build /app/build /usr/share/nginx/html

# Copia configuração customizada do nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Expõe porta
EXPOSE 80

# Comando padrão
CMD ["nginx", "-g", "daemon off;"] 