# 🤖 Planejamento: Framework LangChain COMPLEMENTAR ao Ecossistema Serena

## 📋 Contexto REAL do Projeto

### 🏗️ Arquitetura Existente (MANTIDA)
```
🐳 Docker Compose Stack:
├── Kestra (Orchestrator) - workflows yml
├── PostgreSQL + Redis (Storage)  
├── WhatsApp Service (API integration)
├── Python Runner (Script execution)
└── Elasticsearch (Logs - opcional)

📱 Fluxo de Negócio REAL:
1️⃣ Lead preenche formulário → full-lead-qualification-workflow
2️⃣ Template WhatsApp enviado → ai-conversation-activation-v2  
3️⃣ Conversa IA + OCR faturas → qualificação completa
4️⃣ API Serena REAL (planos, cobertura) → fechamento negócio
```

### 🎯 Propósito Definido do Workflow
**O agente IA é o CORAÇÃO da qualificação de leads para Serena Energia**
- **Input**: Mensagens WhatsApp (texto + imagens de faturas)
- **Processo**: Classificar → Extrair → Qualificar → Responder  
- **Output**: Leads qualificados para energia solar
- **Meta**: Aumentar conversão e consistência das respostas

## 🔧 Problema Atual Identificado

### ❌ Fragmentação do Agente Atual
```python
# ANTES: Espalhado e inconsistente
scripts/ai_agent.py          # 319 linhas - muitas responsabilidades
utils/conversation_manager.py # 306 linhas - mistura negócio + infra
scripts/ocr_processor.py     # Simulação OCR
scripts/serena_api.py        # ✅ REAL - funcionando 
```

### ✅ Solução LangChain COMPLEMENTAR
```python
# DEPOIS: Modular e consistente (integra COM existente)
scripts/serena_agent/
├── core_agent.py           # PromptTemplate + AgentExecutor  
├── intent_classifier.py   # Classificação padronizada
├── data_extractor.py      # Extração estruturada
├── tools/
│   ├── conversation_tool.py    # Wrapper conversation_manager
│   ├── serena_api_tool.py     # Wrapper serena_api.py ✅ 
│   └── ocr_tool.py           # Wrapper ocr_processor.py
└── prompts/                # Templates LangChain
```

## 🎯 Objetivos REDEFINIDOS

### 1. Integração Seamless com Kestra
- **NÃO substituir** workflows existentes
- **Simplificar** tasks Python nos workflows  
- **Manter** triggers webhook e estrutura Docker
- **Melhorar** consistência do agente dentro do fluxo

### 2. Wrapper LangChain sobre Componentes Existentes
- `conversation_manager.py` → `ConversationTool` (LangChain)
- `serena_api.py` → `SerenaAPITool` (LangChain)  
- `ocr_processor.py` → `OCRTool` (LangChain)
- **Reuso total** da lógica existente

### 3. Performance e Consistência  
- **Prompts padronizados** via PromptTemplate
- **Output estruturado** via OutputParser
- **Error handling** unificado  
- **Logging** integrado com Kestra

## 📝 Tarefas REDEFINIDAS

### Fase 1: Análise de Integração ✅
- [x] ~~Analisar documento agente-ia-serena.md~~
- [x] ~~Entender arquitetura Kestra/Docker~~
- [x] ~~Mapear componentes existentes~~
- [x] ~~Definir pontos de integração~~

### Fase 2: Setup Estrutura (Priority 1) 
- [ ] Criar `scripts/serena_agent/` modular
- [ ] Atualizar `requirements.txt` com LangChain  
- [ ] **Manter** all scripts existentes 
- [ ] Configurar imports e testes

### Fase 3: Core Agent Wrapper (Priority 1)
- [ ] `SerenaAIAgent` como orquestrador LangChain
- [ ] `AgentExecutor` com tools customizadas
- [ ] **Integrar** com `conversation_manager` existente
- [ ] **Uma** função pública: `process_conversation()`

### Fase 4: Tools LangChain (Priority 1)
- [ ] `ConversationTool` → wrapper conversation_manager.py
- [ ] `SerenaAPITool` → wrapper serena_api.py ✅
- [ ] `OCRTool` → wrapper ocr_processor.py  
- [ ] `@tool` decorators para AgentExecutor

### Fase 5: Prompts Padronizados (Priority 2)
- [ ] `PromptTemplate` para classificação
- [ ] `PromptTemplate` para extração
- [ ] `OutputParser` para respostas estruturadas
- [ ] Contexto de conversa dinâmico

### Fase 6: Integração Kestra (Priority 1)
- [ ] **Simplificar** `ai-conversation-activation-v2.yml`
- [ ] **Uma task Python**: `call-serena-agent`
- [ ] **Manter** estrutura webhook + Docker
- [ ] Testes end-to-end

## 🔧 Tecnologias COMPLEMENTARES

### Core LangChain 
- **LangChain**: Orquestração + AgentExecutor
- **OpenAI GPT-4o-mini**: Mantido (já configurado)
- **Tools**: Wrappers sobre código existente
- **Prompts**: Padronização sem quebrar lógica

### Integração Preservada ✅
- **conversation_manager.py**: Supabase + lógica histórico
- **serena_api.py**: API real funcionando
- **ocr_processor.py**: Processamento faturas  
- **Kestra workflows**: Triggers + orchestração
- **Docker compose**: Infraestrutura completa

## ⚡ Vantagens da Abordagem COMPLEMENTAR

### 1. Zero Breaking Changes
- Workflows Kestra continuam funcionando
- APIs existentes preservadas  
- Docker stack mantida
- Rollback sempre possível

### 2. Melhoria Incremental
- Agente mais consistente dentro do fluxo existente
- Prompts padronizados via LangChain
- Error handling unificado
- Logging melhorado

### 3. Modularidade Preservada
- Cada componente mantém responsabilidade
- LangChain como "cola" inteligente
- Testes isolados por módulo
- Manutenção facilitada

## 🚀 Implementação FOCADA

### Script de Migração
```python
# ANTES (nos workflows Kestra):
ai_result = process_ai_request(phone, message, "classify")

# DEPOIS (mesmo resultado, melhor estrutura):
ai_result = SerenaAIAgent().process_conversation(phone, message)
```

### Compatibilidade Total
- **Interface idêntica** para Kestra
- **Mesmos inputs/outputs** dos workflows
- **Performance igual ou melhor**
- **Logs mais detalhados**

## 📊 Métricas de Sucesso REALISTAS
- **Zero downtime** na migração
- **Redução 30%** tempo para adicionar novos prompts
- **Aumento 20%** consistência respostas
- **100% compatibilidade** com workflows existentes
- **Manter** performance atual ou melhorar

## 🔄 Próxima Tarefa ESPECÍFICA
**TASK 1**: Criar estrutura serena_agent/ e fazer primeiro wrapper do conversation_manager como LangChain Tool - mantendo interface 100% compatível 