#!/bin/bash

# Script principal de deploy para produção

set -e

echo "🚀 Iniciando deploy da aplicação Bias Detector"
echo "🌐 Domínio: biasdetector.online"
echo "📍 Servidor: 103.199.184.185"
echo ""

# Verificar se está rodando como root (necessário para Docker)
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script precisa ser executado como root ou com sudo"
    echo "Execute: sudo ./scripts/deploy.sh"
    exit 1
fi

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Instalando..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl start docker
    systemctl enable docker
    echo "✅ Docker instalado com sucesso!"
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Instalando..."
    curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose instalado com sucesso!"
fi

# Função para verificar variáveis de ambiente
check_env() {
    echo "🔍 Verificando variáveis de ambiente..."
    
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "❌ OPENAI_API_KEY não está definida"
        echo "Execute: export OPENAI_API_KEY=sua_chave_aqui"
        exit 1
    fi
    
    echo "✅ Variáveis de ambiente verificadas!"
}

# Função para preparar ambiente
prepare_environment() {
    echo "📁 Preparando ambiente..."
    
    # Criar diretórios necessários
    mkdir -p ./certbot/{conf,www}
    mkdir -p ./nginx/logs
    mkdir -p ./scripts
    
    # Definir permissões
    chmod +x ./scripts/*.sh 2>/dev/null || true
    
    echo "✅ Ambiente preparado!"
}

# Função para fazer build das imagens
build_images() {
    echo "🔨 Fazendo build das imagens Docker..."
    
    # Parar containers existentes
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    
    # Remover imagens antigas
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    echo "✅ Build das imagens concluído!"
}

# Função para iniciar aplicação
start_application() {
    echo "🚀 Iniciando aplicação..."
    
    # Iniciar serviços
    docker-compose -f docker-compose.prod.yml up -d backend frontend nginx
    
    # Aguardar serviços iniciarem
    echo "⏳ Aguardando serviços iniciarem..."
    sleep 30
    
    # Verificar saúde dos serviços
    docker-compose -f docker-compose.prod.yml ps
    
    echo "✅ Aplicação iniciada!"
}

# Função para configurar SSL
setup_ssl() {
    echo "🔒 Configurando SSL..."
    
    # Executar script de SSL
    bash ./scripts/setup-ssl.sh
    
    echo "✅ SSL configurado!"
}

# Função para verificar deploy
verify_deployment() {
    echo "🔍 Verificando deployment..."
    
    # Verificar se os containers estão rodando
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        echo "✅ Containers estão rodando!"
    else
        echo "❌ Erro: containers não estão rodando"
        docker-compose -f docker-compose.prod.yml logs
        exit 1
    fi
    
    # Verificar conectividade HTTP (antes do SSL)
    if curl -f http://localhost:80 > /dev/null 2>&1; then
        echo "✅ Aplicação respondendo na porta 80!"
    else
        echo "⚠️  Aplicação não está respondendo na porta 80"
    fi
}

# Função principal
main() {
    echo "🌟 Deploy da aplicação Bias Detector"
    echo "======================================"
    
    check_env
    prepare_environment
    build_images
    start_application
    verify_deployment
    
    echo ""
    echo "🎉 Deploy básico concluído!"
    echo "📋 Próximos passos:"
    echo "1. Configure seu DNS para apontar biasdetector.online para 103.199.184.185"
    echo "2. Execute ./scripts/setup-ssl.sh para configurar SSL"
    echo "3. Acesse https://biasdetector.online"
    echo ""
    echo "📝 Comandos úteis:"  
    echo "- Ver logs: docker-compose -f docker-compose.prod.yml logs -f"
    echo "- Parar: docker-compose -f docker-compose.prod.yml down"
    echo "- Reiniciar: docker-compose -f docker-compose.prod.yml restart"
}

# Verificar argumentos
case "${1:-}" in
    --ssl-only)
        setup_ssl
        ;;
    --no-ssl)
        check_env
        prepare_environment
        build_images
        start_application
        verify_deployment
        echo "🎉 Deploy concluído sem SSL!"
        ;;
    *)
        main
        ;;
esac 