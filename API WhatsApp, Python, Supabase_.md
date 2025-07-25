

# **Guia de Especialista: Processamento de Imagens do WhatsApp com Python e Armazenamento no Supabase**

## **Introdução**

Este relatório técnico detalha a arquitetura e a implementação de uma solução completa e automatizada para processar imagens recebidas através da API do WhatsApp Business e armazená-las de forma segura no Supabase. O objetivo é fornecer um guia de nível especialista que abrange desde a configuração inicial das plataformas até a construção de um backend robusto em Python, com foco em segurança, performance e escalabilidade.

A arquitetura proposta conecta a comunicação direta com o cliente, realizada via WhatsApp, a uma lógica de negócios personalizada, executada em um servidor Python. O fluxo de dados pode ser visualizado da seguinte forma: um usuário envia uma imagem para o número de WhatsApp da empresa; os servidores da Meta (empresa-mãe do WhatsApp) recebem essa imagem e disparam uma notificação em tempo real para um endpoint de webhook pré-configurado. Este webhook, implementado em Python, recebe a notificação, valida sua autenticidade e, em seguida, executa um processo de duas etapas para baixar a imagem. A imagem é então processada inteiramente em memória, sem a necessidade de armazenamento em disco temporário, e finalmente enviada para um bucket de armazenamento no Supabase. Adicionalmente, metadados relevantes sobre a imagem e a mensagem são salvos em uma tabela no banco de dados Postgres do Supabase, criando um sistema de gerenciamento de ativos digitais coeso.

Para implementar esta solução, serão utilizadas as seguintes tecnologias:

* **WhatsApp Business Cloud API:** A interface fornecida pela Meta para interagir programaticamente com a plataforma WhatsApp, permitindo o recebimento de mensagens e mídias.  
* **Python com FastAPI:** Um microframework web moderno e de alta performance para construir APIs e, neste caso, o servidor de webhook. Sua sintaxe baseada em type hints e suporte nativo para operações assíncronas o tornam ideal para tarefas de I/O, como chamadas de API.2  
* **Pillow (PIL Fork):** Uma biblioteca poderosa e essencial para manipulação e processamento de imagens em Python, utilizada para carregar, transformar e salvar imagens em memória.4  
* **Supabase:** Uma plataforma de backend como serviço de código aberto que oferece um banco de dados Postgres, autenticação, armazenamento de objetos e muito mais. Será utilizada tanto para o armazenamento de arquivos (Storage) quanto para a persistência de metadados (Database).6

Este guia foi projetado para capacitar desenvolvedores a construir não apenas um protótipo funcional, mas uma aplicação segura e pronta para produção, abordando as nuances e as melhores práticas de cada componente da arquitetura.

## **Seção 1: Arquitetura da Solução e Configuração de Pré-requisitos**

Antes de escrever qualquer linha de código, é fundamental estabelecer uma base sólida, configurando corretamente todas as plataformas e garantindo que as credenciais de acesso sejam gerenciadas de forma segura. Esta seção aborda a configuração passo a passo da Meta e do Supabase e introduz a prática essencial de gerenciamento de variáveis de ambiente.

### **1.1. Configuração da Plataforma Meta para Desenvolvedores**

A interação com a API do WhatsApp Business começa no portal de desenvolvedores da Meta. Este processo envolve a criação de uma aplicação que servirá como a ponte entre o seu serviço e a infraestrutura do WhatsApp.8

1. **Criação de uma Aplicação Meta:** A primeira etapa é registrar-se como desenvolvedor em developers.facebook.com e criar uma nova aplicação. Durante o processo de criação, é importante selecionar o tipo de aplicação "Business" (Negócios), pois isso alinha a aplicação com as ferramentas e permissões necessárias para a API do WhatsApp Business.9  
2. **Ativação do Produto WhatsApp:** Após a criação da aplicação, navegue até o painel de controle e adicione o produto "WhatsApp". Ao clicar em "Setup" (Configurar), a plataforma irá guiá-lo pelas etapas iniciais, incluindo a associação da sua aplicação a uma Conta Empresarial da Meta (Meta Business Account).9  
3. **Obtenção de Credenciais Essenciais:** O painel de configuração da API do WhatsApp (WhatsApp \> API Setup) é a fonte de várias credenciais críticas para o funcionamento da aplicação. É vital identificar e armazenar com segurança os seguintes itens:  
   * **ID do Número de Telefone (PHONE\_NUMBER\_ID):** Este é o identificador único para o número de telefone da sua empresa que será usado para enviar e receber mensagens. A Meta fornece um número de teste para desenvolvimento inicial.10  
   * **Token de Acesso (WHATSAPP\_ACCESS\_TOKEN):** A plataforma gera inicialmente um token de acesso temporário, válido por apenas 24 horas. Para aplicações em produção, este token é inadequado. É necessário navegar até as configurações da sua Conta Empresarial, criar um "Usuário do Sistema" com permissões de administrador e gerar um token de acesso permanente para ele. Este token será usado para autenticar todas as chamadas para a Graph API.8  
   * **Segredo da Aplicação (APP\_SECRET):** Encontrado nas configurações básicas da sua aplicação Meta (App Settings \> Basic), esta chave secreta é um pilar da segurança do webhook. Ela não é usada para fazer chamadas de API, mas sim para validar que as notificações recebidas no seu webhook são genuinamente da Meta, prevenindo ataques de falsificação.11  
4. **Configuração de um Número de Teste:** Para facilitar o desenvolvimento, a plataforma permite que você adicione e verifique seu próprio número de telefone como um destinatário de teste. Isso permite que você envie mensagens do seu telefone pessoal para o número do bot e veja as notificações chegando ao seu webhook.9

### **1.2. Configuração do Projeto Supabase**

O Supabase servirá como o destino final para as imagens processadas e seus metadados. A configuração correta do projeto, do bucket de armazenamento e das políticas de acesso é crucial.

1. **Criação de um Novo Projeto:** Acesse o painel do Supabase e crie um novo projeto. O processo é direto e provisionará um banco de dados Postgres completo e outros serviços associados.7  
2. **Obtenção das Chaves de API do Supabase:** Nas configurações do projeto (Project Settings \> API), você encontrará o **URL do Projeto** e as chaves de API. Para operações de backend, como as que serão realizadas pelo script Python, a chave service\_role é a mais indicada. Esta chave tem privilégios de administrador e pode contornar as políticas de segurança de nível de linha (Row Level Security \- RLS), o que é útil para operações de sistema, mas exige que ela seja mantida em absoluto segredo.6  
3. **Criação de um Bucket no Supabase Storage:** Navegue até a seção "Storage" e crie um novo bucket. Um nome descritivo, como whatsapp-images, é recomendado. Durante a criação, uma decisão crucial de segurança é desmarcar a opção que torna o bucket público. Um bucket privado garante que os arquivos não possam ser acessados diretamente por qualquer pessoa na internet. O acesso será controlado programaticamente, por exemplo, através da geração de URLs assinadas com tempo de expiração, ou diretamente pela aplicação de backend usando a chave service\_role.6  
4. **Configuração de Políticas de Acesso (RLS):** Embora a chave service\_role contorne as políticas de RLS, é uma boa prática entender como elas funcionam. As políticas de RLS no Supabase permitem definir regras granulares na tabela storage.objects para controlar quem pode ver, fazer upload, atualizar ou deletar arquivos com base em critérios como o ID do usuário autenticado. Para este guia, onde o backend atua como um administrador, a service\_role é suficiente, mas em cenários mais complexos com acesso de cliente, as RLS são indispensáveis.15

