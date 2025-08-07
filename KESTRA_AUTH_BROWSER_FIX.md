# 🔧 Correção de Autenticação do Kestra no Navegador

## ✅ Status: Credenciais Funcionando via API

**Diagnóstico:** As credenciais estão funcionando corretamente via API (status 200), mas há problemas no navegador.

## 🔍 Problema Identificado

- ✅ **API:** Credenciais funcionando
- ❌ **Navegador:** "Nome de usuário ou senha inválidos"

## 🛠️ Soluções para o Navegador

### **Solução 1: Limpar Cache do Navegador**

#### **Chrome/Edge:**
1. Pressione `Ctrl+Shift+Delete` (Windows) ou `Cmd+Shift+Delete` (Mac)
2. Selecione "Todo o período"
3. Marque todas as opções
4. Clique em "Limpar dados"

#### **Firefox:**
1. Pressione `Ctrl+Shift+Delete` (Windows) ou `Cmd+Shift+Delete` (Mac)
2. Selecione "Tudo"
3. Clique em "Limpar agora"

### **Solução 2: Modo Incógnito/Privado**

1. Abra uma janela incógnita/privada
2. Acesse: https://kestra.darwinai.com.br
3. Use as credenciais:
   - **Username:** `leonardo@darwinai.com.br`
   - **Password:** `@Atjlc151523`

### **Solução 3: URL Direta**

Tente acessar diretamente:
- https://kestra.darwinai.com.br/ui/
- https://kestra.darwinai.com.br/login

### **Solução 4: Outro Navegador**

Teste em um navegador diferente:
- Chrome
- Firefox
- Safari
- Edge

## 🔧 Verificação de Configuração

### **Credenciais Confirmadas:**
- **Username:** `leonardo@darwinai.com.br`
- **Password:** `@Atjlc151523`
- **URL:** https://kestra.darwinai.com.br

### **Teste via Terminal:**
```bash
# Teste básico
curl -I https://kestra.darwinai.com.br/ui/

# Teste com autenticação
curl -u "leonardo@darwinai.com.br:@Atjlc151523" \
     https://kestra.darwinai.com.br/ui/
```

## 🚨 Possíveis Causas

### **1. Cache do Navegador**
- Credenciais antigas em cache
- Cookies de sessão conflitantes

### **2. Configuração de Proxy**
- Traefik não passando credenciais corretamente
- Headers de autenticação mal configurados

### **3. Caracteres Especiais**
- O `@` na senha pode estar sendo interpretado incorretamente

### **4. Configuração de CORS**
- Problemas de cross-origin requests

## 🔍 Diagnóstico Avançado

### **Verificar Headers de Resposta:**
```bash
curl -I https://kestra.darwinai.com.br/ui/
```

### **Verificar Configuração do Traefik:**
No painel do Coolify, verifique se as labels do Traefik estão corretas:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.kestra.rule=Host(`kestra.darwinai.com.br`)"
  - "traefik.http.services.kestra.loadbalancer.server.port=8081"
```

## 🛠️ Soluções Alternativas

### **Solução 5: Configurar via Setup Page**

Se o Kestra v0.24.0 detectar que não há credenciais configuradas, ele pode mostrar uma Setup Page:

1. Acesse: https://kestra.darwinai.com.br
2. Se aparecer uma página de setup, configure as credenciais
3. Use:
   - **Username:** `leonardo@darwinai.com.br`
   - **Password:** `@Atjlc151523`

### **Solução 6: Reiniciar Container**

No painel do Coolify:
1. Vá para o projeto serena-qualifier
2. Encontre o container `kestra`
3. Clique em "Restart"
4. Aguarde a reinicialização
5. Teste novamente

### **Solução 7: Verificar Variáveis de Ambiente**

No painel do Coolify, verifique se estas variáveis estão definidas:

```bash
KESTRA_SERVER_BASICAUTH_USERNAME=leonardo@darwinai.com.br
KESTRA_SERVER_BASICAUTH_PASSWORD=@Atjlc151523
```

## 📞 Próximos Passos

### **Se nada funcionar:**

1. **Verificar logs do container kestra** no Coolify
2. **Verificar logs do Traefik** para problemas de proxy
3. **Testar com credenciais temporárias** via Setup Page
4. **Contatar suporte técnico** com logs completos

## ✅ Checklist de Verificação

- [ ] Limpar cache do navegador
- [ ] Testar em modo incógnito
- [ ] Testar em outro navegador
- [ ] Verificar variáveis no Coolify
- [ ] Reiniciar container kestra
- [ ] Verificar logs do container
- [ ] Testar Setup Page

---

## 🎯 Resumo

**As credenciais estão funcionando via API**, então o problema é específico do navegador. Tente as soluções acima na ordem apresentada, começando pela limpeza de cache.
