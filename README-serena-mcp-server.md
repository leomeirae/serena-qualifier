# Servidor MCP para API de Parcerias Serena

## 📋 Visão Geral

Este é um servidor MCP (Model Context Protocol) que permite que assistentes de IA interajam com a API de Parcerias da Serena através de ferramentas estruturadas. O servidor está disponível no endpoint: **http://mwc8k8wk0wg8o8s4k0w8scc4.157.180.32.249.sslip.io/**

### 🎯 Objetivo
Fornecer uma interface padronizada para que agentes de IA possam:
- Consultar áreas de operação para Geração Distribuída (GD)
- Gerenciar leads de vendas
- Validar qualificação de clientes
- Criar contratos de energia solar
- Interagir com a API de Parcerias da Serena de forma estruturada

### ✅ Status do Servidor
- **🟢 Servidor MCP**: 100% Funcional
- **🟢 Consultas**: Funcionando perfeitamente
- **🟢 Autenticação**: OK
- **🟢 API Externa**: Funcionando
- **⚠️ Cadastro de Leads**: Requer validações específicas (ver seção de Validações)

## 🛠️ Ferramentas Disponíveis

### 📍 Geração Distribuída (Distributed Generation)

#### 1. `consultar_areas_operacao_gd`
**Descrição**: Consulta áreas onde o serviço de Geração Distribuída está disponível

**Parâmetros**:
- `cidade` (string, opcional): Nome da cidade
- `estado` (string, opcional): Sigla do estado (ex: SP, RJ)
- `codigo_ibge` (string, opcional): Código IBGE da localidade

**Retorno**: Lista de áreas de operação disponíveis com informações de cobertura

**Exemplo de uso**:
```python
# Por cidade e estado
resultado = await consultar_areas_operacao_gd(
    cidade="São Paulo", 
    estado="SP"
)

# Por código IBGE
resultado = await consultar_areas_operacao_gd(
    codigo_ibge="3550308"
)
```

**Exemplo de resposta**:
```json
{
  "result": [
    {
      "energyUtilityPublicId": "a06dcadc-fe16-44ee-b541-0c4658aa2d3e",
      "energyUtilityName": "ENEL SP",
      "ibgeCode": 3550308,
      "state": "SP",
      "city": "SÃO PAULO",
      "energyUtilityQualified": false
    }
  ]
}
```

#### 2. `obter_planos_gd`
**Descrição**: Obtém planos de Geração Distribuída disponíveis para uma localidade

**Parâmetros**:
- `id_distribuidora` (string, opcional): ID da distribuidora (prioridade)
- `cidade` (string, opcional): Nome da cidade
- `estado` (string, opcional): Sigla do estado

**Retorno**: Lista de planos disponíveis com detalhes de desconto, fidelidade e benefícios

**Exemplo de uso**:
```python
# Por ID da distribuidora
resultado = await obter_planos_gd(
    id_distribuidora="4c03af39-6fdc-4297-9153-fa2b36617c1b"
)

# Por cidade e estado
resultado = await obter_planos_gd(
    cidade="Recife",
    estado="PE"
)
```

**Exemplo de resposta**:
```json
{
  "result": [
    {
      "energyUtilityName": "CELPE",
      "plans": [
        {
          "id": 489,
          "name": "Plano Básico-14%",
          "fidelityMonths": 0,
          "discount": "0.14",
          "offeredBenefits": []
        },
        {
          "id": 556,
          "name": "Plano Premium-18%",
          "fidelityMonths": 60,
          "discount": "0.18",
          "offeredBenefits": [
            {
              "description": "Este contrato contempla o benefício da 1° fatura paga pela Serena."
            }
          ]
        }
      ]
    }
  ]
}
```

### 💼 Conversão de Vendas (Sales Conversion)

#### 3. `cadastrar_lead`
**Descrição**: Cadastra um novo lead na base de dados

**⚠️ IMPORTANTE**: Esta ferramenta requer validações específicas (ver seção de Validações de Negócio)

**Parâmetros**:
- `dados_lead` (object, obrigatório): Objeto com todos os dados do lead

