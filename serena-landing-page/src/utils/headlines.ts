// A/B Testing headline variants
export type HeadlineVariant = {
  id: string;
  title: string;
  subtitle: string;
};

export const headlineVariants: HeadlineVariant[] = [
  {
    id: 'variant-1',
    title: 'Paga R$500 por mês de luz? Com Serena, você economiza até R$1.000 por ano. Sem gastar nada.',
    subtitle: 'Preencha o formulário e receba uma simulação personalizada com Serena.'
  },
  {
    id: 'variant-2',
    title: 'Serena reduz sua conta em até 18%. Sem investimento. Sem obra. Só economia.',
    subtitle: 'Descubra quanto você pode economizar agora.'
  },
  {
    id: 'variant-3',
    title: 'Você trabalha. A energia solar também. Com a Serena, ela trabalha por você — e custa menos.',
    subtitle: 'Sem compromisso. Só vantagem.'
  },
  {
    id: 'variant-4',
    title: 'Quanto você pagou de luz nos últimos 12 meses? Com Serena, poderia ter sobrado até R$1.080 no seu bolso.',
    subtitle: 'Preencha o formulário e receba uma simulação personalizada com Serena.'
  },
  {
    id: 'variant-5',
    title: 'Em dois anos, você pode economizar mais de R$2.000 com a Serena. E o melhor: sem comprar placa nenhuma.',
    subtitle: 'Descubra quanto você pode economizar agora.'
  },
  {
    id: 'variant-6',
    title: 'A conta de luz sobe. Com Serena, o seu custo desce. Faça a conta. Depois preencha o formulário.',
    subtitle: 'Sem compromisso. Só vantagem.'
  },
  {
    id: 'variant-7',
    title: 'Serena entrega energia limpa, mais barata e sem custo de instalação. Só precisa de um clique seu.',
    subtitle: 'Preencha o formulário e receba uma simulação personalizada com Serena.'
  },
  {
    id: 'variant-8',
    title: 'Economia imediata, sem investimento. Isso é energia solar com Serena.',
    subtitle: 'Descubra quanto você pode economizar agora.'
  },
  {
    id: 'variant-9',
    title: 'Está tudo mais caro. Mas sua conta de luz pode ser mais barata a partir de agora. Descubra como.',
    subtitle: 'Sem compromisso. Só vantagem.'
  },
  {
    id: 'variant-10',
    title: 'Enquanto outros ainda pesquisam por placas solares, você já pode começar a economizar hoje. Com Serena.',
    subtitle: 'Preencha o formulário e receba uma simulação personalizada com Serena.'
  },
  {
    id: 'variant-11',
    title: 'Você não precisa comprar placas, nem esperar retorno. Com Serena, a economia começa no próximo mês.',
    subtitle: 'Descubra quanto você pode economizar agora.'
  },
  {
    id: 'variant-12',
    title: 'Já pensou em economizar R$1.500 em dois anos sem investir um real? Com Serena, isso é possível.',
    subtitle: 'Sem compromisso. Só vantagem.'
  },
  {
    id: 'variant-13',
    title: 'Você paga a conta. A Serena paga a tecnologia. O sol faz o resto. Simples assim.',
    subtitle: 'Preencha o formulário e receba uma simulação personalizada com Serena.'
  },
  {
    id: 'variant-14',
    title: 'Se a sua conta de luz passou dos R$400, você já está pagando por uma energia que podia ser solar.',
    subtitle: 'Descubra quanto você pode economizar agora.'
  },
  {
    id: 'variant-15',
    title: 'Pare de financiar o sistema antigo. Com Serena, você economiza sem gastar. E sem esperar.',
    subtitle: 'Sem compromisso. Só vantagem.'
  }
];

// Function to get a random headline variant for A/B testing
export const getRandomHeadlineVariant = (): HeadlineVariant => {
  const randomIndex = Math.floor(Math.random() * headlineVariants.length);
  return headlineVariants[randomIndex];
};

// Function to get a specific headline variant by ID
export const getHeadlineVariantById = (id: string): HeadlineVariant => {
  const variant = headlineVariants.find(v => v.id === id);
  return variant || headlineVariants[0]; // Fallback to first variant if not found
};