### **1.3. Gestão Segura de Credenciais com .env**

A prática de "hard-coding" — inserir credenciais como tokens de API e senhas diretamente no código-fonte — é uma das falhas de segurança mais comuns e perigosas. Se o código for compartilhado ou publicado em um repositório público como o GitHub, essas informações sensíveis ficam expostas a qualquer pessoa.17 A solução padrão da indústria é usar variáveis de ambiente.

A biblioteca python-dotenv simplifica esse processo em ambientes de desenvolvimento:

1. **Instalação:** Instale a biblioteca no seu ambiente virtual com pip install python-dotenv.17  
2. **Criação do arquivo .env:** Na raiz do seu projeto, crie um arquivo chamado .env. Este arquivo conterá os pares chave-valor de todas as suas credenciais.17  
3. **Criação do arquivo .gitignore:** Para garantir que o arquivo .env nunca seja rastreado pelo Git e enviado para o seu repositório, crie um arquivo .gitignore (se ainda não existir) e adicione a linha .env a ele.17  
4. **Carregamento no Script:** No início do seu script Python, importe e chame a função load\_dotenv() da biblioteca dotenv. Isso carregará as variáveis do arquivo .env para o ambiente do sistema operacional. A partir daí, elas podem ser acessadas de forma segura usando os.environ.get('NOME\_DA\_VARIAVEL').17

A segurança de uma aplicação não é uma etapa final, mas uma fundação construída desde o início. A arquitetura de segurança da Meta, que exige tokens e validação de webhooks, dita a necessidade de um gerenciamento de credenciais robusto. Negligenciar a gestão segura dessas chaves na etapa de configuração resulta em uma aplicação inerentemente vulnerável, independentemente da qualidade do código subsequente.12

### **Tabela 1: Checklist de Variáveis de Ambiente**

Para centralizar e organizar todas as credenciais necessárias, a tabela a seguir serve como um checklist para o seu arquivo .env.

| Nome da Variável no .env | Descrição | Origem |
| :---- | :---- | :---- |
| WHATSAPP\_ACCESS\_TOKEN | Token de Acesso Permanente para autenticar na Graph API. | Painel da Meta App (Usuário do Sistema) |
| PHONE\_NUMBER\_ID | ID do número de telefone do WhatsApp Business. | Painel da Meta App (WhatsApp \> API Setup) |
| WEBHOOK\_VERIFY\_TOKEN | Uma string secreta definida por você para a verificação do webhook. | Definido pelo Desenvolvedor |
| APP\_SECRET | Segredo da Aplicação Meta para validar payloads do webhook. | Painel da Meta App (Basic Settings) |
| SUPABASE\_URL | URL do seu projeto Supabase. | Painel do Supabase (Project Settings \> API) |
| SUPABASE\_KEY | Chave de API service\_role do seu projeto Supabase. | Painel do Supabase (Project Settings \> API) |

## **Seção 2: Construindo um Webhook Robusto com Python e FastAPI**

O webhook é o coração da nossa aplicação reativa; ele atua como o "ouvido" que aguarda as notificações da API do WhatsApp. Esta seção detalha a construção de um servidor de webhook seguro e eficiente usando FastAPI, um framework Python moderno escolhido por sua performance, validação de dados nativa e excelente suporte a operações assíncronas, que são ideais para lidar com chamadas de API externas.2

### **2.1. Estrutura do Projeto e Dependências**

Uma estrutura de projeto bem organizada e um gerenciamento de dependências claro são essenciais para a manutenibilidade e escalabilidade.

1. **Ambiente Virtual:** É uma prática recomendada isolar as dependências de cada projeto. Crie um ambiente virtual na pasta do seu projeto:  
   Bash  
   python \-m venv venv  
   source venv/bin/activate  \# No macOS/Linux  
   venv\\Scripts\\activate      \# No Windows

   8  
2. **Instalação de Bibliotecas:** Instale todas as bibliotecas necessárias com um único comando. Isso garante que todos os componentes estejam disponíveis para a aplicação:  
   Bash  
   pip install "fastapi\[all\]" "uvicorn\[standard\]" requests python-dotenv supabase Pillow

   Este comando instala o FastAPI com todas as suas dependências opcionais, o servidor ASGI Uvicorn, a biblioteca requests para fazer chamadas HTTP, python-dotenv para gerenciar as variáveis de ambiente, o cliente oficial do Supabase para Python e a biblioteca Pillow para processamento de imagem.3  
3. **Estrutura de Arquivos:** Uma estrutura simples para começar pode ser:  
   /whatsapp-processor