**Estrutura do dados_lead**:
```json
{
  "fullName": "string",
  "personType": "natural|juridical",
  "emailAddress": "string",
  "mobilePhone": "string",
  "utilityBillHolder": "natural|juridical",
  "utilityBillingValue": "number",
  "identificationNumber": "string",
  "nationality": "string",
  "maritalStatus": "string",
  "profession": "string",
  "zipCode": "string",
  "state": "string",
  "city": "string",
  "street": "string",
  "number": "string",
  "neighborhood": "string",
  "complement": "string",
  "plan": {
    "benefit": "string",
    "discount": "string",
    "loyaltyRequirement": "string",
    "planName": "string"
  }
}
```

**Retorno**: ID do lead criado e status da operação

**Exemplo de uso**:
```python
dados_lead = {
    "fullName": "João Silva",
    "personType": "natural",
    "emailAddress": "joao@email.com",
    "mobilePhone": "11999885544",
    "utilityBillHolder": "natural",
    "utilityBillingValue": 800.00,
    "identificationNumber": "12345678901",
    "nationality": "Brasileiro",
    "maritalStatus": "Solteiro",
    "profession": "Engenheiro",
    "zipCode": "50030-230",
    "state": "PE",
    "city": "Recife",
    "street": "Avenida Conde da Boa Vista",
    "number": "800",
    "neighborhood": "Boa Vista"
}

resultado = await cadastrar_lead({"dados_lead": dados_lead})
```

#### 4. `buscar_leads`
**Descrição**: Busca leads com filtros e paginação

**Parâmetros**:
- `filtros` (string, opcional): Filtros para busca
- `pagina` (number, opcional): Número da página (padrão: 1)
- `limite` (number, opcional): Limite de resultados por página (padrão: 10)

**Retorno**: Lista paginada de leads com informações básicas

**Exemplo de uso**:
```python
resultado = await buscar_leads(
    filtros="status:negociacao",
    pagina=1,
    limite=20
)
```

#### 5. `validar_qualificacao_lead`
**Descrição**: Valida se um lead está qualificado para produtos de energia solar

**Parâmetros**:
- `cidade` (string, obrigatório): Cidade do lead
- `estado` (string, obrigatório): Estado do lead
- `tipo_pessoa` (string, obrigatório): "natural" ou "juridical"
- `valor_conta` (number, obrigatório): Valor da conta de energia

**Retorno**: Resultado da validação com detalhes de qualificação

**Exemplo de uso**:
```python
resultado = await validar_qualificacao_lead(
    cidade="Recife",
    estado="PE",
    tipo_pessoa="natural",
    valor_conta=800.00
)
```

**Exemplo de resposta**:
```json
{
  "result": {
    "product": "Geração Distribuída",
    "qualification": true
  }
}
```

#### 6. `buscar_lead_por_id`
**Descrição**: Busca informações detalhadas de um lead específico

**Parâmetros**:
- `id_lead` (string, obrigatório): ID único do lead

**Retorno**: Informações completas do lead incluindo histórico e status

**Exemplo de uso**:
```python
resultado = await buscar_lead_por_id("lead_123456")
```

#### 7. `atualizar_lead`
**Descrição**: Atualiza informações de um lead existente

**Parâmetros**:
- `id_lead` (string, obrigatório): ID do lead
- `dados_atualizacao` (object, obrigatório): Dados a serem atualizados

**Retorno**: Confirmação da atualização

**Exemplo de uso**:
```python
dados_atualizacao = {
    "emailAddress": "novo_email@email.com",
    "mobilePhone": "11988776655"
}

resultado = await atualizar_lead("lead_123456", dados_atualizacao)
```

#### 8. `atualizar_credenciais_distribuidora`
**Descrição**: Atualiza credenciais de acesso à distribuidora de energia

**Parâmetros**:
- `id_lead` (string, obrigatório): ID do lead
- `login` (string, obrigatório): Login da distribuidora
- `senha` (string, obrigatório): Senha da distribuidora

**Retorno**: Confirmação da atualização das credenciais

**Exemplo de uso**:
```python
resultado = await atualizar_credenciais_distribuidora(
    "lead_123456",
    "usuario_distribuidora",
    "senha_distribuidora"
)
```

#### 9. `criar_contrato`
**Descrição**: Cria um contrato de geração distribuída para um lead

**Parâmetros**:
- `id_lead` (string, obrigatório): ID do lead
- `plano` (object, opcional): Dados do plano
- `representantes_legais` (array, opcional): Lista de representantes legais

**Retorno**: ID do contrato criado e status

