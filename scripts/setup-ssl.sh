#!/bin/bash

# Script para configurar SSL com Let's Encrypt

set -e

echo "🚀 Configurando SSL para biasdetector.online"

# Criar diretórios necessários
mkdir -p ./certbot/conf
mkdir -p ./certbot/www
mkdir -p ./nginx/logs

# Função para verificar se o domínio aponta para o servidor
check_domain() {
    echo "🔍 Verificando se o domínio aponta para este servidor..."
    DOMAIN_IP=$(dig +short biasdetector.online)
    SERVER_IP="103.199.184.185"
    
    if [ "$DOMAIN_IP" = "$SERVER_IP" ]; then
        echo "✅ Domínio configurado corretamente!"
        return 0
    else
        echo "❌ Domínio não aponta para o servidor. IP encontrado: $DOMAIN_IP, esperado: $SERVER_IP"
        echo "Configure seu DNS antes de continuar."
        exit 1
    fi
}

# Função para obter certificado SSL
get_certificate() {
    echo "📜 Obtendo certificado SSL..."
    
    # Primeiro, iniciar nginx temporário para validação
    docker-compose -f docker-compose.prod.yml up -d nginx
    
    # Aguardar nginx inicializar
    sleep 10
    
    # Obter certificado
    docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
        --webroot \
        --webroot-path /var/www/certbot \
        --email seu-email@exemplo.com \
        --agree-tos \
        --no-eff-email \
        --force-renewal \
        -d biasdetector.online \
        -d www.biasdetector.online
    
    echo "✅ Certificado SSL obtido com sucesso!"
}

# Configurar renovação automática
setup_renewal() {
    echo "🔄 Configurando renovação automática..."
    
    # Criar script de renovação
    cat > ./scripts/renew-ssl.sh << 'EOF'
#!/bin/bash
echo "Renovando certificado SSL..."
docker-compose -f docker-compose.prod.yml run --rm certbot renew
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
echo "Certificado renovado!"
EOF
    
    chmod +x ./scripts/renew-ssl.sh
    
    echo "✅ Script de renovação criado em ./scripts/renew-ssl.sh"
    echo "📅 Adicione ao crontab: 0 12 * * * /caminho/para/seu/projeto/scripts/renew-ssl.sh"
}

# Executar configuração
main() {
    echo "🌟 Iniciando configuração SSL para biasdetector.online"
    echo "📍 Servidor: 103.199.184.185"
    echo ""
    
    check_domain
    get_certificate
    setup_renewal
    
    echo ""
    echo "🎉 Configuração SSL concluída!"
    echo "🚀 Execute: docker-compose -f docker-compose.prod.yml up -d"
    echo "🌐 Acesse: https://biasdetector.online"
}

# Verificar se está rodando no servidor correto
if [ "$1" = "--skip-checks" ]; then
    echo "⚠️  Pulando verificações de domínio..."
    get_certificate
    setup_renewal
else
    main
fi 