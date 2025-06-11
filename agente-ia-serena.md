Decidimos que, para lidar com a complexidade da interação com a IA (prompts, RAG, leitura de imagens, chamadas a APIs externas), a melhor abordagem é criar um serviço de agente de IA mais robusto e integrá-lo ao nosso workflow Kestra ai-conversation-activation. Vamos usar Python para isso, e gostaríamos de explorar o uso do framework LangChain para nos ajudar a estruturar esse agente.

Aqui está o passo a passo do que precisamos que você nos ajude a desenvolver ou configurar:

Fase 1: Configuração do Ambiente e Dependências
Instalar LangChain e Dependências Relacionadas:
Adicionar langchain, langchain-openai (para interagir com a OpenAI), e potencialmente langchain-community (para outros componentes) ao nosso arquivo requirements.txt.
Se formos usar um Vector Store para RAG (e.g., FAISS, ChromaDB), adicionar a dependência correspondente (e.g., faiss-cpu ou chromadb).
Garantir que nossa imagem Docker serena/kestra-python-runner:latest (ou uma nova versão dela) tenha essas bibliotecas instaladas.
Fase 2: Estrutura do Novo Serviço de Agente de IA
Criar serena_agent.py
Este arquivo será o coração do nosso novo agente. Ele conterá uma classe principal, por exemplo, SerenaAIAgent.

Inicialização (__init__)
Carregar variáveis de ambiente (como OPENAI_API_KEY).
Inicializar o cliente LLM (e.g., ChatOpenAI(model="gpt-4o-mini", ...)).
Potencialmente, carregar ou inicializar outros componentes que serão usados consistentemente (como um Vector Store para RAG, se aplicável).
Fase 3: Implementação das Capacidades do Agente dentro de serena_agent.py
Gerenciamento de Conversa:
O agente deve interagir com nosso utils.conversation_manager.py para:

Obter o histórico da conversa para um phone_number.
Adicionar novas mensagens (do usuário e da IA) ao histórico.
Obter/atualizar dados de qualificação acumulados do lead.
Classificação de Intenção:
Criar um método (e.g., classify_intent(self, user_message: str, conversation_history: list) -> dict):
Utilizar PromptTemplate do LangChain para criar um prompt de classificação robusto.
Formatar o histórico da conversa e a mensagem do usuário para o LLM.
Chamar o LLM para obter a intenção e a confiança.
Considerar o uso de OutputParser do LangChain para estruturar a saída do LLM.
Extração de Dados:
Criar um método (e.g., extract_data(self, user_message: str, conversation_history: list, data_type_to_extract: str) -> dict):
Usar PromptTemplate para extração de entidades específicas (cidade, valor da conta, etc.).
Chamar o LLM e usar OutputParser para obter os dados extraídos.
Lógica de RAG (Retrieval Augmented Generation):
Configurar um Vector Store:
Carregar documentos relevantes (FAQs, informações de planos detalhadas) da pasta knowledge_base/ usando DocumentLoaders do LangChain.
Processar (dividir) os documentos usando TextSplitters.
Criar embeddings (e.g., com OpenAIEmbeddings) e armazená-los em um Vector Store (e.g., FAISS, Chroma).
Criar um Retriever: Configurar um retriever a partir do Vector Store.
Montar uma Cadeia RAG (RetrievalQA ou customizada):
Um método (e.g., answer_general_question_with_rag(self, user_question: str, conversation_history: list) -> str).
O método usará o retriever para buscar documentos relevantes.
Construirá um prompt que inclui a pergunta, o histórico e os documentos recuperados.
Chamará o LLM para gerar a resposta.
Definição de Ferramentas (Tools) para o Agente:
Abstrair nossas funcionalidades existentes como "ferramentas" que o agente LangChain pode usar:

Ferramenta SerenaAPI:
Funções para check_city_coverage(city, state) e get_plans_by_city(city, state, utility_id=None).
O agente decidirá quando chamar essas funções com base na conversa.
Ferramenta OCRProcessor:
Função para extract_invoice_data(file_path_or_url: str).
O agente precisará de um mecanismo para receber o arquivo (talvez o Kestra baixe o arquivo de uma URL fornecida pelo webhook do WhatsApp e passe o caminho para o agente).
Usar Tool ou StructuredTool do LangChain para definir essas ferramentas.
Criação do Agente Executor (LangChain Agent):
Usar um dos tipos de agentes do LangChain (e.g., create_openai_tools_agent ou um agente ReAct) e um AgentExecutor.
Fornecer ao agente o LLM e a lista de ferramentas definidas.
O agente usará o LLM para decidir qual ferramenta chamar (ou se deve responder diretamente) com base na entrada do usuário e no histórico.
Método Principal de Interação:
Criar um método principal no SerenaAIAgent (e.g., async def process_user_interaction(self, phone_number: str, user_message: str, message_type: str, media_url: Optional[str] = None) -> str):
Este método orquestrará os passos:
Obter histórico da conversa.
Se message_type for mídia (e.g., imagem da fatura):
Desencadear o download do arquivo.
Chamar a ferramenta OCR.
Atualizar o estado da qualificação com os dados do OCR.
Gerar uma mensagem de confirmação ou próximo passo.
Se for uma mensagem de texto:
Usar o Agente Executor LangChain para processar a user_message e o histórico. O agente decidirá se usa RAG, chama a API Serena, ou apenas conversa.
Obter a resposta gerada pela IA.
Atualizar o histórico da conversa e os dados de qualificação.
Retornar a resposta da IA para ser enviada ao usuário.
Fase 4: Integração com o Workflow Kestra ai-conversation-activation
Simplificar as Tasks Kestra:
As tasks classify-user-intention, extract-user-data, e generate-ai-response no workflow Kestra serão significativamente simplificadas.
Provavelmente, elas se fundirão em uma ou duas tasks principais que fazem chamadas ao SerenaAIAgent.process_user_interaction(...).
Passagem de Dados:
O Kestra continuará responsável por pegar os dados do trigger.body do webhook do WhatsApp (lead_phone, lead_message, message_type, media_url se houver anexo).
Se houver um anexo, o Kestra pode precisar de uma task para baixar o arquivo para um local acessível pelo kestra-python-runner e passar o caminho do arquivo para o SerenaAIAgent.
A task Kestra receberá a resposta final da IA do SerenaAIAgent e a passará para a task send-ai-response.
Manter a Task send-ai-response:
Esta task Kestra continuará responsável por chamar o serviço whatsapp-service para enviar a resposta final ao usuário.

O que Precisamos de Você (IA de Codificação):
Ajuda na estruturação da classe SerenaAIAgent e seus métodos.
Exemplos de como integrar PromptTemplate, LLMs, e OutputParser para classificação e extração.
Orientação sobre como configurar e usar o Agente Executor com as ferramentas personalizadas (SerenaAPI, OCRProcessor).
Melhores práticas para passar o contexto da conversa (histórico) para o agente.
Se optarmos por RAG, ajuda na configuração do pipeline de RAG (loaders, splitters, embeddings, vector store, retriever).
Como o script dentro da task Kestra deve instanciar e chamar o SerenaAIAgent.
Acreditamos que essa abordagem nos dará um sistema de IA mais poderoso, flexível e de fácil manutenção. Por favor, nos guie na implementação desses componentes.