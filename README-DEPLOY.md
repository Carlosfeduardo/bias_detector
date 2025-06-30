# 🚀 Deploy da Aplicação Bias Detector

Guia completo para fazer deploy da aplicação com domínio **biasdetector.online** no servidor **103.199.184.185**.

## 📋 Pré-requisitos

### 1. Configuração do DNS

**PRIMEIRO PASSO OBRIGATÓRIO**: Configure seu provedor de DNS para apontar o domínio para o servidor:

```
Tipo: A
Nome: biasdetector.online
Valor: 103.199.184.185

Tipo: A  
Nome: www.biasdetector.online
Valor: 103.199.184.185
```

⚠️ **Aguarde a propagação DNS** (pode levar até 24h, mas geralmente é rápido).

### 2. Configuração da OpenAI API Key

Antes de fazer o deploy, configure sua chave da OpenAI:

```bash
export OPENAI_API_KEY="sua_chave_openai_aqui"
```

### 3. Configuração do Email para SSL

Edite o arquivo `.env.production` e configure o email para o certificado SSL:

```bash
SSL_EMAIL=seu-email@exemplo.com
```

## 🔧 Arquivos Criados

A configuração adicionou os seguintes arquivos:

```
bias-detector/
├── nginx/
│   └── nginx.conf                    # Configuração principal do Nginx
├── scripts/
│   ├── deploy.sh                     # Script principal de deploy
│   ├── setup-ssl.sh                  # Configuração automática de SSL
│   ├── monitor.sh                    # Monitoramento da aplicação
│   └── renew-ssl.sh                  # Renovação automática de SSL
├── frontend/
│   ├── Dockerfile.prod               # Dockerfile otimizado p/ produção
│   └── nginx-frontend.conf           # Config do Nginx do frontend
├── docker-compose.prod.yml           # Docker Compose para produção
└── .env.production                   # Variáveis de ambiente
```

## 🚀 Deploy Passo a Passo

### 1. Conectar ao Servidor

```bash
ssh root@103.199.184.185
```

### 2. Clonar/Enviar Código

Se ainda não tem o código no servidor:

```bash
# Opção 1: Git
git clone seu-repositorio.git
cd nuvia_case/bias-detector

# Opção 2: SCP (do seu computador local)
scp -r /caminho/local/nuvia_case root@103.199.184.185:/root/
```

### 3. Configurar Variáveis de Ambiente

```bash
cd /root/nuvia_case/bias-detector

# Configurar OpenAI API Key
export OPENAI_API_KEY="sua_chave_openai_aqui"

# Editar email para SSL
nano .env.production
# Altere: SSL_EMAIL=seu-email@exemplo.com
```

### 4. Executar Deploy

```bash
# Tornar scripts executáveis
chmod +x scripts/*.sh

# Deploy completo (instala Docker se necessário)
sudo ./scripts/deploy.sh
```

### 5. Configurar SSL (após DNS propagado)

```bash
# Verificar se DNS está propagando
dig +short biasdetector.online

# Se retornar 103.199.184.185, execute:
./scripts/setup-ssl.sh
```

### 6. Reiniciar com SSL

```bash
# Parar containers
docker-compose -f docker-compose.prod.yml down

# Reiniciar com SSL
docker-compose -f docker-compose.prod.yml up -d
```

## 🔍 Verificação e Monitoramento

### Verificar Status

```bash
# Monitoramento completo
./scripts/monitor.sh

# Monitoramento contínuo (atualiza a cada 30s)
./scripts/monitor.sh --watch

# Ver logs em tempo real
docker-compose -f docker-compose.prod.yml logs -f
```

### Verificar Acessibilidade

```bash
# Teste local
curl -I http://localhost:80
curl -I https://localhost:443

# Teste domínio
curl -I https://biasdetector.online
```

## 🌐 URLs de Acesso

Após o deploy completo:

- **Frontend**: https://biasdetector.online
- **API**: https://biasdetector.online/api
- **Health Check**: https://biasdetector.online/api/health

## 🔒 Configuração SSL

### Certificado Let's Encrypt

O certificado SSL é configurado automaticamente com Let's Encrypt:

- **Provedor**: Let's Encrypt (gratuito)
- **Renovação**: Automática (script em `scripts/renew-ssl.sh`)
- **Validade**: 90 dias (renovação automática aos 30 dias)

