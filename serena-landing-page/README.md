# Serena Energia - Landing Page

Landing page de captura de leads para a Serena Energia, uma empresa focada em energia limpa e renovável. O objetivo é capturar leads fornecendo um formulário para que os visitantes insiram seus dados de contato e informações sobre sua conta de luz.

## Tecnologias Utilizadas

- **Next.js**: Framework React para renderização do lado do servidor
- **TypeScript**: Superset JavaScript com tipagem estática
- **Tailwind CSS**: Framework CSS utilitário
- **React Hook Form**: Biblioteca para gerenciamento de formulários

## Estrutura do Projeto

```
serena-energia/
├── public/               # Arquivos estáticos
├── src/                  # Código fonte
│   ├── app/              # Páginas da aplicação (App Router)
│   │   ├── page.tsx      # Página inicial
│   │   ├── layout.tsx    # Layout global
│   │   ├── globals.css   # Estilos globais
│   │   └── politica-de-privacidade/  # Página de política de privacidade
│   ├── components/       # Componentes React
│   │   ├── Hero.tsx      # Seção de destaque
│   │   ├── Benefits.tsx  # Seção de benefícios
│   │   ├── LeadForm.tsx  # Formulário de captura de leads
│   │   ├── Footer.tsx    # Rodapé
│   │   └── ui/           # Componentes de UI reutilizáveis
│   └── utils/            # Funções utilitárias
│       ├── validation.ts # Funções de validação
│       └── api.ts        # Funções para submissão de dados
├── .env.local            # Variáveis de ambiente (não versionado)
├── tailwind.config.js    # Configuração do Tailwind CSS
├── next.config.ts        # Configuração do Next.js
└── package.json          # Dependências e scripts
```

## Requisitos

- Node.js 18.x ou superior
- npm 9.x ou superior

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/serena-energia/landing-page.git
   cd landing-page
   ```

2. Instale as dependências:
   ```bash
   npm install
   ```

3. Crie um arquivo `.env.local` na raiz do projeto com as configurações do Google Sheets (veja o arquivo `.env.local.sample` para referência)

## Desenvolvimento

Para iniciar o servidor de desenvolvimento:

```bash
npm run dev
```

O site estará disponível em [http://localhost:3000](http://localhost:3000).

## Build e Produção

Para criar uma versão de produção:

```bash
npm run build
```

Para iniciar o servidor de produção:

```bash
npm start
```

## Funcionalidades

- **Página Inicial**: Apresentação da empresa e captura de leads
- **Formulário de Captura**: Coleta de dados dos usuários (nome, email, WhatsApp, valor da conta de luz)
- **Validação de Formulário**: Validação em tempo real dos campos do formulário
- **Integração com Google Sheets**: Armazenamento automático dos dados em planilha
- **Página de Política de Privacidade**: Informações sobre o tratamento de dados

## Personalização

### Cores

As cores principais podem ser ajustadas no arquivo `tailwind.config.js`:

```js
theme: {
  extend: {
    colors: {
      'primary': {
        // Tons de verde
      },
      'secondary': {
        // Tons de cinza
      },
    },
  },
},
```

### Textos

Os textos podem ser editados diretamente nos componentes correspondentes:

- `Hero.tsx`: Título e subtítulo principal
- `Benefits.tsx`: Benefícios da empresa
- `LeadForm.tsx`: Textos do formulário
- `Footer.tsx`: Informações do rodapé

## Licença

Este projeto é proprietário e confidencial. Todos os direitos reservados à Serena Energia.