**Exemplo de uso**:
```python
plano = {
    "id": 556,
    "name": "Plano Premium-18%",
    "discount": "0.18"
}

resultado = await criar_contrato("lead_123456", plano)
```

## ⚠️ Validações de Negócio Importantes

### 🔍 Qualificação de Leads
**CRÍTICO**: Leads devem estar qualificados antes do cadastro

#### Exemplos de Qualificação:
- **✅ Recife, PE + R$ 800,00**: Qualificado
- **❌ São Paulo, SP + R$ 500,00**: Não qualificado

#### Como Verificar:
```python
# Sempre verifique a qualificação antes do cadastro
qualificacao = await validar_qualificacao_lead(
    cidade="Recife",
    estado="PE", 
    tipo_pessoa="natural",
    valor_conta=800.00
)

if qualificacao["result"]["qualification"]:
    # Prosseguir com cadastro
    lead = await cadastrar_lead(dados_lead)
else:
    # Lead não qualificado
    print("Lead não qualificado para esta região/valor")
```

### 🚫 Validações de Duplicidade
**IMPORTANTE**: A API rejeita leads duplicados

#### Campos Únicos:
- **Email**: Não pode existir na base
- **Telefone**: Não pode existir na base  
- **CPF/CNPJ**: Provavelmente também único

#### Erros Comuns:
- `"Contact with email X already exists"`
- `"already exist lead, try update lead - X"`

### 📋 Campos Obrigatórios
**CRÍTICO**: Todos os campos obrigatórios devem ser preenchidos

#### Para Pessoa Física:
- `fullName`, `personType`, `emailAddress`, `mobilePhone`
- `utilityBillHolder`, `utilityBillingValue`, `identificationNumber`
- `nationality`, `maritalStatus`, `profession`
- `zipCode`, `state`, `city`, `street`, `number`, `neighborhood`

#### Para Pessoa Jurídica:
- Todos os campos acima + `companyName`

## 🔧 Configuração para Agentes de IA

### Configuração MCP

Para configurar este servidor MCP em um agente de IA, adicione a seguinte configuração:

```json
{
  "mcpServers": {
    "serena-partnerships": {
      "command": "python",
      "args": ["servidor_parcerias_mcp.py"],
      "env": {
        "PARTNERSHIP_API_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImQzNDBmZWEyLWM3ZTQtNGY1Ni1hYjdlLTAyMmE5ZDcwNTBiNiIsInBhcnRuZXJUeXBlIjoicGFydG5lcl9ncm91cCIsImlhdCI6MTc0NDgzNzEzOX0.YvvCD-I4GOSPmRduMoXit8Rw05c9ILoiCjhnPMgygO0",
        "PARTNERSHIP_API_ENDPOINT": "https://partnership-service-staging.api.srna.co/"
      }
    }
  }
}
```

### Configuração para Claude Desktop

1. Abra as configurações do Claude Desktop
2. Vá para a seção "MCP Servers"
3. Adicione um novo servidor com as seguintes configurações:
   - **Nome**: Serena Partnerships API
   - **Comando**: `python`
   - **Argumentos**: `servidor_parcerias_mcp.py`
   - **Diretório de trabalho**: Caminho para este projeto
   - **Variáveis de ambiente**: Configure as variáveis PARTNERSHIP_API_KEY e PARTNERSHIP_API_ENDPOINT

### Configuração para Ollama

Adicione ao arquivo de configuração do Ollama:

```yaml
mcp_servers:
  - name: serena-partnerships
    command: python
    args: [servidor_parcerias_mcp.py]
    env:
      PARTNERSHIP_API_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImQzNDBmZWEyLWM3ZTQtNGY1Ni1hYjdlLTAyMmE5ZDcwNTBiNiIsInBhcnRuZXJUeXBlIjoicGFydG5lcl9ncm91cCIsImlhdCI6MTc0NDgzNzEzOX0.YvvCD-I4GOSPmRduMoXit8Rw05c9ILoiCjhnPMgygO0"
      PARTNERSHIP_API_ENDPOINT: "https://partnership-service-staging.api.srna.co/"
```

## 🌐 Endpoints da API

### Base URL
- **Staging**: `https://partnership-service-staging.api.srna.co/`
- **Produção**: `https://partnership.api.srna.co/`

### Mapeamento de Endpoints

