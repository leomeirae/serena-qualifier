# Testes da API Serena

Este diretório contém testes automatizados para validar a integração com a API Serena.

## 🧪 Executar Testes

### Todos os testes:
```bash
pytest
```

### Com output detalhado:
```bash
pytest -v -s
```

### Apenas testes específicos:
```bash
pytest tests/test_serena_api.py::TestPlans -v
```

### Testes de timeout/lembrete:
```bash
pytest tests/test_timeout_functionality.py -v
pytest tests/test_waitforwebhook_behavior.py -v
```

### Testes de funcionalidade RAG:
```bash
pytest tests/test_rag_functionality.py -v
```

### Testes unitários (rápidos):
```bash
pytest tests/test_timeout_functionality.py -m "not integration and not slow" -v
```

### Gerar relatório de cobertura:
```bash
pytest --cov=scripts --cov-report=html
```

## 📋 Estrutura dos Testes

### `TestOperationAreas`
- Testa consulta de áreas de operação
- Valida estrutura de dados retornados
- Testa cenários com cidades existentes e inexistentes

### `TestPlans`
- Testa consulta de planos de energia
- Valida planos para distribuidoras qualificadas vs não qualificadas
- Testa diferentes métodos de consulta (por cidade/estado, por ID da distribuidora)

### `TestConvenienceFunctions`
- Testa funções de conveniência (`get_plans_by_city`, `check_city_coverage`)
- Valida formatação de dados
- Testa inferência automática de estados

### `TestDataQuality`
- Valida qualidade dos dados retornados
- Testa ranges válidos (descontos, fidelidade)
- Valida formatos (UUIDs, nomes não vazios)

### `TestErrorHandling`
- Testa tratamento de erros
- Valida configuração de credenciais
- Testa comportamento com inputs inválidos

### `TestTimeoutFunctionality` (NOVO)
- Testa funcionalidade de timeout/lembrete do workflow ai-conversation.yml
- Valida configuração de WaitForWebhook (2 horas)
- Testa envio automático de lembrete após timeout
- Testa processamento de resposta antes do timeout
- Valida analytics e estrutura de dados

### `TestWaitForWebhookBehavior` (NOVO)
- Testa comportamento específico do WaitForWebhook
- Valida gerenciamento de chaves de webhook
- Testa cenários de múltiplas respostas
- Valida tratamento de erros durante timeout
- Testa analytics de timeout vs resposta

### `TestRAGFunctionality` (NOVO)
- Testa funcionalidade RAG (Retrieval-Augmented Generation)
- Valida schema de input da RAGTool
- Testa componentes isolados (text splitting, similarity filtering)
- Valida operações de arquivo (carregamento knowledge base)
- Testa tratamento de erros (diretórios inexistentes, arquivos vazios)
- Valida lógica de geração de respostas com threshold de relevância

## 🔧 Fixtures

- `api_client`: Instância da SerenaAPI para reutilização
- `sp_areas`: Áreas de operação de São Paulo (reutilizada entre testes)
- `bh_areas`: Áreas de operação de Belo Horizonte
- `bh_plans`: Planos de Belo Horizonte (cidade com planos disponíveis)

## ✅ Critérios de Sucesso

Os testes validam:

1. **Conectividade**: API responde corretamente
2. **Estrutura de Dados**: Campos obrigatórios presentes
3. **Tipos de Dados**: Valores no formato correto
4. **Lógica de Negócio**: Distribuidoras qualificadas têm planos
5. **Tratamento de Erros**: Comportamento correto com inputs inválidos
6. **Qualidade**: Dados fazem sentido (descontos válidos, nomes não vazios)

## 🌍 Dados Reais Testados

### Belo Horizonte/MG (CEMIG - Qualificada)
- ✅ Tem áreas de operação
- ✅ Tem 3 planos disponíveis (14%, 16%, 18% desconto)
- ✅ Cobertura confirmada

### São Paulo/SP (ENEL - Não Qualificada)  
- ✅ Tem área de operação
- ❌ Não tem planos (distribuidora não qualificada)
- ⚠️ Cobertura limitada

## 🚀 Executar em CI/CD

Os testes são independentes e podem ser executados em qualquer ambiente com:

1. Python 3.11+
2. Dependências instaladas (`pip install -r requirements-test.txt`)
3. Variáveis de ambiente configuradas:
   - `SERENA_API_TOKEN`
   - `SERENA_API_BASE_URL`

### Exemplo GitHub Actions:
```yaml
- name: Run API Tests
  run: |
    pip install -r requirements-test.txt
    pytest tests/test_serena_api.py -v
  env:
    SERENA_API_TOKEN: ${{ secrets.SERENA_API_TOKEN }}
    SERENA_API_BASE_URL: ${{ secrets.SERENA_API_BASE_URL }}
``` 