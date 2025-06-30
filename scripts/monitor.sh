#!/bin/bash

# Script de monitoramento da aplicação

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Monitoramento da aplicação Bias Detector"
echo "=========================================="

# Função para verificar status dos containers
check_containers() {
    echo -e "\n📦 Status dos Containers:"
    echo "------------------------"
    
    containers=("bias-detector-nginx" "bias-detector-backend" "bias-detector-frontend")
    
    for container in "${containers[@]}"; do
        if docker ps | grep -q "$container"; then
            echo -e "${GREEN}✅ $container: Running${NC}"
        else
            echo -e "${RED}❌ $container: Not running${NC}"
        fi
    done
}

# Função para verificar saúde dos serviços
check_health() {
    echo -e "\n🏥 Verificação de Saúde:"
    echo "----------------------"
    
    # Verificar frontend
    if curl -f -s http://localhost:80 > /dev/null; then
        echo -e "${GREEN}✅ Frontend: Healthy${NC}"
    else
        echo -e "${RED}❌ Frontend: Unhealthy${NC}"
    fi
    
    # Verificar HTTPS (se SSL estiver configurado)
    if curl -f -s -k https://localhost:443 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ HTTPS: Healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  HTTPS: Not configured or unhealthy${NC}"
    fi
    
    # Verificar domínio externo
    if curl -f -s https://biasdetector.online > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Domain: Accessible${NC}"
    else
        echo -e "${YELLOW}⚠️  Domain: Not accessible or SSL not configured${NC}"
    fi
}

# Função para mostrar uso de recursos
check_resources() {
    echo -e "\n💻 Uso de Recursos:"
    echo "------------------"
    
    # CPU e memória total do sistema
    echo "Sistema:"
    free -h | head -2
    echo ""
    
    # Uso por container
    echo "Containers:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null || echo "Nenhum container rodando"
}

# Função para mostrar logs recentes
show_recent_logs() {
    echo -e "\n📋 Logs Recentes:"
    echo "----------------"
    
    # Logs do nginx
    if docker ps | grep -q "bias-detector-nginx"; then
        echo -e "\n${YELLOW}Nginx (últimas 5 linhas):${NC}"
        docker logs --tail 5 bias-detector-nginx 2>/dev/null || echo "Sem logs"
    fi
    
    # Logs do backend
    if docker ps | grep -q "bias-detector-backend"; then
        echo -e "\n${YELLOW}Backend (últimas 5 linhas):${NC}"
        docker logs --tail 5 bias-detector-backend 2>/dev/null || echo "Sem logs"
    fi
    
    # Logs do frontend
    if docker ps | grep -q "bias-detector-frontend"; then
        echo -e "\n${YELLOW}Frontend (últimas 5 linhas):${NC}"
        docker logs --tail 5 bias-detector-frontend 2>/dev/null || echo "Sem logs"
    fi
}

# Função para verificar certificados SSL
check_ssl() {
    echo -e "\n🔒 Status SSL:"
    echo "-------------"
    
    if [ -f "./certbot/conf/live/biasdetector.online/fullchain.pem" ]; then
        # Verificar validade do certificado
        expiry=$(openssl x509 -enddate -noout -in ./certbot/conf/live/biasdetector.online/fullchain.pem | cut -d= -f2)
        echo -e "${GREEN}✅ Certificado SSL: Instalado${NC}"
        echo "   Expira em: $expiry"
        
        # Verificar se está próximo do vencimento (30 dias)
        if openssl x509 -checkend 2592000 -noout -in ./certbot/conf/live/biasdetector.online/fullchain.pem; then
            echo -e "${GREEN}   Status: Válido (>30 dias)${NC}"
        else
            echo -e "${YELLOW}⚠️  Status: Expira em menos de 30 dias!${NC}"
        fi
    else
        echo -e "${RED}❌ Certificado SSL: Não encontrado${NC}"
    fi
}

# Função para verificar conectividade de rede
check_network() {
    echo -e "\n🌐 Conectividade:"
    echo "----------------"
    
    # Verificar se as portas estão abertas
    if netstat -tuln | grep -q ":80 "; then
        echo -e "${GREEN}✅ Porta 80: Aberta${NC}"
    else
        echo -e "${RED}❌ Porta 80: Fechada${NC}"
    fi
    
    if netstat -tuln | grep -q ":443 "; then
        echo -e "${GREEN}✅ Porta 443: Aberta${NC}"
    else
        echo -e "${YELLOW}⚠️  Porta 443: Fechada${NC}"
    fi
    
    # Verificar resolução DNS
    if dig +short biasdetector.online | grep -q "147.93.68.216"; then
        echo -e "${GREEN}✅ DNS: Configurado corretamente${NC}"
    else
        echo -e "${YELLOW}⚠️  DNS: Não aponta para 147.93.68.216${NC}"
    fi
}

# Função principal
main() {
    check_containers
    check_health
    check_resources
    check_ssl
    check_network
    
    if [ "${1:-}" = "--logs" ]; then
        show_recent_logs
    fi
    
    echo -e "\n🎯 Comandos úteis:"
    echo "- Ver logs completos: docker-compose -f docker-compose.prod.yml logs -f"
    echo "- Reiniciar serviços: docker-compose -f docker-compose.prod.yml restart"
    echo "- Atualizar SSL: ./scripts/renew-ssl.sh"
    echo "- Deploy completo: sudo ./scripts/deploy.sh"
}

# Verificar argumentos
case "${1:-}" in
    --watch)
        while true; do
            clear
            main
            echo -e "\n⏰ Atualizando em 30s... (Ctrl+C para sair)"
            sleep 30
        done
        ;;
    *)
        main "$@"
        ;;
esac 