# Verificação de Autenticação do Kestra v0.24.0

## ✅ Status Atual
- **Versão:** Kestra v0.24.0 instalada com sucesso
- **Status:** Solicitando login e senha (✅ **NORMAL**)
- **Problema:** Credenciais não estão sendo aceitas

## 🔑 Credenciais Configuradas

### No docker-compose-coolify.yml:
```yaml
KESTRA_SERVER_BASICAUTH_USERNAME: "leonardo@darwinai.com.br"
KESTRA_SERVER_BASICAUTH_PASSWORD: "@Atjlc151523"
```

### Para Acesso:
- **URL:** https://kestra.darwinai.com.br
- **Username:** `leonardo@darwinai.com.br`
- **Password:** `@Atjlc151523`

## 🔍 Verificações Necessárias

### 1. **Verificar Variáveis de Ambiente no Coolify**
No painel do Coolify, verifique se as seguintes variáveis estão definidas:

```bash
# Obrigatórias para autenticação
KESTRA_SERVER_BASICAUTH_USERNAME=leonardo@darwinai.com.br
KESTRA_SERVER_BASICAUTH_PASSWORD=@Atjlc151523

# Outras variáveis importantes
SECRET_OPENAI_API_KEY=...
SECRET_WHATSAPP_API_TOKEN=...
SECRET_SERENA_API_TOKEN=...
SECRET_SUPABASE_URL=...
SECRET_SUPABASE_KEY=...
SECRET_DB_CONNECTION_STRING=...
```

### 2. **Verificar Logs do Kestra no Coolify**
No painel do Coolify, acesse os logs do container `kestra` e procure por:

```bash
# Logs de inicialização
grep -i "auth\|basic\|password" logs

# Logs de erro
grep -i "error\|exception" logs
```

### 3. **Testar Conectividade**
```bash
# Teste básico de conectividade
curl -I https://kestra.darwinai.com.br

# Teste com autenticação
curl -u "leonardo@darwinai.com.br:@Atjlc151523" https://kestra.darwinai.com.br
```

## 🛠️ Soluções Possíveis

### **Problema 1: Variáveis não definidas no Coolify**
**Solução:** Adicionar as variáveis no painel do Coolify

### **Problema 2: Caracteres especiais na senha**
**Solução:** Verificar se o `@` na senha está sendo interpretado corretamente

### **Problema 3: Cache do navegador**
**Solução:** 
- Limpar cache do navegador
- Usar modo incógnito
- Tentar outro navegador

### **Problema 4: Configuração do proxy reverso**
**Solução:** Verificar se o Traefik está passando as credenciais corretamente

## 🔧 Script de Diagnóstico

Execute este script para verificar a configuração:

```bash
#!/bin/bash
echo "🔍 Diagnóstico de Autenticação do Kestra v0.24.0"
echo "================================================"

# 1. Teste de conectividade
echo "1. Testando conectividade..."
curl -I https://kestra.darwinai.com.br 2>/dev/null | head -5

# 2. Teste de autenticação
echo ""
echo "2. Testando autenticação..."
curl -u "leonardo@darwinai.com.br:@Atjlc151523" \
     -I https://kestra.darwinai.com.br 2>/dev/null | head -5

# 3. Verificar se o serviço está respondendo
echo ""
echo "3. Verificando resposta do serviço..."
curl -s https://kestra.darwinai.com.br | grep -i "kestra\|login" | head -3
```

## 📞 Próximos Passos

1. **Verificar variáveis no Coolify**
2. **Testar credenciais manualmente**
3. **Verificar logs do container**
4. **Se necessário, reiniciar o serviço**

## 🚨 Se Nada Funcionar

1. **Reverter para v0.23.7 temporariamente:**
   ```yaml
   image: kestra/kestra:v0.23.7
   ```

2. **Ou definir credenciais via Setup Page:**
   - Acesse https://kestra.darwinai.com.br
   - Use a página de setup para configurar credenciais

3. **Contatar suporte técnico** com logs completos