| Ferramenta MCP | Método HTTP | Endpoint | Descrição |
|----------------|-------------|----------|-----------|
| `consultar_areas_operacao_gd` | GET | `/distribuited-generation/operation-areas` | Consulta áreas de operação |
| `obter_planos_gd` | GET | `/distribuited-generation/plans` | Obtém planos disponíveis |
| `cadastrar_lead` | POST | `/sales-conversion/leads` | Cadastra novo lead |
| `buscar_leads` | GET | `/sales-conversion/leads` | Lista leads com filtros |
| `validar_qualificacao_lead` | GET | `/sales-conversion/leads/qualification` | Valida qualificação |
| `buscar_lead_por_id` | GET | `/sales-conversion/leads/{id}` | Busca lead específico |
| `atualizar_lead` | PUT | `/sales-conversion/leads/{id}` | Atualiza lead |
| `atualizar_credenciais_distribuidora` | PATCH | `/sales-conversion/leads/{id}/energy-utility-credentials` | Atualiza credenciais |
| `criar_contrato` | POST | `/sales-conversion/leads/{id}/contracts` | Cria contrato |

## 🔐 Autenticação

Todas as requisições utilizam autenticação Bearer Token:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 📊 Estrutura de Dados

### Lead (Pessoa Física)
```json
{
  "fullName": "string",
  "personType": "natural",
  "emailAddress": "string",
  "mobilePhone": "string",
  "utilityBillHolder": "natural",
  "utilityBillingValue": "number",
  "identificationNumber": "string",
  "nationality": "string",
  "maritalStatus": "string",
  "profession": "string",
  "zipCode": "string",
  "state": "string",
  "city": "string",
  "street": "string",
  "number": "string",
  "neighborhood": "string",
  "complement": "string"
}
```

### Lead (Pessoa Jurídica)
```json
{
  "fullName": "string",
  "personType": "juridical",
  "emailAddress": "string",
  "mobilePhone": "string",
  "utilityBillHolder": "juridical",
  "utilityBillingValue": "number",
  "identificationNumber": "string",
  "companyName": "string",
  "zipCode": "string",
  "state": "string",
  "city": "string",
  "street": "string",
  "number": "string",
  "neighborhood": "string",
  "complement": "string"
}
```

## 🚀 Casos de Uso

### 1. Processo de Vendas Completo
```python
# 1. Verificar se a área tem cobertura
areas = await consultar_areas_operacao_gd(cidade="Recife", estado="PE")

# 2. Obter planos disponíveis
planos = await obter_planos_gd(cidade="Recife", estado="PE")

# 3. Validar qualificação ANTES do cadastro
qualificacao = await validar_qualificacao_lead(
    cidade="Recife",
    estado="PE",
    tipo_pessoa="natural",
    valor_conta=800.00
)

# 4. Se qualificado, cadastrar lead
if qualificacao["result"]["qualification"]:
    dados_lead = {
        "fullName": "João Silva",
        "personType": "natural",
        "emailAddress": "joao.unique@email.com",
        "mobilePhone": "11999885544",
        "utilityBillHolder": "natural",
        "utilityBillingValue": 800.00,
        "identificationNumber": "12345678901",
        "nationality": "Brasileiro",
        "maritalStatus": "Solteiro",
        "profession": "Engenheiro",
        "zipCode": "50030-230",
        "state": "PE",
        "city": "Recife",
        "street": "Avenida Conde da Boa Vista",
        "number": "800",
        "neighborhood": "Boa Vista"
    }
    
    lead = await cadastrar_lead({"dados_lead": dados_lead})
    print(f"Lead criado: {lead}")
else:
    print("Lead não qualificado para esta região/valor")
```

### 2. Consulta de Leads Existentes
```python
# Buscar leads ativos
leads = await buscar_leads(limite=50)

# Para cada lead, buscar detalhes
for lead in leads["leads"]:
    detalhes = await buscar_lead_por_id(lead["id"])
    print(f"Lead: {detalhes['fullName']} - Status: {detalhes['status']}")
```

### 3. Atualização em Lote
```python
# Buscar leads que precisam de atualização
leads = await buscar_leads(filtros="status:pending_credentials")

# Atualizar credenciais
for lead in leads["leads"]:
    await atualizar_credenciais_distribuidora(
        lead["id"], 
        "novo_user",
        "nova_senha"
    )
```

## ⚠️ Tratamento de Erros

O servidor inclui tratamento robusto de erros:

