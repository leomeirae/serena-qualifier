#!/bin/bash

echo "🔧 REINICIANDO KESTRA COM CONFIGURAÇÃO OTIMIZADA"
echo "=============================================="

# Parar apenas o Kestra (mantendo outros serviços)
echo "🛑 Parando Kestra atual..."
docker stop kestra
docker rm kestra

# Aguardar um pouco
sleep 5

# Reiniciar apenas o Kestra otimizado
echo "🚀 Iniciando Kestra otimizado (apenas plugins essenciais)..."
docker-compose up -d kestra

echo "⏳ Aguardando Kestra inicializar (pode demorar 2-3 minutos)..."

# Loop para verificar quando Kestra estiver pronto
attempt=1
max_attempts=20

while [ $attempt -le $max_attempts ]; do
    echo "Tentativa $attempt/$max_attempts - Verificando Kestra..."
    
    if curl -s http://localhost:8080/api/v1/flows > /dev/null 2>&1; then
        echo "✅ Kestra pronto!"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        echo "❌ Kestra não inicializou após $max_attempts tentativas"
        echo "Verificando logs..."
        docker logs kestra --tail 20
        exit 1
    fi
    
    sleep 15
    attempt=$((attempt + 1))
done

# Verificar status final
echo -e "\n📊 Status dos serviços:"
echo "🔍 WhatsApp Service:"
curl -s http://localhost:8000/health | jq . 2>/dev/null || echo "WhatsApp Service não disponível"

echo -e "\n🔍 Kestra:"
curl -s http://localhost:8080/api/v1/flows | head -c 100 2>/dev/null || echo "Kestra não disponível"

echo -e "\n\n✅ AMBIENTE PRONTO PARA TESTE REAL!"
echo "🌐 Kestra UI: http://localhost:8080/ui"
echo "🤖 WhatsApp Service: http://localhost:8000"

echo -e "\n📋 PRÓXIMOS PASSOS PARA TESTE REAL:"
echo "1. Acessar Kestra UI em http://localhost:8080/ui"
echo "2. Importar workflow 'ai-conversation-activation'"
echo "3. Configurar webhook do WhatsApp para seu número"
echo "4. Mandar mensagem no WhatsApp e interagir com a IA!" 