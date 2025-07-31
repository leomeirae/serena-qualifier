# =============================================================================
# SERENA SDR - DOCUMENTAÇÃO DE TESTES
# =============================================================================

## 📋 Visão Geral

Este diretório contém todos os testes para o sistema Serena SDR, incluindo:
- **Testes Unitários** (`tests/unit/`)
- **Testes de Integração** (`tests/integration/`)
- **Testes End-to-End** (`tests/e2e/`)

## 🎯 Cenários de Teste Implementados

### 1. Teste de Mensagem de Texto (`test_text_message_flow.py`)
- ✅ Webhook normal com resposta IA
- ✅ Lead não encontrado com fallback
- ✅ Payload inválido com erro 400
- ✅ Verificação de tempo de resposta (< 15s SLA)
- ✅ Logging de métricas no Supabase

### 2. Teste de Fatura OCR (`test_energy_bill_ocr_flow.py`)
- ✅ Fluxo completo: imagem → OCR → qualificação → planos
- ✅ Valor abaixo do threshold (R$200) - não qualificado
- ✅ Erro de classificação com fallback
- ✅ Imagem que não é fatura
- ✅ Precisão do OCR com dados específicos
- ✅ Tempo de processamento (< 30s SLA)

### 3. Teste de Follow-Up (`test_follow_up_flow.py`)
- ✅ Timeout disparado após 2 horas
- ✅ Cancelamento por resposta antecipada
- ✅ Múltiplos follow-ups com mensagens diferentes
- ✅ Logging e métricas de follow-up
- ✅ Tratamento de erro no follow-up
- ✅ Precisão de timing (exatamente 2 horas)

### 4. Teste de Fallback e Métricas (`test_fallback_and_metrics.py`)
- ✅ Timeout em MCP com mensagem de fallback
- ✅ Erro 500 em MCP com fallback
- ✅ Erro no WhatsApp MCP
- ✅ Logging de métricas de erro
- ✅ Mecanismo de retry
- ✅ Conteúdo apropriado de mensagens de fallback
- ✅ Agregação de métricas
- ✅ Padrão circuit breaker

## 📱 Número de WhatsApp para Testes

**Todos os testes estão configurados para usar o número:**
```
+5581997498268
```

Isso significa que durante os testes, você receberá as mensagens no seu WhatsApp para verificar o funcionamento real do sistema.

## 🚀 Como Executar os Testes

### Pré-requisitos
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais
```

### Executar Todos os Testes
```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=scripts --cov-report=html

# Executar com verbose
pytest -v
```

### Executar Testes Específicos
```bash
# Apenas testes E2E
pytest tests/e2e/ -v

# Apenas testes de mensagem de texto
pytest tests/e2e/test_text_message_flow.py -v

# Apenas testes de OCR
pytest tests/e2e/test_energy_bill_ocr_flow.py -v

# Apenas testes de follow-up
pytest tests/e2e/test_follow_up_flow.py -v

# Apenas testes de fallback
pytest tests/e2e/test_fallback_and_metrics.py -v
```

### Executar por Marcadores
```bash
# Testes de OCR
pytest -m ocr -v

# Testes de follow-up
pytest -m followup -v

# Testes de fallback
pytest -m fallback -v

# Testes de métricas
pytest -m metrics -v

# Testes relacionados aos MCPs
pytest -m mcp -v
```

### Executar Testes Lentos
```bash
# Testes que podem demorar mais
pytest -m slow -v
```

## 📊 Relatórios de Cobertura

Após executar os testes com cobertura:
```bash
pytest --cov=scripts --cov-report=html
```

Os relatórios estarão disponíveis em:
- **HTML**: `htmlcov/index.html`
- **XML**: `coverage.xml`

## 🔧 Configuração de Testes

### Fixtures Disponíveis
- `mock_supabase_mcp` - Mock do servidor MCP Supabase
- `mock_serena_mcp` - Mock do servidor MCP Serena
- `mock_whatsapp_mcp` - Mock do servidor MCP WhatsApp
- `mock_whatsapp_media` - Mock para download de mídia
- `mock_openai_vision` - Mock para OpenAI Vision API
- `mock_openai_chat` - Mock para OpenAI Chat API
- `sample_webhook_payload` - Payload de exemplo para webhook
- `sample_webhook_payload_with_image` - Payload com imagem
- `test_environment` - Configuração de ambiente de teste

### Helpers Disponíveis
- `assert_mcp_call()` - Verificar chamadas MCP
- `assert_supabase_log()` - Verificar logs no Supabase
- `create_test_lead()` - Criar lead de teste

## 🐛 Debugging

### Executar Teste Específico com Debug
```bash
# Executar um teste específico com mais informações
pytest tests/e2e/test_text_message_flow.py::TestTextMessageFlow::test_text_message_webhook_flow -v -s

# Executar com print statements
pytest tests/e2e/test_text_message_flow.py -v -s
```

### Verificar Logs
```bash
# Executar com logs detalhados
pytest --log-cli-level=DEBUG -v
```

## 📈 SLAs de Performance

Os testes validam os seguintes SLAs:
- **Resposta de texto**: < 15 segundos
- **Processamento de fatura**: < 30 segundos
- **Follow-up**: Exatamente 2 horas
- **Webhook response**: < 200ms

## 🔄 Fluxo de Teste Típico

1. **Setup**: Configurar mocks e fixtures
2. **Execute**: Simular webhook ou ação
3. **Verify**: Verificar chamadas MCP e logs
4. **Assert**: Validar resultados esperados

## 📝 Exemplo de Teste

```python
def test_example(self, sample_webhook_payload, mock_whatsapp_mcp):
    # 1. Simular webhook
    response = httpx.post("http://localhost:8001/webhook", 
                         json=sample_webhook_payload)
    
    # 2. Verificar resposta
    assert response.status_code == 200
    
    # 3. Verificar que mensagem foi enviada
    mock_whatsapp_mcp.assert_called()
    
    # 4. Verificar conteúdo da mensagem
    call_args = mock_whatsapp_mcp.call_args
    message = call_args[1]['json']['params']['message']
    assert "Silvia" in message
```

## 🚨 Troubleshooting

### Erro: "Module not found"
```bash
# Verificar se PYTHONPATH está correto
export PYTHONPATH="${PYTHONPATH}:/app/scripts:/app/scripts/sdr"
```

### Erro: "Connection refused"
```bash
# Verificar se os serviços estão rodando
docker-compose ps

# Reiniciar serviços se necessário
docker-compose restart
```

### Erro: "Timeout"
```bash
# Aumentar timeout para testes
pytest --timeout=60 -v
```

## 📞 Suporte

Para dúvidas sobre os testes, consulte:
- `conftest.py` - Configuração e fixtures
- `pytest.ini` - Configuração do pytest
- Documentação do pytest: https://docs.pytest.org/ 