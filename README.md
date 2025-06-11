# Serena Lead Qualifier

Sistema automatizado para qualificação de leads de energia solar via WhatsApp + IA.

## 🏗️ Arquitetura

- **Kestra**: Orquestração de workflows
- **WhatsApp Business API**: Comunicação com leads
- **OpenAI GPT-4**: Agente IA conversacional  
- **LangChain**: Framework IA complementar (NOVO ✨)
- **Supabase**: Persistência de dados
- **Docker**: Containerização completa

## 📦 Estrutura do Projeto

```
serena-qualifier/
├── scripts/
│   ├── serena_agent/           # 🆕 LangChain Framework
│   │   ├── core_agent.py       # Orquestrador principal
│   │   ├── tools/              # Wrappers LangChain
│   │   │   ├── conversation_tool.py
│   │   │   ├── serena_api_tool.py  
│   │   │   └── ocr_tool.py
│   │   └── prompts/            # Templates padronizados
│   │       ├── classification.py
│   │       ├── extraction.py
│   │       └── conversation.py
│   ├── ai_agent.py             # ✅ Agente IA (preservado)
│   ├── serena_api.py           # ✅ API real Serena
│   ├── ocr_processor.py        # ✅ Processamento faturas
│   └── whatsapp_sender.py      # ✅ Envio WhatsApp
├── kestra/workflows/           # ✅ Workflows Kestra
├── utils/                      # ✅ Utilitários
└── docker-compose.yml          # ✅ Stack completa
```

## 🚀 Setup Rápido

```bash
# 1. Clone o projeto
git clone <repo-url>
cd serena-qualifier

# 2. Configure ambiente
cp .env.example .env
# Edite .env com suas credenciais

# 3. Instale dependências
pip install -r requirements.txt

# 4. Teste estrutura
python test_serena_agent_structure.py

# 5. Execute stack completa
docker-compose up -d
```

## 🧪 Testes

```bash
# Teste estrutura LangChain
python test_serena_agent_structure.py

# Teste API Serena (real)
python test_serena_api_detailed.py

# Teste integração completa
python test_ai_integration.py
```

## 📋 Status Desenvolvimento

- ✅ **TASK 1**: Framework LangChain complementar implementado
- ✅ **TASK 2**: LangChain real funcionando com AgentExecutor ativo
- ✅ **TASK 3**: Workflows Kestra otimizados e casos avançados

**🚀 SISTEMA COMPLETO E OPERACIONAL!**

### 🎯 Funcionalidades Ativas:
- **AgentExecutor LangChain** com OpenAI GPT-4o-mini
- **3 Tools reais**: Supabase + API Serena + OCR
- **Modo híbrido**: LangChain + prompts otimizado
- **Workflows Kestra v3**: Análise inteligente unificada
- **Casos avançados**: Multi-contexto + qualificação dinâmica
- **Respostas personalizadas**: Adaptativas por categoria (premium/qualificado)
- **Analytics avançados**: Métricas de performance e conversão
- **100% compatibilidade** com workflows Kestra existentes

## 📚 Documentação

- [`PLANNING.md`](PLANNING.md) - Planejamento arquitetural
- [`TASK.md`](TASK.md) - Tarefas específicas e progresso
- [`PROJECT_GUIDE.md`](PROJECT_GUIDE.md) - Guia completo implementação

## 🔧 Tecnologias

- **Python 3.11+** - Backend principal
- **LangChain 0.1.20** - Framework IA (NOVO)
- **OpenAI GPT-4o-mini** - Modelo conversacional
- **FastAPI** - APIs REST
- **Supabase** - Database PostgreSQL
- **Docker** - Containerização
- **Kestra** - Orquestração workflows