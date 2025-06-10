// Lista de estados brasileiros
export const estados = [
  { value: 'AC', label: 'Acre' },
  { value: 'AL', label: 'Alagoas' },
  { value: 'AP', label: 'Amapá' },
  { value: 'AM', label: 'Amazonas' },
  { value: 'BA', label: 'Bahia' },
  { value: 'CE', label: 'Ceará' },
  { value: 'DF', label: 'Distrito Federal' },
  { value: 'ES', label: 'Espírito Santo' },
  { value: 'GO', label: 'Goiás' },
  { value: 'MA', label: 'Maranhão' },
  { value: 'MT', label: 'Mato Grosso' },
  { value: 'MS', label: 'Mato Grosso do Sul' },
  { value: 'MG', label: 'Minas Gerais' },
  { value: 'PA', label: 'Pará' },
  { value: 'PB', label: 'Paraíba' },
  { value: 'PR', label: 'Paraná' },
  { value: 'PE', label: 'Pernambuco' },
  { value: 'PI', label: 'Piauí' },
  { value: 'RJ', label: 'Rio de Janeiro' },
  { value: 'RN', label: 'Rio Grande do Norte' },
  { value: 'RS', label: 'Rio Grande do Sul' },
  { value: 'RO', label: 'Rondônia' },
  { value: 'RR', label: 'Roraima' },
  { value: 'SC', label: 'Santa Catarina' },
  { value: 'SP', label: 'São Paulo' },
  { value: 'SE', label: 'Sergipe' },
  { value: 'TO', label: 'Tocantins' }
];

// Mapeamento de cidades por estado (simplificado para as principais cidades)
export const cidadesPorEstado: Record<string, Array<{ value: string; label: string }>> = {
  AC: [
    { value: 'rio-branco', label: 'Rio Branco' },
    { value: 'cruzeiro-do-sul', label: 'Cruzeiro do Sul' }
  ],
  AL: [
    { value: 'maceio', label: 'Maceió' },
    { value: 'arapiraca', label: 'Arapiraca' }
  ],
  AP: [
    { value: 'macapa', label: 'Macapá' },
    { value: 'santana', label: 'Santana' }
  ],
  AM: [
    { value: 'manaus', label: 'Manaus' },
    { value: 'parintins', label: 'Parintins' }
  ],
  BA: [
    { value: 'salvador', label: 'Salvador' },
    { value: 'feira-de-santana', label: 'Feira de Santana' },
    { value: 'vitoria-da-conquista', label: 'Vitória da Conquista' }
  ],
  CE: [
    { value: 'fortaleza', label: 'Fortaleza' },
    { value: 'caucaia', label: 'Caucaia' },
    { value: 'juazeiro-do-norte', label: 'Juazeiro do Norte' }
  ],
  DF: [
    { value: 'brasilia', label: 'Brasília' }
  ],
  ES: [
    { value: 'vitoria', label: 'Vitória' },
    { value: 'serra', label: 'Serra' },
    { value: 'vila-velha', label: 'Vila Velha' }
  ],
  GO: [
    { value: 'goiania', label: 'Goiânia' },
    { value: 'aparecida-de-goiania', label: 'Aparecida de Goiânia' },
    { value: 'anapolis', label: 'Anápolis' }
  ],
  MA: [
    { value: 'sao-luis', label: 'São Luís' },
    { value: 'imperatriz', label: 'Imperatriz' }
  ],
  MT: [
    { value: 'cuiaba', label: 'Cuiabá' },
    { value: 'varzea-grande', label: 'Várzea Grande' }
  ],
  MS: [
    { value: 'campo-grande', label: 'Campo Grande' },
    { value: 'dourados', label: 'Dourados' }
  ],
  MG: [
    { value: 'belo-horizonte', label: 'Belo Horizonte' },
    { value: 'uberlandia', label: 'Uberlândia' },
    { value: 'contagem', label: 'Contagem' },
    { value: 'juiz-de-fora', label: 'Juiz de Fora' }
  ],
  PA: [
    { value: 'belem', label: 'Belém' },
    { value: 'ananindeua', label: 'Ananindeua' },
    { value: 'santarem', label: 'Santarém' }
  ],
  PB: [
    { value: 'joao-pessoa', label: 'João Pessoa' },
    { value: 'campina-grande', label: 'Campina Grande' }
  ],
  PR: [
    { value: 'curitiba', label: 'Curitiba' },
    { value: 'londrina', label: 'Londrina' },
    { value: 'maringa', label: 'Maringá' }
  ],
  PE: [
    { value: 'recife', label: 'Recife' },
    { value: 'jaboatao-dos-guararapes', label: 'Jaboatão dos Guararapes' },
    { value: 'olinda', label: 'Olinda' }
  ],
  PI: [
    { value: 'teresina', label: 'Teresina' },
    { value: 'parnaiba', label: 'Parnaíba' }
  ],
  RJ: [
    { value: 'rio-de-janeiro', label: 'Rio de Janeiro' },
    { value: 'sao-goncalo', label: 'São Gonçalo' },
    { value: 'duque-de-caxias', label: 'Duque de Caxias' },
    { value: 'nova-iguacu', label: 'Nova Iguaçu' },
    { value: 'niteroi', label: 'Niterói' }
  ],
  RN: [
    { value: 'natal', label: 'Natal' },
    { value: 'mossoro', label: 'Mossoró' }
  ],
  RS: [
    { value: 'porto-alegre', label: 'Porto Alegre' },
    { value: 'caxias-do-sul', label: 'Caxias do Sul' },
    { value: 'pelotas', label: 'Pelotas' }
  ],
  RO: [
    { value: 'porto-velho', label: 'Porto Velho' },
    { value: 'ji-parana', label: 'Ji-Paraná' }
  ],
  RR: [
    { value: 'boa-vista', label: 'Boa Vista' }
  ],
  SC: [
    { value: 'florianopolis', label: 'Florianópolis' },
    { value: 'joinville', label: 'Joinville' },
    { value: 'blumenau', label: 'Blumenau' }
  ],
  SP: [
    { value: 'sao-paulo', label: 'São Paulo' },
    { value: 'guarulhos', label: 'Guarulhos' },
    { value: 'campinas', label: 'Campinas' },
    { value: 'sao-bernardo-do-campo', label: 'São Bernardo do Campo' },
    { value: 'santo-andre', label: 'Santo André' },
    { value: 'ribeirao-preto', label: 'Ribeirão Preto' },
    { value: 'osasco', label: 'Osasco' },
    { value: 'sorocaba', label: 'Sorocaba' }
  ],
  SE: [
    { value: 'aracaju', label: 'Aracaju' },
    { value: 'nossa-senhora-do-socorro', label: 'Nossa Senhora do Socorro' }
  ],
  TO: [
    { value: 'palmas', label: 'Palmas' },
    { value: 'araguaina', label: 'Araguaína' }
  ]
};
