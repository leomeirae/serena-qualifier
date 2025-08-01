# Guia Técnico e Comercial Unificado: Treinamento do Agente SDR IA “Sílvia” Serena Energia (100% MCP)

> **Última atualização: 01 Ago 2025**  
> **Atenção:** Este documento SUPERA todas as versões anteriores. Ele traz todos os requisitos do atendimento, fluxos, dicas de tom de conversa, arquitetura, arquivos/códigos e integrações exclusivamente via MCP Servers (JSON-RPC). Use como referência oficial para desenvolvimento, DevOps, treinamento e operação.

## 🔗 Sumário

1. [Introdução](#introducao)
2. [Contexto Comercial e Posicionamento](#comercial)
3. [Persona & Tom de Voz](#persona)
4. [Fluxo de Atendimento (YAML, Scripts, MCP)](#fluxo)
5. [Arquitetura Técnica: Arquivos & Integração MCP Server](#arquivos)
   - 5.1 [Scripts e Funções](#scripts)
   - 5.2 [Configuração Workflow Kestra](#kestra)
   - 5.3 [Payloads JSON-RPC por MCP](#jsonrpc)
   - 5.4 [Testes e Mocks MCP](#testes)
   - 5.5 [Persistência, Logs e Métricas](#metricas)
6. [Políticas de Retry, Timeout & Fallback](#retry)
7. [Anexos: Troubleshooting, Ambiente e Extras](#anexos)

## 1. Introdução <a name="introducao"></a>

O **Serena SDR IA** é um agente digital batizado de Sílvia, treinado para receber, qualificar e encaminhar leads de energia renovável pelo WhatsApp de forma humanizada, personalizada, e 100% conectada via servidores MCP (Model Context Protocol — JSON-RPC). Todos os dados são consultados, salvos e atualizados via ferramentas MCP expostas nos respectivos servers WhatsApp, Serena e Supabase.

## 2. Contexto Comercial e Posicionamento <a name="comercial"></a>

- **Sobre:** A Serena Energia é referência no Brasil em energia solar e eólica, operando há 15 anos com foco em economia, facilidade e sustentabilidade para clientes residenciais e empresariais.
- **Diferenciais:** Zero investimento inicial, contratação digital, sem instalação de equipamentos, desconto mensal garantido, primeira fatura grátis.
- **Promoção Real:** “Economize até 18%* na conta residencial, até 35% para empresas.” *É obrigatório buscar o valor em tempo real no campo `discount` de cada plano em `obter_planos_gd` via MCP (`SERENA_MCP_URL`).
- **Bônus:** Programa de indicação (R$100 por novo cliente), pagamento via cartão de crédito, abrangência para mais de 2.000 cidades. Não precisa instalar nada.
- **Perguntas-chave:**  
  - “Preciso instalar painéis?” → NÃO.  
  - “Muda minha distribuidora?” → NÃO.  
  - “Recebo duas contas?” → NÃO, uma só.
- **Nota Técnica:**  
  > *Todos os dados apresentados ao cliente (planos, descontos, cobertura) vêm exclusivamente via MCP Serena (`SERENA_MCP_URL`), método `obter_planos_gd`.*

## 3. Persona & Tom de Voz <a name="persona"></a>

- **Persona:** Sílvia, consultiva, cordial, otimista, imediata.
- **Tom:** Próximo, simples, sem jargão, animado, sempre use emojis só **😊** e **⚡**.
- **Regras:**
  - **NUNCA** pergunte informações já enviadas no formulário do lead.
  - Responda dúvidas enfatizando “zero custo”, “primeira fatura grátis”, “energia limpa”.
  - Se mencionar descontos, busque sempre o número via MCP na hora.
  - Demostrar empatia, celebração e senso de urgência.
- **Exemplo de saudação:**
  ```
  Oi [Nome]! 😊 Vi que sua conta de luz está na faixa de R$[valor]. Aqui na Serena, você pode economizar até R$[economia_apurada] todo mês! ⚡ Quer saber como funciona sem precisar instalar nada?
  ```

## 4. Fluxo de Atendimento (Workflow YAML, Scripts, MCP) <a name="fluxo"></a>

### Fluxo Resumido

| Etapa               | Script/Função                                         | MCP Server    | Método RPC           |
|---------------------|-------------------------------------------------------|---------------|----------------------|
| Captura de Lead     | `supabase_tools.py → save_or_update_lead()`           | Supabase MCP  | `execute_sql`        |
| Saudação            | `agent_orchestrator.py → handle_greeting()`           | WhatsApp MCP  | `sendTextMessage`    |
| Consulta de Planos  | `serena_tools.py → obter_planos_gd(cidade, estado)`   | Serena MCP    | `obter_planos_gd`    |
| Validação           | `serena_tools.py → validar_qualificacao_lead()`       | Serena MCP    | `validar_qualificacao_lead` |
| Upload de Conta     | `supabase_tools.py → upload_energy_bill_image()`      | Supabase MCP  | `execute_sql`        |
| Handoff para Humano | `agent_orchestrator.py → handle_handoff_to_human()`   | Supabase MCP  | `execute_sql`        |

#### Fluxo Conversacional
1. Saudação personalizada (nome, cidade, valor da conta)
2. Apresentação dos planos (faça chamada MCP para buscar “discount real”)
3. Esclarecimento de dúvidas (reforce “sem custo, sem obra”)
4. Solicitação da foto/arquivo da conta de energia
5. Encaminhamento ao humano após recebimento do documento

#### Situações especiais:
- **Se MCP falhar:** aguarde 1 min e tente 3 vezes, depois envie desculpa ao usuário e registre no log.

## 5. Arquitetura Técnica <a name="arquivos"></a>

### 5.1 Scripts & Funções <a name="scripts"></a>

```text
scripts/agent_tools/supabase_tools.py
  - save_or_update_lead()
  - get_lead_by_phone()
  - upload_energy_bill_image()

scripts/agent_tools/serena_tools.py
  - obter_planos_gd(cidade, estado)
  - validar_qualificacao_lead()

scripts/agent_orchestrator.py
  - handle_greeting()
  - handle_handoff_to_human()

scripts/agent_tools/mcp_supabase_integration.py (se utilizado)
  - consultar_dados_lead_mcp()
  - salvar_ou_atualizar_lead_mcp()
```

### 5.2 Configuração Kestra & YAML <a name="kestra"></a>

**Exemplo de variáveis de ambiente:**
```yaml
vars:
  serena_mcp_url:     http://serena-mcp-server:3002
  supabase_mcp_url:   http://supabase-mcp-server:3000
  whatsapp_mcp_url:   http://whatsapp-mcp-server:3003
```

**inputFiles:**
```yaml
inputFiles:
  scripts/agent_orchestrator.py: |-
    # (conteúdo do orchestrator)
  scripts/agent_tools/serena_tools.py: |-
    # (conteúdo serena_tools)
  scripts/agent_tools/supabase_tools.py: |-
    # (conteúdo supabase_tools)
```

### 5.3 Payloads JSON-RPC por MCP <a name="jsonrpc"></a>

**Sempre enviar requisições como no exemplo abaixo:**

```jsonc
{
  "jsonrpc":"2.0",       // padrão JSON-RPC
  "id":1,
  "method":"tools/call",
  "params":{
    "name":"sendTemplateMessage",  // exemplo WhatsApp MCP
    "arguments":{
      "to":"+55...",
      "templateName":"welcome_profile_site",
      "components":[{"type":"body","parameters":[{"type":"text","text":"João"}]}]
    }
  }
}
```
*Comente cada campo para facilitar Proof-of-Concept/Debug.*

### 5.4 Testes & Mock MCP <a name="testes"></a>

- Para integração MCP: configure no ambiente de testes:
```yaml
environment:
  SUPABASE_MCP_URL: http://localhost:3000/mcp-mock
  SERENA_MCP_URL:   http://localhost:3002/mcp-mock
  WHATSAPP_MCP_URL: http://localhost:3003/mcp-mock
```
- Caminhos:
  - Unidade: `tests/unit/test_serena_tools_mcp.py`
  - E2E:     `tests/e2e/test_whatsapp_flow_mcp.py`

### 5.5 Persistência, Logs e Métricas <a name="metricas"></a>

- **Tabelas**: `leads`, `lead_status`, `sdr_logs`
- **Chamada MCP para log:**
```python
payload = {
  "jsonrpc":"2.0",
  "id":1,
  "method":"tools/call",
  "params":{
    "name":"log_event",
    "arguments":{"event":"greeting_sent","lead_id":lead_id}
  }
}
requests.post(f"{SUPABASE_MCP_URL}/mcp", json=payload)
```
- **Query exemplo para dashboard conversão**:
```sql
SELECT COUNT(*) FILTER (WHERE contract_created) * 100.0 / COUNT(*) AS taxa_conversao
FROM lead_status;
```
- Relatório: automatize via cron às 8h.

## 6. Políticas de Retry, Timeout & Fallback <a name="retry"></a>

- **Qualquer falha em chamada MCP:** aguarde 1 min, tente 3 vezes (exponencial).  
- **Timeout padrão:** 10–15 segundos
- **Falha total:** registre no sdr_logs, envie mensagem padrão:
  > “Desculpe, tivemos um problema técnico. Retornarei em breve. 😊”

## 7. Anexos: Troubleshooting, Ambiente e Extras <a name="anexos"></a>

### Principais URLs MCP e Health Checks

| Server           | URL Base                                             | Health        |
|------------------|-----------------------------------------------------|--------------|
| WhatsApp MCP     | http://bw48gc80kokwwckg0wskc40c.157.180.32.249.sslip.io/ | /health      |
| Supabase MCP     | http://hwg4ks4ooooc04wsosookoog.157.180.32.249.sslip.io/ | /health      |
| Serena MCP       | http://mwc8k8wk0wg8o8s4k0w8scc4.157.180.32.249.sslip.io/ | GET `/`      |

### Troubleshooting acelerado

1. **MCP não responde:** test via curl `/health`.  
2. **Falha WhatsApp:** revise `WHATSAPP_API_TOKEN` e números.
3. **Dados desatualizados:** use “execute_sql” no Supabase MCP.
4. **Flag `initial_template_sent` não atualiza:** cheque fluxo de activation.
5. **Qualificação recusa:** verifique campo via `validar_qualificacao_lead`.
6. **Logs/Kestra:** sempre debug pelos logs em tempo real (`docker-compose logs -f kestra-agent`).

### Blueprints úteis
- Kestra: “Chat with Elasticsearch Data”, “Wait & Remind”
- OpenAI Cookbook “Deep Research API Agents”
- OpenAI GPT-4 Function Calling
- WhatsApp Business API – Cloud Version

# RESUMO – Checklist de Implementação e Treinamento

- Toda lógica de qualificação, consulta de planos, logs, follow-up e envio de mensagens é feita via métodos MCP, nunca REST direto, respeitando o payload JSON-RPC.
- O treinamento do agente Sílvia reforça sempre o valor humano, a economia real e benefícios sustentáveis, usando apenas dados dinâmicos MCP.
- As funções Python e YAML são mapeadas 1:1 com suas chamadas MCP equivalentes.
- Scripts e workflows sempre atualizados para manter nomes reais e referências de arquivos.
- Testes sempre em mock MCP, logs por função/etapa após cada chamada relevante.
- *Atualize sempre este documento conforme evoluírem o escopo dos MCP Servers e as regras comerciais do negócio.*

**Este é o seu manual central, tanto para programar como para treinar o time (IA E HUMANO) sobre o atendimento Serena Energia!**

Fontes
[1] README.md https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/71661805/3d15d301-de33-4296-ba85-57170bc5a8c2/README.md
[2] Serena-Energia-Perfil-e-Comunicacao.pdf https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/71661805/7a2a27bf-de77-4835-97b0-b97a78f6a34f/Serena-Energia-Perfil-e-Comunicacao.pdf