### Códigos de Erro Comuns
- `400`: Dados inválidos ou obrigatórios ausentes
- `401`: Token de autenticação inválido
- `404`: Recurso não encontrado
- `422`: Dados de validação inválidos
- `500`: Erro interno do servidor

### Erros Específicos de Cadastro
- `"Lead não está apto a seguir no cadastro"`: Lead não qualificado
- `"Contact with email X already exists"`: Email já existe
- `"already exist lead, try update lead - X"`: Telefone já existe

### Exemplo de Tratamento
```python
try:
    resultado = await cadastrar_lead({"dados_lead": dados_lead})
    print(f"Lead criado com sucesso")
except Exception as e:
    if "Lead não está apto" in str(e):
        print("Lead não qualificado - verifique região e valor da conta")
    elif "already exists" in str(e):
        print("Lead já existe - use dados únicos")
    elif "422" in str(e):
        print("Dados de validação inválidos")
    else:
        print(f"Erro ao cadastrar lead: {e}")
```

## 🔒 Segurança

### Boas Práticas
- ✅ A chave de API é carregada de variável de ambiente
- ✅ Todas as requisições incluem autenticação Bearer Token
- ✅ Não armazene credenciais no código fonte
- ✅ Use HTTPS para todas as comunicações
- ✅ Valide todos os dados de entrada

### Configuração de Segurança
```bash
# Configure as variáveis de ambiente
export PARTNERSHIP_API_KEY="sua_chave_aqui"
export PARTNERSHIP_API_ENDPOINT="https://partnership-service-staging.api.srna.co/"
```

## 📈 Monitoramento e Logs

### Logs Disponíveis
- Requisições HTTP com timestamps
- Erros de validação
- Tempo de resposta das APIs
- Status de autenticação

### Exemplo de Log
```
[2024-01-15 10:30:45] INFO: Requisição para /sales-conversion/leads
[2024-01-15 10:30:46] INFO: Lead criado com sucesso - ID: lead_123456
[2024-01-15 10:30:47] INFO: Tempo de resposta: 1.2s
```

## 🧪 Testes

### Testando as Ferramentas
```python
# Teste básico de conectividade
areas = await consultar_areas_operacao_gd(cidade="São Paulo", estado="SP")
assert areas is not None
assert len(areas["result"]) > 0

# Teste de qualificação
qualificacao = await validar_qualificacao_lead(
    cidade="Recife",
    estado="PE",
    tipo_pessoa="natural",
    valor_conta=800.00
)
assert qualificacao["result"]["qualification"] == True

# Teste de cadastro de lead (com dados únicos)
lead_data = {
    "fullName": "Teste MCP",
    "personType": "natural",
    "emailAddress": f"teste.{timestamp}@mcp.com",
    "mobilePhone": f"1199988{timestamp}",
    "utilityBillHolder": "natural",
    "utilityBillingValue": 800.00,
    "identificationNumber": "12345678901",
    "nationality": "Brasileiro",
    "maritalStatus": "Solteiro",
    "profession": "Engenheiro",
    "zipCode": "50030-230",
    "state": "PE",
    "city": "Recife",
    "street": "Avenida Conde da Boa Vista",
    "number": "800",
    "neighborhood": "Boa Vista"
}
lead = await cadastrar_lead({"dados_lead": lead_data})
assert lead is not None
```

## 📞 Suporte

### Recursos de Ajuda
- **Documentação da API**: Consulte `api-documentation.md`
- **Issues**: Abra issues no repositório para bugs ou melhorias
- **Equipe de Desenvolvimento**: Entre em contato para suporte técnico

### Informações de Contato
- **Email**: dev@serena.co
- **Slack**: #serena-partnerships-api
- **Documentação**: https://docs.serena.co/partnerships

## 🔄 Versões e Changelog

### v1.0.0 (Atual)
- ✅ Implementação completa das 9 ferramentas MCP
- ✅ Suporte a leads pessoa física e jurídica
- ✅ Validação de qualificação
- ✅ Criação de contratos
- ✅ Tratamento robusto de erros
- ✅ Documentação completa com validações de negócio
- ✅ Exemplos práticos de uso

### Próximas Versões
- 🔄 Suporte a webhooks
- 🔄 Cache de consultas frequentes
- 🔄 Métricas de performance
- 🔄 Suporte a múltiplos ambientes

---

**Desenvolvido pela Equipe Serena** 🚀 