### Configuração do Cron para Renovação

```bash
# Adicionar ao crontab para renovação automática
crontab -e

# Adicionar linha:
0 12 * * * /root/nuvia_case/bias-detector/scripts/renew-ssl.sh
```

## 🐳 Gerenciamento Docker

### Comandos Úteis

```bash
# Ver status dos containers
docker-compose -f docker-compose.prod.yml ps

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f [service]

# Reiniciar serviços
docker-compose -f docker-compose.prod.yml restart [service]

# Parar tudo
docker-compose -f docker-compose.prod.yml down

# Iniciar tudo
docker-compose -f docker-compose.prod.yml up -d

# Rebuild e restart
docker-compose -f docker-compose.prod.yml up -d --build
```

### Containers Criados

- **bias-detector-nginx**: Reverse proxy e SSL termination
- **bias-detector-frontend**: Interface React
- **bias-detector-backend**: API FastAPI
- **bias-detector-certbot**: Gerenciamento SSL

## 🔧 Troubleshooting

### DNS não está propagando

```bash
# Verificar propagação DNS
dig +short biasdetector.online
nslookup biasdetector.online

# Se não retornar 103.199.184.185, aguarde ou contate seu provedor DNS
```

### SSL não está funcionando

```bash
# Verificar se o domínio está acessível via HTTP
curl -I http://biasdetector.online

# Tentar reconfigurar SSL
./scripts/setup-ssl.sh --skip-checks

# Ver logs do certbot
docker-compose -f docker-compose.prod.yml logs certbot
```

### Containers não estão iniciando

```bash
# Ver logs detalhados
docker-compose -f docker-compose.prod.yml logs

# Verificar recursos do sistema
free -h
df -h

# Rebuild completo
docker-compose -f docker-compose.prod.yml down
docker system prune -a
sudo ./scripts/deploy.sh --no-ssl
```

### Aplicação não responde

```bash
# Verificar portas
netstat -tulpn | grep ':80\|:443'

# Verificar firewall
ufw status
# Se necessário: ufw allow 80 && ufw allow 443

# Reiniciar nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

## 📊 Monitoramento Contínuo

### Logs Importantes

```bash
# Logs do Nginx (acesso e erro)
docker-compose -f docker-compose.prod.yml exec nginx tail -f /var/log/nginx/access.log
docker-compose -f docker-compose.prod.yml exec nginx tail -f /var/log/nginx/error.log

# Logs da aplicação
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### Métricas de Performance

```bash
# Uso de recursos
docker stats

# Espaço em disco
df -h

# Monitoramento completo
./scripts/monitor.sh --logs
```

## 🔄 Atualizações

### Deploy de Nova Versão

```bash
# Parar aplicação
docker-compose -f docker-compose.prod.yml down

# Atualizar código
git pull  # ou scp novo código

# Rebuild e iniciar
docker-compose -f docker-compose.prod.yml up -d --build

# Verificar se está funcionando
./scripts/monitor.sh
```

### Backup do Certificado SSL

```bash
# Fazer backup dos certificados
tar -czf ssl-backup-$(date +%Y%m%d).tar.gz certbot/

# Restaurar se necessário
tar -xzf ssl-backup-YYYYMMDD.tar.gz
```

## 📞 Suporte

### Comandos de Diagnóstico

```bash
# Status completo do sistema
./scripts/monitor.sh --watch

# Verificar configuração
docker-compose -f docker-compose.prod.yml config

# Testar conectividade
curl -vvv https://biasdetector.online/api/health
```

### Logs para Análise

Se precisar de suporte, colete estes logs:

```bash
# Logs dos containers
docker-compose -f docker-compose.prod.yml logs > app-logs.txt

# Status do sistema
./scripts/monitor.sh > system-status.txt

# Configuração do nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -T > nginx-config.txt
```

## ✅ Checklist Final

- [ ] DNS configurado e propagado
- [ ] OpenAI API Key configurada
- [ ] Deploy executado com sucesso
- [ ] SSL configurado e funcionando
- [ ] Aplicação acessível via https://biasdetector.online
- [ ] Monitoramento configurado
- [ ] Renovação automática de SSL agendada

## 🎉 Conclusão

Após seguir todos os passos, sua aplicação estará rodando em:

**🌐 https://biasdetector.online**

Com SSL automático, monitoramento e renovação de certificados configurados! 