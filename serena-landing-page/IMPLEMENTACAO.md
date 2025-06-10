# Implementação da Landing Page Serena Energia

## Visão Geral

Este documento descreve a implementação da landing page de captura de leads para a Serena Energia, conforme o plano estabelecido. A landing page foi desenvolvida utilizando Next.js, TypeScript e Tailwind CSS, seguindo as melhores práticas de desenvolvimento web moderno.

## Estrutura do Projeto

O projeto foi estruturado seguindo as convenções do Next.js com App Router:

```
serena-energia/
├── public/               # Arquivos estáticos
│   └── hero-image.svg    # Imagem da seção hero
├── src/                  # Código fonte
│   ├── app/              # Páginas da aplicação
│   │   ├── page.tsx      # Página inicial
│   │   ├── layout.tsx    # Layout global
│   │   ├── globals.css   # Estilos globais
│   │   └── politica-de-privacidade/  # Página de política de privacidade
│   │       └── page.tsx
│   ├── components/       # Componentes React
│   │   ├── Hero.tsx      # Seção de destaque
│   │   ├── Benefits.tsx  # Seção de benefícios
│   │   ├── LeadForm.tsx  # Formulário de captura de leads
│   │   ├── Footer.tsx    # Rodapé
│   │   └── ui/           # Componentes de UI reutilizáveis
│   │       ├── Input.tsx
│   │       ├── Select.tsx
│   │       ├── Checkbox.tsx
│   │       ├── Button.tsx
│   │       └── Alert.tsx
│   └── utils/            # Funções utilitárias
│       ├── validation.ts # Funções de validação
│       └── api.ts        # Funções para submissão de dados
├── .env.local            # Variáveis de ambiente
├── tailwind.config.js    # Configuração do Tailwind CSS
├── postcss.config.mjs    # Configuração do PostCSS
└── package.json          # Dependências e scripts
```

## Componentes Implementados

### 1. Componentes de UI

Foram criados componentes reutilizáveis para os elementos de interface:

- **Input**: Campo de texto com label e validação
- **Select**: Campo de seleção com opções
- **Checkbox**: Campo de marcação com label
- **Button**: Botão com variantes e estado de carregamento
- **Alert**: Mensagem de alerta com diferentes tipos (sucesso, erro, etc.)

### 2. Seções da Página

A landing page foi dividida em seções principais:

- **Hero**: Seção de destaque com título, subtítulo e chamada para ação
- **Benefits**: Seção de benefícios com ícones e descrições
- **LeadForm**: Formulário de captura de leads com validação
- **Footer**: Rodapé com links e informações da empresa

### 3. Página de Política de Privacidade

Foi criada uma página separada para a política de privacidade, acessível através do link no rodapé.

## Funcionalidades Implementadas

### 1. Formulário de Captura de Leads

O formulário de captura de leads foi implementado com as seguintes funcionalidades:

- **Campos**:
  - Nome Completo (validação de texto)
  - E-mail (validação de formato)
  - WhatsApp (máscara para formato brasileiro)
  - Valor da Conta de Luz (select com opções)
  - Consentimento LGPD (checkbox)

- **Validação**:
  - Validação em tempo real
  - Mensagens de erro claras
  - Prevenção de submissão com erros

- **Submissão**:
  - Integração direta com Google Sheets para armazenamento de dados
  - Feedback visual durante e após submissão
  - Tratamento de erros e mecanismo de fallback

### 2. Responsividade

A landing page foi implementada com design responsivo, adaptando-se a diferentes tamanhos de tela:

- Layout fluido com Flexbox e Grid
- Media queries para ajustes específicos
- Abordagem mobile-first

### 3. Acessibilidade

Foram implementadas práticas de acessibilidade:

- HTML semântico
- Labels associados a campos de formulário
- Mensagens de erro associadas aos campos
- Contraste adequado de cores
- Navegação por teclado

## Configuração de Ambiente

### 1. Variáveis de Ambiente

Foram configuradas as variáveis de ambiente para a integração com Google Sheets:

```env
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id
GOOGLE_SHEETS_SHEET_NAME=Leads Serena
GOOGLE_SHEETS_CLIENT_EMAIL=your_service_account_email
GOOGLE_SHEETS_PRIVATE_KEY=your_private_key
```

### 2. Estilização com Tailwind CSS

O Tailwind CSS foi configurado com um tema personalizado:

- Cores primárias: tons de verde para representar energia renovável
- Cores secundárias: tons de cinza para um visual moderno
- Tipografia: fonte sans-serif (Inter)

## Considerações Finais

A implementação seguiu o plano estabelecido, resultando em uma landing page profissional, responsiva e funcional para a captura de leads da Serena Energia. A página está pronta para ser implantada em um ambiente de produção.

Para executar o projeto localmente:

```bash
# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev

# Construir para produção
npm run build

# Iniciar servidor de produção
npm start
```