|-- /venv  
|-- main.py \# Arquivo principal da aplicação FastAPI  
|--.env \# Arquivo com as variáveis de ambiente (secreto)  
|--.gitignore \# Ignora o.env e outros arquivos  
|-- requirements.txt \# Lista de dependências  
\`\`\`

### **2.2. Implementação do Servidor FastAPI**

O servidor terá dois endpoints no mesmo caminho /webhook, um para requisições GET (verificação) e outro para POST (notificações).

* **Endpoint de Verificação (GET /webhook):** A Meta usa este endpoint uma única vez para confirmar que você controla o URL do webhook. Este processo é um "handshake" de segurança. O endpoint deve:  
  1. Receber os parâmetros de consulta hub.mode, hub.verify\_token e hub.challenge da requisição GET.  
  2. Verificar se hub.mode é igual a "subscribe" e se o hub.verify\_token recebido corresponde ao WEBHOOK\_VERIFY\_TOKEN que você definiu no seu arquivo .env e no painel da Meta.  
  3. Se a verificação for bem-sucedida, ele deve responder com o valor do hub.challenge e um status HTTP 200 OK. Caso contrário, deve retornar um erro 403 Forbidden.24  
* **Endpoint de Notificação (POST /webhook):** Este é o endpoint principal que receberá todas as notificações de eventos do WhatsApp, incluindo novas mensagens de imagem. Ele servirá como o ponto de partida para o fluxo de processamento.24

### **2.3. Validação de Assinatura: A Camada Crítica de Segurança**

Após o handshake inicial, o endpoint POST /webhook fica exposto na internet. Qualquer pessoa que conheça o URL poderia enviar dados falsificados para ele. Para evitar isso, a Meta assina cada payload de notificação com uma assinatura HMAC-SHA256 e a envia no cabeçalho X-Hub-Signature-256. Validar essa assinatura em cada requisição POST é crucial para garantir que a notificação é autêntica e não foi adulterada.11

A arquitetura do webhook do WhatsApp impõe uma separação clara entre a verificação de configuração (um GET único para provar a propriedade do endpoint) e a verificação de autenticidade contínua (um POST com assinatura para provar a origem de cada mensagem). Negligenciar a validação da assinatura deixa o webhook vulnerável a ataques de POST falsificados.

A implementação de uma função de validação envolve:

1. **Extrair a assinatura recebida:** O cabeçalho vem no formato sha256=\<assinatura\>. É preciso remover o prefixo sha256=.12  
2. **Gerar uma assinatura local:** Use os módulos hmac e hashlib do Python para criar um hash HMAC-SHA256 do corpo da requisição.  
3. **Usar o corpo bruto da requisição:** É fundamental usar os bytes brutos do corpo da requisição (await request.body()) para gerar o hash. Usar o JSON já processado (await request.json()) falhará, pois qualquer alteração na formatação (espaços, ordem das chaves) resultará em um hash diferente.12  
4. **Usar o APP\_SECRET:** O APP\_SECRET do seu arquivo .env é a chave secreta usada na função HMAC.  
5. **Comparação segura:** Compare a assinatura recebida com a assinatura gerada localmente usando hmac.compare\_digest(). Esta função é projetada para prevenir ataques de temporização, que poderiam permitir que um atacante adivinhasse a assinatura byte a byte.12

No FastAPI, essa lógica de validação pode ser encapsulada em uma função de dependência, garantindo que ela seja executada antes do código principal da rota POST. Se a validação falhar, a dependência pode levantar uma exceção HTTPException com status 403 Forbidden, interrompendo o processamento.

### **2.4. Expondo o Webhook Local com Ngrok**

Durante o desenvolvimento, seu servidor FastAPI está rodando localmente (ex: http://127.0.0.1:8000) e não é acessível pela internet. A Meta precisa de um URL público e com HTTPS para enviar as notificações do webhook. A ferramenta ngrok resolve esse problema criando um túnel seguro do seu ambiente local para um subdomínio público.

Para usá-lo:

1. Baixe e instale o ngrok.  
2. Inicie sua aplicação FastAPI com Uvicorn: uvicorn main:app \--reload.  
3. Em outro terminal, inicie o ngrok apontando para a porta da sua aplicação: ngrok http 8000\.  
4. O ngrok fornecerá um URL público com HTTPS (ex: https://aleatorio.ngrok-free.app). É este URL, seguido pelo caminho do seu webhook (ex: /webhook), que você deve inserir no campo "Callback URL" no painel de configuração do WhatsApp na plataforma Meta.3

## **Seção 3: O Processo de Download da Mídia da API do WhatsApp**

Obter o arquivo de imagem real da API do WhatsApp é um processo que frequentemente causa confusão, pois não se trata de um download direto. A Meta projetou um fluxo de duas etapas que é intencionalmente transitório e seguro, forçando os desenvolvedores a processar os dados rapidamente em vez de armazenar links permanentes para a mídia hospedada em seus servidores. Esta aparente fragilidade é, na verdade, uma característica de segurança.

### **3.1. Análise do Payload da Notificação de Imagem**

Quando um usuário envia uma imagem, o webhook recebe uma notificação POST com um corpo JSON detalhado. Compreender essa estrutura é o primeiro passo para extrair as informações necessárias.29

O payload contém uma estrutura aninhada. O caminho para o objeto da imagem é tipicamente entry.changes.value.messages.image. Dentro deste objeto, o campo mais importante é id, que contém o media\_id da imagem enviada. É crucial navegar por essa estrutura de forma segura, usando métodos como .get() em dicionários Python ou a validação de modelos do Pydantic no FastAPI para evitar KeyError se algum campo estiver ausente.

#### **Tabela 2: Estrutura do Payload de Notificação de Imagem (Simplificada)**

A tabela abaixo ilustra os campos essenciais dentro do payload JSON para uma mensagem de imagem.

| Caminho no JSON | Exemplo de Valor | Descrição |
| :---- | :---- | :---- |
| entry.changes.value.messages.from | "16505551234" | O número de telefone do usuário que enviou a mensagem. |
| entry.changes.value.messages.id | "wamid.HBg...QyNUE3" | O ID único da mensagem do WhatsApp (WAMID). |
| entry.changes.value.messages.timestamp | "1675871539" | O timestamp Unix de quando a mensagem foi recebida. |
| entry.changes.value.messages.type | "image" | O tipo de mensagem, neste caso, uma imagem. |
| entry.changes.value.messages.image.id | "1479537139650973" | **O ID da mídia. Este é o identificador necessário para baixar a imagem.** |
| entry.changes.value.messages.image.mime\_type | "image/jpeg" | O tipo MIME da imagem. |
| entry.changes.value.messages.image.caption | "Legenda da foto" | A legenda opcional que o usuário enviou com a imagem. |

### **3.2. Passo 1: Obtenção da URL de Download Temporária**

Com o media\_id em mãos, o primeiro passo é solicitar à API da Meta uma URL de download.

1. **Construção da Requisição:** Faça uma requisição HTTP GET para o endpoint da Graph API, que é formatado como https://graph.facebook.com/vXX.0/{MEDIA\_ID}, substituindo vXX.0 pela versão da API (ex: v19.0) e {MEDIA\_ID} pelo ID extraído do payload.31  
2. **Autenticação:** Esta requisição deve ser autenticada. Inclua o WHATSAPP\_ACCESS\_TOKEN no cabeçalho Authorization da requisição, prefixado com Bearer .31  
3. **Análise da Resposta:** Se a requisição for bem-sucedida, a API retornará um objeto JSON. Este objeto conterá uma chave url, cujo valor é a URL de download temporária para a mídia.31  
4. **A Validade de 5 Minutos:** É de extrema importância notar que esta URL é efêmera e expira em apenas 5 minutos. Isso significa que a aplicação deve prosseguir para o próximo passo imediatamente. Armazenar esta URL para uso posterior resultará em falha.10

### **3.3. Passo 2: Download do Binário da Imagem**

Com a URL temporária, o passo final é baixar os dados da imagem.

1. **Segunda Requisição:** Faça uma segunda requisição HTTP GET, desta vez para a url obtida no passo anterior.31  
2. **Autenticação Novamente:** Esta segunda requisição também deve ser autenticada. Inclua o mesmo WHATSAPP\_ACCESS\_TOKEN no cabeçalho Authorization.31 Não fazer isso resultará em um erro de acesso, mesmo que a URL seja válida.  
3. **Lidando com a Resposta:** A resposta a esta requisição não será um JSON. Se bem-sucedida, o corpo da resposta (response.content na biblioteca requests) conterá os dados binários brutos da imagem (por exemplo, os bytes que compõem o arquivo JPEG ou PNG).  
4. **O "Gotcha" do User-Agent:** Um problema comum e pouco documentado oficialmente é que esta segunda requisição de download pode falhar ou retornar um erro de "navegador não suportado" se não incluir um cabeçalho User-Agent. A API parece realizar uma verificação neste cabeçalho. Para contornar isso, é recomendado adicionar um User-Agent conhecido à requisição. Exemplos que funcionaram para outros desenvolvedores incluem WhatsApp/2.19.81 A, node, ou até mesmo o user-agent de um bot de busca como o do Google.32

A complexidade deste processo de duas etapas com um link de curta duração não é uma falha de design, mas uma política de segurança deliberada da Meta. Ela impede que os servidores do WhatsApp sejam usados como um CDN (Content Delivery Network) permanente e irrestrito, transferindo a responsabilidade pelo armazenamento de longo prazo para o desenvolvedor. Isso força uma arquitetura de "processamento imediato", que se alinha perfeitamente com o objetivo deste guia.

## **Seção 4: Processamento de Imagens em Memória com Pillow**

Uma vez que os dados binários da imagem são baixados, a abordagem mais eficiente e escalável é processá-los inteiramente na memória RAM, sem nunca salvar um arquivo temporário no disco do servidor. Esta prática elimina a latência de I/O (leitura/escrita em disco) e é fundamental para ambientes de execução modernos e sem estado (stateless), como contêineres Docker ou funções serverless, que podem ter sistemas de arquivos efêmeros ou de baixo desempenho.

### **4.1. Carregando a Imagem a partir de Bytes**

O desafio inicial é converter o fluxo de bytes brutos, obtido da resposta da API, em um objeto de imagem que a biblioteca Pillow possa manipular.

* **A Solução com io.BytesIO:** O módulo io do Python fornece a classe BytesIO, que permite tratar um buffer de bytes em memória como se fosse um arquivo binário. Isso cria um "arquivo virtual" na RAM.34  
* **Integração com Pillow:** A função Image.open() da biblioteca Pillow é versátil e pode aceitar não apenas um caminho de arquivo, mas também um objeto do tipo arquivo. Ao passar o objeto BytesIO para esta função, a imagem é decodificada e carregada diretamente da memória.34 O código para esta operação é conciso e elegante:  
  Python  
  import io  
  from PIL import Image

  \# Supondo que 'image\_bytes' contém os dados binários da imagem  
  image\_stream \= io.BytesIO(image\_bytes)  
  img \= Image.open(image\_stream)

### **4.2. Técnicas Comuns de Processamento de Imagem**

Com a imagem carregada em um objeto Image da Pillow, uma vasta gama de operações de processamento se torna disponível. Todas as manipulações são realizadas no objeto em memória.4

* **Obtenção de Metadados:** Acessar informações básicas da imagem é simples:  
  * img.size: Retorna uma tupla (largura, altura) em pixels.  
  * img.format: Retorna o formato original da imagem (ex: 'JPEG', 'PNG').  
  * img.mode: Retorna o modo de cor (ex: 'RGB', 'RGBA').  
* **Redimensionamento:** Para padronizar o tamanho das imagens, o método resize() é utilizado. Ele retorna um novo objeto de imagem com as dimensões especificadas.  
  Python  
  new\_size \= (800, 600)  
  resized\_img \= img.resize(new\_size)

* **Conversão de Formato e Qualidade:** É comum converter imagens para formatos mais eficientes como JPEG para economizar espaço de armazenamento. Ao salvar como JPEG, é possível controlar o nível de compressão através do parâmetro quality.  
  Python  
  \# Para converter uma imagem com transparência (RGBA) para JPEG,  
  \# é necessário primeiro convertê-la para o modo RGB.  
  if resized\_img.mode \== 'RGBA':  
      resized\_img \= resized\_img.convert('RGB')

* **Aplicação de Filtros:** O submódulo ImageEnhance permite aplicar diversos filtros. Por exemplo, para aumentar a nitidez:  
  Python  
  from PIL import ImageEnhance

  enhancer \= ImageEnhance.Sharpness(resized\_img)  
  sharpened\_img \= enhancer.enhance(2.0) \# Fator 2.0 para duplicar a nitidez

* **Adição de Marca d'Água:** O método paste() permite sobrepor uma imagem sobre outra. Isso é útil para adicionar um logo ou marca d'água. Se a marca d'água tiver um canal alfa (transparência), ela pode ser usada como máscara para uma colagem suave.

### **4.3. Salvando a Imagem Processada em Memória**

Após a conclusão de todas as manipulações, a imagem processada precisa ser codificada de volta para um formato de bytes, pronta para ser enviada ao Supabase. Novamente, o io.BytesIO é a ferramenta ideal.

1. Crie um novo buffer BytesIO vazio para servir como destino.  
2. Use o método save() do objeto de imagem da Pillow, passando o buffer como o destino e especificando o formato desejado (ex: 'JPEG').  
3. **Crucialmente**, após salvar, o "cursor" do buffer estará no final dos dados. Antes de ler o buffer para fazer o upload, é necessário reposicionar o cursor para o início usando output\_buffer.seek(0).

O código completo para esta etapa é:

Python

output\_buffer \= io.BytesIO()  
\# Supondo que 'processed\_img' é o objeto de imagem final  
processed\_img.save(output\_buffer, format\='JPEG', quality=85)  
output\_buffer.seek(0)

\# 'output\_buffer' agora contém os bytes da imagem JPEG processada e está pronto para upload.

A escolha pelo processamento em memória não é apenas uma otimização, mas um requisito arquitetônico que impacta diretamente a escalabilidade e portabilidade da solução, tornando-a mais rápida, limpa e perfeitamente adequada para a nuvem.

## **Seção 5: Upload e Armazenamento da Imagem no Supabase**

A etapa final do fluxo de trabalho é persistir a imagem processada na nuvem. O Supabase oferece uma solução integrada que combina armazenamento de objetos (Storage) e um banco de dados relacional (Postgres). Utilizar ambos em conjunto eleva a aplicação de um simples repositório de arquivos para um sistema de gerenciamento de ativos digitais estruturado e consultável.

### **5.1. Interagindo com o Supabase Storage**

A interação com os serviços do Supabase em Python é facilitada pela biblioteca cliente oficial, supabase-py.

* **Inicialização do Cliente:** O primeiro passo no script é criar uma instância do cliente Supabase, fornecendo o URL do projeto e a chave de API, que foram previamente armazenados no arquivo .env. Para operações de backend, a service\_role key é usada para obter privilégios de administrador.6  
  Python  
  from supabase import create\_client, Client

  supabase\_url \= os.environ.get("SUPABASE\_URL")  
  supabase\_key \= os.environ.get("SUPABASE\_KEY")  
  supabase: Client \= create\_client(supabase\_url, supabase\_key)

* **O Método upload():** A biblioteca fornece uma interface fluente para interagir com o Storage. O método upload() é usado para enviar arquivos para um bucket específico. A estrutura da chamada é supabase.storage.from\_('nome-do-bucket').upload(...).15

### **5.2. Realizando o Upload a partir da Memória**

Graças à abordagem de processamento em memória, o upload para o Supabase pode ser feito diretamente a partir do buffer de bytes, sem a necessidade de um arquivo intermediário.

* **Passando o Buffer:** O objeto io.BytesIO, que contém a imagem processada, é passado diretamente para o parâmetro file do método upload. A biblioteca cliente é capaz de lidar com este objeto do tipo arquivo.15  
* **Definindo o Caminho e o Tipo de Conteúdo:**  
  * **path:** É essencial fornecer um caminho único e lógico para cada arquivo dentro do bucket. Uma boa estratégia é usar informações da própria mensagem, como o número de telefone do remetente e o timestamp da mensagem, para criar uma estrutura de pastas e um nome de arquivo únicos. Isso evita colisões de nomes e organiza os arquivos de forma intuitiva. Exemplo: path=f"{sender\_phone\_number}/{message\_timestamp}.jpg".15  
  * **file\_options:** Este parâmetro permite especificar metadados importantes para o upload. O mais crítico é o content-type (tipo de conteúdo). Definir {'content-type': 'image/jpeg'} informa ao Supabase e aos navegadores como interpretar o arquivo corretamente. Sem isso, ele pode assumir um padrão incorreto, como text/html, causando problemas na exibição.16  
* **Tratamento de Resposta:** O método upload retorna uma resposta que deve ser verificada para confirmar se o upload foi bem-sucedido ou se ocorreu um erro, permitindo um tratamento de falhas adequado.

### **5.3. Prática Recomendada: Armazenando Metadados no Banco de Dados Supabase**

Um sistema robusto precisa de mais do que apenas os arquivos; ele precisa de dados *sobre* os arquivos. O verdadeiro poder do Supabase reside na integração nativa entre o Storage e o banco de dados Postgres. Após um upload bem-sucedido para o Storage, a prática recomendada é inserir um registro em uma tabela de metadados no banco de dados.7

* **Criação de uma Tabela de Metadados:** Primeiro, é necessário criar uma tabela no banco de dados Postgres do Supabase para armazenar as informações. Isso pode ser feito através da interface SQL do Supabase.

#### **Tabela 3: Esquema da Tabela image\_metadata**

O esquema a seguir transforma o projeto de um simples "repositório de arquivos" em uma aplicação de dados estruturada, permitindo consultas complexas e funcionalidades futuras.

| Nome da Coluna | Tipo de Dados | Descrição |
| :---- | :---- | :---- |
| id | uuid (primary key) | Identificador único para o registro, gerado automaticamente. |
| created\_at | timestamp with time zone | Data e hora do upload, com fuso horário. |
| wamid | text (unique) | O ID da mensagem do WhatsApp (WAMID), para evitar o processamento de duplicatas. |
| sender\_phone | text | Número de telefone do remetente da imagem. |
| storage\_path | text | O caminho completo do arquivo no Supabase Storage. Este campo é a "chave estrangeira" que liga o registro do banco de dados ao arquivo físico. |
| mime\_type | text | O tipo MIME do arquivo armazenado (ex: 'image/jpeg'). |
| file\_size\_kb | integer | O tamanho do arquivo processado em kilobytes. |
| original\_caption | text | A legenda que o usuário enviou com a imagem, se houver. |

* **Inserindo o Registro:** Após o upload bem-sucedido para o Storage, o script Python deve fazer uma segunda chamada ao Supabase, desta vez para inserir um registro na tabela image\_metadata com todos os dados coletados durante o processo.  
  Python  
  metadata\_to\_insert \= {  
      "wamid": wamid,  
      "sender\_phone": sender\_phone,  
      "storage\_path": storage\_path,  
      "mime\_type": "image/jpeg",  
      "file\_size\_kb": file\_size\_kb,  
      "original\_caption": caption  
  }  
  data, count \= supabase.table('image\_metadata').insert(metadata\_to\_insert).execute()

  39

Esta abordagem arquitetônica, usando o Storage para blobs de dados e o Database para metadados estruturados, é o que torna a solução verdadeiramente poderosa, consultável e escalável.

## **Seção 6: Código Completo, Testes e Próximos Passos**

Esta seção final consolida todos os conceitos discutidos em um script funcional e coeso, além de fornecer orientações essenciais para levar o projeto do desenvolvimento para um ambiente de produção.

### **6.1. O Script Completo main.py**

A seguir, um exemplo completo e comentado do arquivo main.py que integra a aplicação FastAPI, a validação do webhook, o download da mídia, o processamento com Pillow e o upload para o Supabase.

Python

import os  
import hmac  
import hashlib  
import io  
import logging  
from fastapi import FastAPI, Request, Response, HTTPException, Header, Depends  
from dotenv import load\_dotenv  
import requests  
from PIL import Image, ImageEnhance  
from supabase import create\_client, Client

\# \--- Configuração Inicial \---  
\# Carrega as variáveis de ambiente do arquivo.env  
load\_dotenv()

\# Configuração do logging  
logging.basicConfig(level=logging.INFO, format\='%(asctime)s \- %(levelname)s \- %(message)s')

\# \--- Credenciais e Constantes \---  
WHATSAPP\_ACCESS\_TOKEN \= os.environ.get("WHATSAPP\_ACCESS\_TOKEN")  
PHONE\_NUMBER\_ID \= os.environ.get("PHONE\_NUMBER\_ID")  
WEBHOOK\_VERIFY\_TOKEN \= os.environ.get("WEBHOOK\_VERIFY\_TOKEN")  
APP\_SECRET \= os.environ.get("APP\_SECRET")  
SUPABASE\_URL \= os.environ.get("SUPABASE\_URL")  
SUPABASE\_KEY \= os.environ.get("SUPABASE\_KEY")

\# \--- Inicialização de Clientes \---  
app \= FastAPI()  
try:  
    supabase: Client \= create\_client(SUPABASE\_URL, SUPABASE\_KEY)  
    logging.info("Cliente Supabase inicializado com sucesso.")  
except Exception as e:  
    logging.error(f"Falha ao inicializar o cliente Supabase: {e}")  
    supabase \= None

\# \--- Funções de Segurança do Webhook \---  
async def verify\_signature(request: Request, x\_hub\_signature\_256: str \= Header(None)):  
    """Verifica a assinatura HMAC-SHA256 da requisição do webhook."""  
    if not x\_hub\_signature\_256:  
        logging.warning("Validação de assinatura falhou: Cabeçalho X-Hub-Signature-256 ausente.")  
        raise HTTPException(status\_code=403, detail="Assinatura ausente.")

    if not APP\_SECRET:  
        logging.error("Validação de assinatura falhou: APP\_SECRET não está configurado.")  
        raise HTTPException(status\_code=500, detail="Configuração de segurança incompleta.")

    signature \= x\_hub\_signature\_256.split("=")  
    request\_body \= await request.body()  
      
    expected\_signature \= hmac.new(  
        APP\_SECRET.encode('utf-8'),  
        request\_body,  
        hashlib.sha256  
    ).hexdigest()

    if not hmac.compare\_digest(expected\_signature, signature):  
        logging.warning("Validação de assinatura falhou: Assinaturas não correspondem.")  
        raise HTTPException(status\_code=403, detail="Assinatura inválida.")  
    logging.info("Assinatura do webhook validada com sucesso.")

\# \--- Endpoints do Webhook \---  
@app.get("/webhook")  
async def verify\_webhook\_endpoint(request: Request):  
    """Lida com a verificação do webhook da Meta (handshake)."""  
    mode \= request.query\_params.get("hub.mode")  
    token \= request.query\_params.get("hub.verify\_token")  
    challenge \= request.query\_params.get("hub.challenge")

    if mode \== "subscribe" and token \== WEBHOOK\_VERIFY\_TOKEN:  
        logging.info("WEBHOOK VERIFICADO com sucesso.")  
        return Response(content=challenge, status\_code=200)  
    else:  
        logging.error("Falha na verificação do WEBHOOK.")  
        raise HTTPException(status\_code=403, detail="Falha na verificação.")

@app.post("/webhook", dependencies=)  
async def receive\_webhook\_notification(request: Request):  
    """Recebe, processa e armazena imagens de notificações do WhatsApp."""  
    data \= await request.json()  
    logging.info(f"Payload do webhook recebido: {data}")

    try:  
        changes \= data.get("entry", \[{}\]).get("changes", \[{}\])  
        value \= changes.get("value", {})  
        message \= value.get("messages", \[{}\])

        if message.get("type") \== "image":  
            await process\_image\_message(message)  
        else:  
            logging.info(f"Mensagem recebida não é do tipo imagem: {message.get('type')}")

    except (IndexError, KeyError) as e:  
        logging.warning(f"Payload do webhook com estrutura inesperada: {e}")  
        pass \# Ignora payloads que não são de mensagens de imagem

    return Response(status\_code=200)

\# \--- Lógica de Processamento de Imagem \---  
async def process\_image\_message(message: dict):  
    """Processa uma mensagem do tipo imagem."""  
    media\_id \= message.get("image", {}).get("id")  
    sender\_phone \= message.get("from")  
    wamid \= message.get("id")  
    caption \= message.get("image", {}).get("caption")  
    timestamp \= message.get("timestamp")

    if not all(\[media\_id, sender\_phone, wamid, timestamp\]):  
        logging.error("Dados da mensagem de imagem incompletos.")  
        return

    \# 1\. Obter URL de download da mídia  
    media\_url\_data \= get\_media\_url(media\_id)  
    if not media\_url\_data:  
        return

    \# 2\. Baixar o binário da imagem  
    image\_bytes \= download\_media(media\_url\_data.get("url"))  
    if not image\_bytes:  
        return

    \# 3\. Processar a imagem em memória  
    processed\_image\_buffer, original\_size \= process\_image\_in\_memory(image\_bytes)  
      
    \# 4\. Fazer upload para o Supabase Storage  
    storage\_path \= f"images/{sender\_phone}/{timestamp}.jpg"  
    upload\_to\_supabase(processed\_image\_buffer, storage\_path)

    \# 5\. Salvar metadados no banco de dados Supabase  
    file\_size\_kb \= len(processed\_image\_buffer.getvalue()) // 1024  
    save\_metadata\_to\_supabase(wamid, sender\_phone, storage\_path, caption, file\_size\_kb)

def get\_media\_url(media\_id: str) \-\> dict:  
    """Obtém a URL de download temporária da mídia."""  
    url \= f"https://graph.facebook.com/v19.0/{media\_id}/"  
    headers \= {"Authorization": f"Bearer {WHATSAPP\_ACCESS\_TOKEN}"}  
    try:  
        response \= requests.get(url, headers=headers)  
        response.raise\_for\_status()  
        logging.info(f"URL da mídia obtida com sucesso para o ID: {media\_id}")  
        return response.json()  
    except requests.exceptions.RequestException as e:  
        logging.error(f"Erro ao obter URL da mídia para o ID {media\_id}: {e}")  
        return None

def download\_media(media\_url: str) \-\> bytes:  
    """Baixa os dados binários da mídia."""  
    headers \= {  
        "Authorization": f"Bearer {WHATSAPP\_ACCESS\_TOKEN}",  
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"  
    }  
    try:  
        response \= requests.get(media\_url, headers=headers)  
        response.raise\_for\_status()  
        logging.info("Download da mídia realizado com sucesso.")  
        return response.content  
    except requests.exceptions.RequestException as e:  
        logging.error(f"Erro ao baixar mídia da URL {media\_url}: {e}")  
        return None

def process\_image\_in\_memory(image\_bytes: bytes) \-\> (io.BytesIO, tuple):  
    """Carrega, processa e salva a imagem em um buffer de memória."""  
    with Image.open(io.BytesIO(image\_bytes)) as img:  
        original\_size \= img.size  
        logging.info(f"Imagem carregada em memória. Tamanho original: {original\_size}")  
          
        \# Exemplo de processamento: redimensionar e aplicar um filtro de nitidez  
        img\_resized \= img.resize((1024, 768))  
        enhancer \= ImageEnhance.Sharpness(img\_resized)  
        img\_processed \= enhancer.enhance(1.5)

        \# Converter para RGB se for RGBA (necessário para salvar como JPEG)  
        if img\_processed.mode \== 'RGBA':  
            img\_processed \= img\_processed.convert('RGB')

        output\_buffer \= io.BytesIO()  
        img\_processed.save(output\_buffer, format\='JPEG', quality=85)  
        output\_buffer.seek(0)  
        logging.info("Imagem processada e salva em buffer de memória.")  
        return output\_buffer, original\_size

def upload\_to\_supabase(buffer: io.BytesIO, path: str):  
    """Faz upload do buffer de imagem para o Supabase Storage."""  
    if not supabase:  
        logging.error("Upload para Supabase falhou: cliente não inicializado.")  
        return  
    try:  
        supabase.storage.from\_("whatsapp-images").upload(  
            file=buffer,  
            path=path,  
            file\_options={"content-type": "image/jpeg", "upsert": "true"}  
        )  
        logging.info(f"Upload para Supabase Storage bem-sucedido no caminho: {path}")  
    except Exception as e:  
        logging.error(f"Erro no upload para o Supabase Storage: {e}")

def save\_metadata\_to\_supabase(wamid: str, sender: str, path: str, caption: str, size: int):  
    """Salva os metadados da imagem no banco de dados Supabase."""  
    if not supabase:  
        logging.error("Salvamento de metadados no Supabase falhou: cliente não inicializado.")  
        return  
    try:  
        metadata \= {  
            "wamid": wamid,  
            "sender\_phone": sender,  
            "storage\_path": path,  
            "original\_caption": caption,  
            "file\_size\_kb": size,  
            "mime\_type": "image/jpeg"  
        }  
        supabase.table("image\_metadata").insert(metadata).execute()  
        logging.info(f"Metadados salvos no Supabase para WAMID: {wamid}")  
    except Exception as e:  
        logging.error(f"Erro ao salvar metadados no Supabase: {e}")

### **6.2. Arquivos de Configuração do Projeto**

Para garantir a reprodutibilidade e facilitar a configuração por outros desenvolvedores, o projeto deve incluir os seguintes arquivos:

* **requirements.txt:** Este arquivo lista todas as dependências do Python com suas versões exatas. Pode ser gerado com o comando pip freeze \> requirements.txt.  
  fastapi==...  
  uvicorn==...  
  requests==...  
  python-dotenv==...  
  supabase==...  
  Pillow==...

...  
\`\`\`

* **.env.example:** Um arquivo de exemplo que serve como um modelo para o arquivo .env real. Ele lista todas as variáveis de ambiente necessárias, mas com valores de placeholder. Isso orienta o usuário sobre quais credenciais preencher sem expor nenhum segredo no repositório.  
  WHATSAPP\_ACCESS\_TOKEN="SEU\_TOKEN\_DE\_ACESSO\_AQUI"  
  PHONE\_NUMBER\_ID="SEU\_ID\_DE\_NUMERO\_DE\_TELEFONE\_AQUI"  
  WEBHOOK\_VERIFY\_TOKEN="SUA\_STRING\_SECRETA\_DE\_VERIFICACAO\_AQUI"  
  APP\_SECRET="SEU\_SEGREDO\_DE\_APLICACAO\_AQUI"  
  SUPABASE\_URL="URL\_DO\_SEU\_PROJETO\_SUPABASE\_AQUI"  
  SUPABASE\_KEY="SUA\_CHAVE\_SERVICE\_ROLE\_DO\_SUPABASE\_AQUI"

### **6.3. Considerações para Produção e Melhorias**

A solução apresentada é funcional, mas para um ambiente de produção robusto, algumas melhorias são fortemente recomendadas:

* **Tratamento de Erros Robusto:** O código deve incluir blocos try...except mais granulares para capturar e registrar falhas específicas em cada etapa do processo (download, processamento, upload). Isso facilita a depuração e permite a implementação de lógicas de repetição (retry).  
* **Filas de Tarefas Assíncronas:** Esta é a melhoria mais crítica para a produção. Realizar todo o processo de download e upload de forma síncrona dentro da requisição do webhook é arriscado. A API do WhatsApp espera uma resposta rápida (200 OK) do webhook. Se o processamento demorar muito (devido a uma imagem grande ou latência de rede), a Meta pode considerar que o webhook falhou e parar de enviar notificações. A arquitetura ideal é:  
  1. O webhook recebe a notificação e valida a assinatura.  
  2. Ele imediatamente coloca uma "tarefa" (contendo o media\_id e outros metadados) em uma fila de tarefas (usando sistemas como Celery com Redis/RabbitMQ ou Dramatiq).  
  3. O webhook responde 200 OK para a Meta.  
  4. Um processo worker separado, rodando em segundo plano, pega as tarefas da fila e executa o longo processo de download, processamento e upload de forma assíncrona.  
* **Deployment:** Para implantar a aplicação FastAPI, recomenda-se o uso de contêineres Docker para encapsular a aplicação e suas dependências. Esses contêineres podem ser implantados em serviços de nuvem como Heroku, Render, AWS (ECS, Fargate) ou Google Cloud (Cloud Run).  
* **Rotação de Tokens:** Como prática de segurança, os tokens de acesso, mesmo os permanentes, devem ser rotacionados periodicamente. Isso limita a janela de oportunidade para um atacante caso um token seja comprometido.18

Ao seguir este guia e implementar as melhorias sugeridas, os desenvolvedores podem construir uma solução de processamento de imagens via WhatsApp que não é apenas funcional, mas também segura, eficiente e pronta para escalar.

#### **Works cited**

1. Messages \- WhatsApp Cloud API \- Meta for Developers \- Facebook, accessed July 25, 2025, [https://developers.facebook.com/docs/whatsapp/cloud-api/reference/messages/](https://developers.facebook.com/docs/whatsapp/cloud-api/reference/messages/)  
2. Unable to send WhatsApp messages using FastAPI and requests in Python \- Stack Overflow, accessed July 25, 2025, [https://stackoverflow.com/questions/77844137/unable-to-send-whatsapp-messages-using-fastapi-and-requests-in-python](https://stackoverflow.com/questions/77844137/unable-to-send-whatsapp-messages-using-fastapi-and-requests-in-python)  
3. Build a Secure Twilio Webhook with Python and FastAPI, accessed July 25, 2025, [https://www.twilio.com/en-us/blog/build-secure-twilio-webhook-python-fastapi](https://www.twilio.com/en-us/blog/build-secure-twilio-webhook-python-fastapi)  
4. Image Processing With the Python Pillow Library, accessed July 25, 2025, [https://realpython.com/image-processing-with-the-python-pillow-library/](https://realpython.com/image-processing-with-the-python-pillow-library/)  
5. Pillow in Python: How to Process Images? | by Adrian Boguszewski | Medium, accessed July 25, 2025, [https://medium.com/@adrianboguszewski/a-quick-overview-of-pillow-in-python-an-essential-library-for-image-processing-96b8fc0e7c20](https://medium.com/@adrianboguszewski/a-quick-overview-of-pillow-in-python-an-essential-library-for-image-processing-96b8fc0e7c20)  
6. Efficiently import files from Supabase in Python \- Transloadit, accessed July 25, 2025, [https://transloadit.com/devtips/efficiently-import-files-from-supabase-in-python/](https://transloadit.com/devtips/efficiently-import-files-from-supabase-in-python/)  
7. Supabase Docs, accessed July 25, 2025, [https://supabase.com/docs](https://supabase.com/docs)  
8. Sending Messages with WhatsApp in Your Python Applications \- Meta for Developers, accessed July 25, 2025, [https://developers.facebook.com/blog/post/2022/10/24/sending-messages-with-whatsapp-in-your-python-applications/](https://developers.facebook.com/blog/post/2022/10/24/sending-messages-with-whatsapp-in-your-python-applications/)  
9. Automate Messages Using WhatsApp Business API & Flask \- Part 1 \- Pragnakalp Techlabs, accessed July 25, 2025, [https://www.pragnakalp.com/automate-messages-using-whatsapp-business-api-flask-part-1/](https://www.pragnakalp.com/automate-messages-using-whatsapp-business-api-flask-part-1/)  
10. Sending WhatsApp Media Messages From An App, accessed July 25, 2025, [https://business.whatsapp.com/blog/media-messages-via-app](https://business.whatsapp.com/blog/media-messages-via-app)  
11. python-whatsapp-bot/README.md at main \- GitHub, accessed July 25, 2025, [https://github.com/daveebbelaar/python-whatsapp-bot/blob/main/README.md](https://github.com/daveebbelaar/python-whatsapp-bot/blob/main/README.md)  
12. python \- Validate X-Hub-Signature-256 meta / whatsapp webhook ..., accessed July 25, 2025, [https://stackoverflow.com/questions/75422064/validate-x-hub-signature-256-meta-whatsapp-webhook-request](https://stackoverflow.com/questions/75422064/validate-x-hub-signature-256-meta-whatsapp-webhook-request)  
13. Python: Initializing | Supabase Docs, accessed July 25, 2025, [https://supabase.com/docs/reference/python/initializing](https://supabase.com/docs/reference/python/initializing)  
14. Storage | Supabase Docs, accessed July 25, 2025, [https://supabase.com/docs/guides/storage](https://supabase.com/docs/guides/storage)  
15. Python: Upload a file | Supabase Docs, accessed July 25, 2025, [https://supabase.com/docs/reference/python/storage-from-upload](https://supabase.com/docs/reference/python/storage-from-upload)  
16. Standard Uploads | Supabase Docs, accessed July 25, 2025, [https://supabase.com/docs/guides/storage/uploads/standard-uploads](https://supabase.com/docs/guides/storage/uploads/standard-uploads)  
17. Storing Environment Variables and API Keys in Python | by Alwin Raju | Medium, accessed July 25, 2025, [https://medium.com/@alwinraju/%EF%B8%8F-storing-environment-variables-and-api-keys-in-python-475144b2f098](https://medium.com/@alwinraju/%EF%B8%8F-storing-environment-variables-and-api-keys-in-python-475144b2f098)  
18. Best Practices for API Key Safety | OpenAI Help Center, accessed July 25, 2025, [https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety)  
19. 8 tips for securely using API keys \- Streamlit Blog, accessed July 25, 2025, [https://blog.streamlit.io/8-tips-for-securely-using-api-keys/](https://blog.streamlit.io/8-tips-for-securely-using-api-keys/)  
20. Tech Tip Tuesday \- Store API keys in python \- YouTube, accessed July 25, 2025, [https://www.youtube.com/shorts/HbkTVPGcB3w](https://www.youtube.com/shorts/HbkTVPGcB3w)  
21. Python \- Hiding the API Key in Environment Variables \- Network Direction, accessed July 25, 2025, [https://networkdirection.net/python/resources/env-variable/](https://networkdirection.net/python/resources/env-variable/)  
22. OpenAPI Webhooks \- FastAPI, accessed July 25, 2025, [https://fastapi.tiangolo.com/advanced/openapi-webhooks/](https://fastapi.tiangolo.com/advanced/openapi-webhooks/)  
23. How to Receive WhatsApp Messages in Python Using Flask and Twilio, accessed July 25, 2025, [https://www.twilio.com/en-us/blog/receive-whatsapp-messages-python-flask-twilio](https://www.twilio.com/en-us/blog/receive-whatsapp-messages-python-flask-twilio)  
24. gustavz/whatsbot: python flask app serving as webhook for ... \- GitHub, accessed July 25, 2025, [https://github.com/gustavz/whatsbot](https://github.com/gustavz/whatsbot)  
25. How to Configure and Validate WhatsApp Webhooks for Real-Time Notifications Using Power Automate, C\#, Java, and Python | by Zain Zulfiqar | Medium, accessed July 25, 2025, [https://medium.com/@zainzulfiqarmaknojia/how-to-configure-and-validate-whatsapp-webhooks-for-real-time-notifications-using-power-automate-e1f5ecd7ab99](https://medium.com/@zainzulfiqarmaknojia/how-to-configure-and-validate-whatsapp-webhooks-for-real-time-notifications-using-power-automate-e1f5ecd7ab99)  
26. How to receive an incoming message to webhook whatsapp business app \- n8n Community, accessed July 25, 2025, [https://community.n8n.io/t/how-to-receive-an-incoming-message-to-webhook-whatsapp-business-app/18551](https://community.n8n.io/t/how-to-receive-an-incoming-message-to-webhook-whatsapp-business-app/18551)  
27. how to authenticate whatsapp webhook post request to my server \- Meta for Developers, accessed July 25, 2025, [https://developers.facebook.com/community/threads/611570411016094/](https://developers.facebook.com/community/threads/611570411016094/)  
28. How to verify a webhook request sign | Meta Community Forums \- 1171086, accessed July 25, 2025, [https://communityforums.atmeta.com/discussions/dev-general/how-to-verify-a-webhook-request-sign/1171086](https://communityforums.atmeta.com/discussions/dev-general/how-to-verify-a-webhook-request-sign/1171086)  
29. Downloading Media using Whatsapp's Cloud API Webhook and uploading it to AWS S3 buckets through NodeJS | by Shreyas Sreedhar | Medium, accessed July 25, 2025, [https://medium.com/@shreyas.sreedhar/downloading-media-using-whatsapps-cloud-api-webhooks-and-uploading-it-to-aws-s3-bucket-via-nodejs-07c5cbae896f](https://medium.com/@shreyas.sreedhar/downloading-media-using-whatsapps-cloud-api-webhooks-and-uploading-it-to-aws-s3-bucket-via-nodejs-07c5cbae896f)  
30. Received Message with Image | WhatsApp On-Premises API (deprecated) \- Postman, accessed July 25, 2025, [https://www.postman.com/meta/whatsapp-business-platform/request/tysqb9i/received-message-with-image](https://www.postman.com/meta/whatsapp-business-platform/request/tysqb9i/received-message-with-image)  
31. Media \- WhatsApp Cloud API \- Meta for Developers \- Facebook, accessed July 25, 2025, [https://developers.facebook.com/docs/whatsapp/cloud-api/reference/media/](https://developers.facebook.com/docs/whatsapp/cloud-api/reference/media/)  
32. How to download media files in WhatsApp API which send users? \- Stack Overflow, accessed July 25, 2025, [https://stackoverflow.com/questions/67881798/how-to-download-media-files-in-whatsapp-api-which-send-users](https://stackoverflow.com/questions/67881798/how-to-download-media-files-in-whatsapp-api-which-send-users)  
33. Cannot Download Media from WhatsApp Business API \- Working with Postman and cURL \- Not working with NodeJS Fetch, accessed July 25, 2025, [https://stackoverflow.com/questions/77846881/cannot-download-media-from-whatsapp-business-api-working-with-postman-and-curl](https://stackoverflow.com/questions/77846881/cannot-download-media-from-whatsapp-business-api-working-with-postman-and-curl)  
34. image \- Python Imaging: load jpeg from memory \- Stack Overflow, accessed July 25, 2025, [https://stackoverflow.com/questions/8821259/python-imaging-load-jpeg-from-memory](https://stackoverflow.com/questions/8821259/python-imaging-load-jpeg-from-memory)  
35. Image module \- Pillow (PIL Fork) 11.3.0 documentation, accessed July 25, 2025, [https://pillow.readthedocs.io/en/stable/reference/Image.html](https://pillow.readthedocs.io/en/stable/reference/Image.html)  
36. Image Processing using Pillow \- CoderzColumn, accessed July 25, 2025, [https://coderzcolumn.com/tutorials/python/pillow](https://coderzcolumn.com/tutorials/python/pillow)  
37. Image Processing in Python with Pillow \- Auth0, accessed July 25, 2025, [https://auth0.com/blog/image-processing-in-python-with-pillow/](https://auth0.com/blog/image-processing-in-python-with-pillow/)  
38. supabase/storage-py \- GitHub, accessed July 25, 2025, [https://github.com/supabase/storage-py](https://github.com/supabase/storage-py)  
39. Python: Fetch data | Supabase Docs, accessed July 25, 2025, [https://supabase.com/docs/reference/python/select](https://supabase.com/docs/reference/python/select)