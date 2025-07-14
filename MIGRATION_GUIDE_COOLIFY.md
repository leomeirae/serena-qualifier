Diretiva de Migração para Produção (Coolify) - Para Serena-Coder
Documento: MIGRATION_GUIDE_COOLIFY.md
Status: Mandatório. Este documento é a diretiva única para reconfigurar o projeto serena-qualifier do ambiente de desenvolvimento local para o ambiente de produção hospedado no Coolify.

Olá, Serena-Coder.

Sua nova missão é migrar o projeto serena-qualifier para o ambiente de produção totalmente online. O desenvolvimento local foi concluído e agora todos os serviços estão hospedados em domínios públicos via Coolify.

Sua fonte de verdade para a arquitetura base continua sendo o MASTER_GUIDE_FINAL.md, mas esta diretiva de migração sobrepõe quaisquer configurações de URL e comunicação de rede nele contidas.

Contexto Geral da Migração
Até agora, os serviços se comunicavam via localhost ou nomes de contêineres Docker na rede local (ex: http://kestra-minimal:8080). Em produção, a comunicação acontece de duas formas:

Externa: Serviços de fora (como a API do WhatsApp ou o formulário do site) acessam seus serviços através de URLs públicos.

Interna: Seus próprios serviços (contêineres) se comunicam entre si usando os nomes dos serviços definidos no Docker, através da rede interna do Coolify.

URLs de Produção (Externos):

Interface Kestra (UI): https://kestra.darwinai.com.br/

API Principal: https://api.darwinai.com.br/

Webhook WhatsApp: https://kestrawebhook.darwinai.com.br/

Origem do Formulário (Cliente): https://www.saasia.com.br/

Seu objetivo é garantir que todos os pontos de comunicação do sistema sejam atualizados para usar esses novos endereços de forma correta. Siga o plano de ação abaixo, passo a passo.

Plano de Ação Detalhado
Passo 1: Entender e Configurar a Comunicação Externa (CORS)
Objetivo: Permitir que o servidor Kestra (kestra.darwinai.com.br) aceite requisições de API vindas de outros domínios, como o da sua API principal e do serviço de webhook.

Contexto: Navegadores e servidores aplicam uma política de segurança chamada CORS (Cross-Origin Resource Sharing). Por padrão, um domínio (ex: kestra.darwinai.com.br) rejeita chamadas de scripts vindos de outros domínios (ex: api.darwinai.com.br). Precisamos configurar o servidor Kestra para explicitamente permitir essas chamadas, adicionando cabeçalhos de resposta HTTP como Access-Control-Allow-Origin.

Action Plan:

Localize o arquivo de configuração do ambiente de produção: docker-compose-coolify.yml.

Inspecione a configuração do serviço kestra: Observe a seção de variáveis de ambiente (environment), especificamente a âncora YAML x-kestra-config.

Confirme a configuração de CORS: O arquivo docker-compose-coolify.yml já contém a configuração correta para permitir os domínios necessários. Sua tarefa é verificar e garantir que a configuração abaixo está ativa no ambiente Coolify.

# Dentro de x-kestra-config: &kestra-config
micronaut:
  server:
    # ... outras configs
    cors:
      enabled: true
      configurations:
        web:
          allowed-origins:
            - "https://kestra.darwinai.com.br"
            - "https://api.darwinai.com.br"
            - "https://kestrawebhook.darwinai.com.br"
          allowed-methods:
            - GET
            - POST
            - PUT
            - DELETE
            - OPTIONS
          allowed-headers:
            - "*"
          allow-credentials: true

Validação: Se essa configuração já existe em docker-compose-coolify.yml, nenhuma alteração de código é necessária. Apenas confirme seu entendimento de que o CORS está corretamente configurado para os serviços de produção.

Passo 2: Reconfigurar a Comunicação Interna entre Serviços
Objetivo: Garantir que os serviços dentro do Coolify (webhook_service, api_principal) se comuniquem com o Kestra da maneira correta.

Contexto: Este é o ponto mais crítico. Dentro da rede Docker do Coolify, os contêineres não devem usar os URLs públicos para falar entre si. Eles devem usar os nomes dos serviços definidos no docker-compose-coolify.yml. Isso é mais rápido, seguro e não depende da internet pública.

Action Plan:

Analise webhook_service.py:

Identifique a variável KESTRA_WEBHOOK_URL. Ela é construída a partir da variável de ambiente KESTRA_API_URL.

KESTRA_WEBHOOK_URL = f"{KESTRA_BASE_URL}/api/v1/executions/webhook/serena.production/2_ai_conversation_flow/converse_production_lead"

Analise docker-compose-coolify.yml:

No serviço webhook-service, a variável de ambiente KESTRA_API_URL está definida como "http://kestra:8081".

Esta configuração está CORRETA. kestra é o nome do serviço Kestra no Docker, e 8081 é a porta interna que ele expõe na rede coolify.

Validação: Confirme que esta URL interna não será alterada para a URL pública.

Analise api_principal.py:

Identifique as variáveis KESTRA_API_URL e WEBHOOK_SERVICE_URL.

No docker-compose-coolify.yml, a KESTRA_API_URL para este serviço também está definida como "http://kestra:8081".

No código de api_principal.py, a WEBHOOK_SERVICE_URL está definida como "http://webhook-service:8001".

Validação: Assim como no ponto anterior, essas configurações estão corretas para a comunicação interna. webhook-service é o nome do contêiner do webhook, e 8001 é sua porta interna. Confirme que essas URLs não serão alteradas.

Passo 3: Atualizar a Documentação e Pontos de Entrada
Objetivo: Garantir que todos os artefatos do projeto que são vistos por humanos ou por sistemas externos usem os URLs públicos corretos.

Contexto: Enquanto a comunicação interna usa nomes de serviço, qualquer exemplo de código, documentação ou configuração que um sistema externo (como a Meta/WhatsApp) usa deve ter o URL público completo.

Action Plan:

Configuração do Webhook do WhatsApp (Ação Externa):

O sistema externo do WhatsApp precisa saber para onde enviar as mensagens. O URL a ser configurado no painel da Meta for Developers é o URL público do seu serviço de webhook:

https://kestrawebhook.darwinai.com.br/webhook

Sua Tarefa: Documente que esta é a URL correta a ser usada na configuração externa do WhatsApp.

Revise MASTER_GUIDE_FINAL.md:

Procure por qualquer ocorrência de localhost, 127.0.0.1, ou qualquer URL que não seja de produção em exemplos de curl, diagramas ou descrições.

Ação: Substitua o URI do gatilho de exemplo na seção "Fluxo 1: Ativação do Lead" pela URL completa do webhook de produção: https://kestra.darwinai.com.br/api/v1/executions/webhook/serena.production/1_lead_activation_flow/activate_production_lead.

Ação: Atualize o diagrama da arquitetura e as descrições para refletir os novos URLs públicos.

Revise os Workflows Kestra (*.yml):

Inspecione as seções triggers. O tipo io.kestra.plugin.core.trigger.Webhook não precisa da URL completa, apenas da key. A URL é gerada pelo Kestra.

Inspecione as tarefas do tipo script ou http.Request para garantir que não existam URLs de desenvolvimento "hard-coded". A análise atual dos arquivos mostra que eles usam variáveis de ambiente e nomes de serviço internos, o que é a prática correta.

Validação: Confirme que os workflows não contêm URLs de localhost e estão prontos para produção.

Resumo da Missão
Confirme a Configuração de CORS: Verifique se a configuração de CORS no docker-compose-coolify.yml está correta e implantada, permitindo a comunicação entre os domínios de produção.

Valide a Comunicação Interna: Confirme que os serviços usam corretamente os nomes de serviço do Docker (kestra:8081, webhook-service:8001) para a comunicação interna. Não altere essas URLs internas para as públicas.

Atualize a Documentação: Modifique o MASTER_GUIDE_FINAL.md para refletir os novos URLs de produção nos exemplos e diagramas, garantindo que ele permaneça como a fonte canônica de informação.

Documente os Pontos de Entrada Externos: Deixe claro qual URL público deve ser usado para configurar o webhook do WhatsApp.

Após completar estas validações e atualizações, o sistema estará totalmente configurado para o ambiente de produção Coolify. Aguardo sua confirmação para prosseguir.