#!/bin/bash

echo "🚀 INICIANDO AMBIENTE DE TESTE REAL - SERENA QUALIFIER"
echo "=================================================="

# Parar ambiente atual
echo "🛑 Parando ambiente atual..."
docker-compose down -v

# Aguardar um pouco
sleep 3

# Iniciar ambiente mínimo
echo "🔧 Iniciando ambiente mínimo (apenas plugins essenciais)..."
docker-compose -f docker-compose-minimal.yml up -d

echo "⏳ Aguardando serviços iniciarem..."
sleep 30

# Verificar status
echo "📊 Verificando status dos serviços..."

echo "🔍 WhatsApp Service:"
curl -s http://localhost:8000/health | jq .

echo -e "\n🔍 Kestra (pode demorar mais um pouco):"
curl -s http://localhost:8081/api/v1/flows | head -c 100

echo -e "\n\n✅ AMBIENTE PRONTO PARA TESTE!"
echo "🌐 Kestra UI: http://localhost:8081/ui"
echo "🤖 WhatsApp Service: http://localhost:8000"

echo -e "\n📋 PRÓXIMOS PASSOS:"
echo "1. Acessar Kestra UI em http://localhost:8081/ui"
echo "2. Importar workflows"
echo "3. Configurar webhook do WhatsApp"
echo "4. Iniciar teste real!" 