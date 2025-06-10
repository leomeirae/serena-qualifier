# Solução CORS para Serena Energia

Este documento contém instruções para implementar a solução CORS para o projeto Serena Energia.

## Arquivos Implementados

1. **api/submit-form.php**: Proxy PHP para intermediar a comunicação entre o frontend e o Google Apps Script
2. **.htaccess**: Configuração do servidor para lidar com requisições CORS
3. **src/utils/api.ts**: Atualizado para usar o proxy PHP em vez de comunicação direta com o Google Apps Script
4. **google-apps-script.js**: Código para ser implementado no Google Apps Script

## Passos para Implementação

### 1. Google Apps Script

1. Acesse o Google Apps Script em https://script.google.com/
2. Crie um novo projeto e cole o código do arquivo `google-apps-script.js`
3. Implante como aplicativo da web:
   - Execute como: Você
   - Quem tem acesso: Qualquer pessoa
4. Copie a URL do aplicativo implantado
5. **Importante**: Teste manualmente o endpoint usando o botão "Testar implantação" para garantir que o script está funcionando corretamente

### 2. Configuração de Variáveis de Ambiente

1. Crie ou atualize o arquivo `.env.local` na raiz do projeto com as seguintes variáveis:

   ```env
   NEXT_PUBLIC_GOOGLE_SHEETS_APPS_SCRIPT_URL=https://script.google.com/macros/s/AKfycbxRl7o0nVZ5bpfqZX_NxQYd7fV9p4LPCIwH7ubCKbF5ujKyX4wLwxBp4sFvz-23T3Bb/exec
   ```

2. **Importante**: Certifique-se de que todas as variáveis de ambiente usadas no frontend tenham o prefixo `NEXT_PUBLIC_`

### 3. Build do Next.js

1. Execute `npm run build` para gerar os arquivos estáticos
2. Verifique se os arquivos foram gerados corretamente na pasta `out/`
3. **Verificação**: Inspecione os arquivos em `out/_next/static/chunks` para confirmar que não há referências diretas ao Apps Script URL (deve usar a variável de ambiente)

### 4. Upload para o Hostinger

1. Faça upload de todos os arquivos da pasta `out/` para a raiz do seu domínio (geralmente `/public_html/`)
2. Crie uma pasta `api` na raiz do domínio (`/public_html/api/`)
3. Faça upload do arquivo `submit-form.php` para a pasta `api`
4. Faça upload do arquivo `.htaccess` para a raiz do domínio (`/public_html/`)
5. **Importante**: Verifique as permissões do arquivo PHP (deve ser 755) e da pasta `api` (deve ser 755)

### 4. Teste

1. Acesse seu site em `https://www.saasia.com.br`
2. Preencha o formulário e envie
3. Verifique se os dados foram adicionados à planilha do Google Sheets

## Solução de Problemas

Se encontrar problemas após a implementação:

1. **Verifique os logs do console** no navegador para identificar erros específicos

2. **Teste o proxy PHP diretamente**:
   - Crie um arquivo `test.html` com um formulário simples que envia para `/api/submit-form.php`
   - Verifique se o proxy está funcionando corretamente

3. **Adicione logs no PHP**:
   - Descomente a linha `file_put_contents('form_log.txt', ...)` no arquivo PHP
   - Verifique o arquivo `form_log.txt` para ver os dados recebidos

4. **Verifique as permissões**:
   - Certifique-se de que o arquivo PHP tem permissões de execução (geralmente 755)
   - Verifique se o PHP tem permissão para fazer requisições externas (allow_url_fopen e curl)

## Por que esta solução funciona

Esta solução resolve o problema de CORS contornando-o completamente:

1. O navegador faz requisições apenas para o mesmo domínio (`https://www.saasia.com.br`)
2. O servidor PHP lida com a comunicação com o Google Apps Script
3. Não há tentativa de configurar CORS no Google Apps Script, pois isso não funciona para requisições OPTIONS
4. O proxy PHP adiciona os cabeçalhos CORS necessários para permitir requisições do navegador
