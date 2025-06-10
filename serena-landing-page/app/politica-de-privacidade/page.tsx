import Link from 'next/link';
import Image from 'next/image';
import Footer from '@/components/Footer';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Aviso de Privacidade e Proteção de Dados | Serena Energia',
  description: 'Aviso de Privacidade da Serena Energia. Saiba como tratamos seus dados pessoais de acordo com a LGPD.',
};

export function generateViewport() {
  return {
    themeColor: '#ff5247',
    viewport: "width=device-width, initial-scale=1",
  };
}

export default function PrivacyPolicy() {
  return (
    <main>
      <div className="bg-serena-lightgray py-8">
        <div className="container mx-auto px-4 md:px-6">
          <div className="flex justify-between items-center">
            <Link href="/" className="inline-block">
              <Image
                src="/images/logo.svg"
                alt="Serena Energia"
                width={150}
                height={50}
                className="h-10 w-auto"
              />
            </Link>

            <Link
              href="/"
              className="inline-flex items-center text-serena-blue hover:text-serena-darkblue transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
              </svg>
              Voltar para a página inicial
            </Link>
          </div>

          <div className="mt-12 text-center">
            <h1 className="text-3xl md:text-4xl font-bold text-serena-darkblue">
              Aviso de Privacidade e Proteção de Dados
            </h1>
            <p className="mt-4 text-gray-600 max-w-2xl mx-auto">
              Saiba como a Serena Energia coleta, utiliza e protege seus dados pessoais de acordo com a LGPD
            </p>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 md:px-6 py-12">
        <div className="max-w-3xl mx-auto bg-white p-8 rounded-xl shadow-serena">
          <div className="mb-8 pb-6 border-b border-gray-100">
            <p className="text-gray-500">
              <strong>Última atualização:</strong> 24 de janeiro de 2025
            </p>
          </div>

          <div className="space-y-8">
            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">I. Para que serve este Aviso de Privacidade</h2>
              <p className="text-gray-700">
                A <strong>Serena</strong> valoriza a sua privacidade e a proteção dos seus Dados Pessoais. Por isso, é nosso compromisso garantir que você, como Titular de Dados e usuário dos nossos serviços, saiba como Tratamos os seus Dados Pessoais, com quem podemos compartilhá-los, como os protegemos e os mantemos seguros, sempre de acordo com a legislação aplicável de proteção de dados e nos termos deste Aviso de Privacidade ("<strong>Aviso</strong>").
              </p>
              <p className="text-gray-700 mt-4">
                Este Aviso está em conformidade com a legislação aplicável de proteção de dados, em especial a Lei Geral de Proteção de Dados (Lei No. 13.709/2018) – LGPD, que regula o tratamento de dados pessoais no Brasil, garantindo os direitos dos titulares e impondo deveres aos controladores e operadores de dados. Leia atentamente este Aviso, pois, ao interagir conosco, você confia a nós seus Dados Pessoais e declara ter lido atentamente as disposições deste Aviso, declarando estar ciente dos termos aqui indicados.
              </p>
              <p className="text-gray-700 mt-4">
                Caso você tenha qualquer dúvida, não hesite em entrar em contato conosco pelo e-mail: <a href="mailto:dpo@omegaenergia.com.br" className="text-serena-blue hover:text-serena-darkblue">dpo@omegaenergia.com.br</a>.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">II. Quem somos?</h2>
              <p className="text-gray-700">
                <strong>SERENA ENERGIA S.A.</strong>, inscrita no CNPJ/MF sob o nº42.500.384/0001-51, é uma pessoa jurídica de direito privado ("<strong>Serena</strong>"), é responsável pelos dados pessoais que você compartilha conosco.
              </p>
              <p className="text-gray-700 mt-4">
                Sempre que você encontrar os termos "Serena", "nós", "nosso" ou "nos", é à <strong>SERENA ENERGIA S.A</strong>. a que estamos nos referindo.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">III. Princípios do Tratamento</h2>
              <p className="text-gray-700">
                A Serena se orienta, a todo momento, pelos princípios estabelecidos na Legislação Aplicável de Proteção de Dados para o Tratamento de seus Dados Pessoais. São eles os princípios da finalidade, adequação, necessidade, livre acesso, qualidade dos dados, transparência, segurança, não discriminação, prevenção e responsabilidade e prestação de contas.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">IV. De quem são os Dados Pessoais tratados pela Serena?</h2>
              <p className="text-gray-700">
                Neste Aviso, os Dados Pessoais são quaisquer informações identificadas e/ou identificáveis referentes a você, nosso cliente ("<strong>Titular de Dados</strong>"), os quais tratamos em nossas atividades diárias, especialmente para garantir a prestação dos serviços. Quaisquer termos que apareçam neste Aviso, que estejam escritos em letra maiúscula, e não foram definidos acima deverão ser interpretados conforme a LGPD.
              </p>
              <p className="text-gray-700 mt-4">
                Este Aviso é aplicável a todos os consumidores que interagem e/ou interagiram, de alguma forma, com a Serena.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">V. Quais tipos de Dados Pessoais coletamos e tratamos?</h2>
              <p className="text-gray-700 mb-4">
                Para o desempenho de nossas atividades, podemos tratar as seguintes categorias de Dados Pessoais:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-gray-700">
                <li><strong className="text-serena-darkblue">Informações cadastrais e de identificação:</strong> nome completo, RG, CPF, nacionalidade, endereço, e-mail, data de nascimento, profissão, estado civil, assinatura e telefone;</li>
                <li><strong className="text-serena-darkblue">Informações de autenticação:</strong> login e senha do portal da distribuidora de energia;</li>
                <li><strong className="text-serena-darkblue">Informações relacionadas ao consumo de energia:</strong> faturas de energia, número da unidade consumidora, protocolos ou tickets de atendimento (caso aplicável), histórico de consumo, dentre outros que se façam necessários.</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">VI. Como coletamos seus Dados Pessoais e para quais finalidades os usamos?</h2>
              <p className="text-gray-700 font-bold">
                Manifestação de Ciência e Consentimento
              </p>
              <p className="text-gray-700 mt-2 mb-4">
                Ao acessar nossos serviços ou interagir conosco, você declara estar ciente dos termos deste Aviso de Privacidade. Para finalidades que exijam consentimento, será solicitado explicitamente, garantindo que sua manifestação seja livre, informada e inequívoca. Você poderá revogar o consentimento a qualquer momento, conforme disposto no art. 8º da LGPD.
              </p>
              <p className="text-gray-700 mb-4">
                Geralmente, a Serena coleta seus Dados Pessoais diretamente de você, por meio do formulário preenchido diretamente do website da Serena ou por outro canal de comunicação.
              </p>
              <p className="text-gray-700 mb-4">
                Não iremos realizar o tratamento de seus dados pessoais sem possuir uma base legal para isso, em cumprimento às leis de proteção de dados aplicáveis. A base legal para coleta e tratamento dos seus dados pessoais dependerá dos Dados Pessoais em questão, bem como da finalidade de Tratamento.
              </p>

              <p className="text-gray-700 font-bold mt-6">1. Finalidades</p>

              <p className="text-gray-700 font-bold mt-4">Prestamos nossos serviços utilizando seus dados cadastrais e de consumo para:</p>
              <ul className="list-disc pl-6 space-y-2 text-gray-700">
                <li>Efetivar contratos.</li>
                <li>Oferecer descontos na fatura de energia.</li>
                <li>Realizar a emissão de boletos.</li>
              </ul>

              <p className="text-gray-700 mt-4 mb-4">
                Por exemplo, suas informações cadastrais, de autenticação e relacionadas ao seu consumo de energia podem ser utilizados para (i) calcular possíveis descontos na conta de luz, (ii) efetuar seu cadastro nos sistemas internos da Serena; (iii) realizar a assinatura do contrato para contratação dos serviços; e (iv) conduzir outros processos indispensáveis à contratação e prestação de nossos serviços, como a geração do boleto para que você possa pagar sua fatura com desconto.
              </p>

              <p className="text-gray-700 font-bold mt-4">Melhoramos nossos serviços e realizamos campanhas de marketing mediante:</p>
              <ul className="list-disc pl-6 space-y-2 text-gray-700">
                <li>Controle de qualidade.</li>
                <li>Envio de ofertas relevantes.</li>
                <li>Prospecção de novos clientes.</li>
              </ul>

              <p className="text-gray-700 mt-4 mb-4">
                Nesse sentido, podemos tratar seus dados quando há um legítimo interesse em promover nossas atividades ou proporcionar benefícios a você. Isso inclui, por exemplo, controle da qualidade de atendimento, gestão de campanhas de marketing voltadas à divulgação de serviços que possam ser do seu interesse e a prospecção de novos clientes com perfis semelhantes aos de nossa base atual.
              </p>

              <p className="text-gray-700 mb-4">
                Reforçamos que somente os Dados Pessoais estritamente necessários serão tratados para estas finalidades específicas (e.g., nome, estado, cidade, e-mail, WhatsApp e dados de consumo de energia), garantindo que seus direitos e interesses sejam observados durante todo o Tratamento.
              </p>

              <p className="text-gray-700 font-bold mt-6">2. Bases legais aplicáveis</p>

              <p className="text-gray-700 mb-4">
                Nos termos do art. 7º da LGPD, utilizamos as seguintes bases legais para o tratamento de seus dados:
              </p>

              <p className="text-gray-700 mb-4">
                As bases legais incluem:
              </p>

              <ul className="list-disc pl-6 space-y-2 text-gray-700">
                <li>Consentimento</li>
                <li>Legítimo interesse</li>
                <li>Execução de contrato</li>
                <li>Cumprimento de obrigações legais</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">VII. Por quanto tempo mantemos seus Dados Pessoais nos nossos sistemas?</h2>
              <p className="text-gray-700">
                Armazenaremos os seus Dados Pessoais apenas durante o período necessário para cumprir as finalidades de Tratamento para as quais o Dado Pessoal foi coletado, conforme indicado neste Aviso. Podemos, além disso, guardar seus Dados Pessoais por um período adicional para cumprir nossas obrigações legais ou regulatórias, para o exercício regular de nossos direitos em processos judiciais, administrativos ou arbitrais.
              </p>
              <p className="text-gray-700 mt-4">
                Assim, a menos que tenhamos uma razão legal para manter os seus Dados Pessoais nos nossos sistemas, descartaremos os seus Dados Pessoais ou realizaremos o procedimento de anonimização sempre quando (i) a finalidade do Tratamento foi alcançada ou os Dados Pessoais deixaram de ser necessários; (ii) o Tratamento chegar ao fim; e (iii) a ANPD determinar, nós procederemos à eliminação dos Dados Pessoais de nossos sistemas ou realizaremos o procedimento de anonimização, no âmbito e nos limites técnicos das atividades desenvolvidas pela Serena.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">VIII. Com quem podemos compartilhar seus Dados Pessoais?</h2>
              <p className="text-gray-700 mb-4">
                A Serena preserva a privacidade e a proteção dos seus Dados Pessoais e se compromete a não compartilhar os seus Dados Pessoais, a menos que (i) seja autorizado prévia e expressamente por você; ou (ii) em um dos seguintes casos:
              </p>

              <ul className="list-disc pl-6 space-y-4 text-gray-700">
                <li>
                  <strong className="text-serena-darkblue">Operações Societárias:</strong> Em decorrência de eventuais operações de reestruturação societária, fusões, aquisições, incorporações e similares, a Serena poderá compartilhar informações, Dados Pessoais com as pessoas físicas ou jurídicas envolvidas na operação pretendida. Note que, nestes casos, os terceiros celebrarão com a Serena contratos de confidencialidade por meio do qual se comprometerão a não usar ou compartilhar os Dados Pessoais para finalidades diversas daquelas relacionadas à operação pretendida.
                </li>
                <li>
                  <strong className="text-serena-darkblue">Parceiros:</strong> Às vezes, podemos precisar compartilhar alguns Dados Pessoais de forma incidental para parceiros de confiança que nos auxiliam e ajudam no fornecimento de serviços que são necessários à prestação dos nossos serviços, tais como os fornecedores de nossas plataformas e prestadores de serviços de armazenamento de dados. Além disso, podemos compartilhar os seus Dados Pessoais com terceiros para fins de mídia direcionada (como por exemplo, o Google e a Meta).
                </li>
                <li>
                  <strong className="text-serena-darkblue">Medidas Judiciais e Obrigações Legais:</strong> A Serena poderá divulgar ou compartilhar informações, incluindo Dados Pessoais, se entender, de boa-fé, que o acesso, o uso, a conservação ou a divulgação das informações seja razoavelmente necessário para (i) cumprir qualquer legislação, regulamentação, decisão judicial ou solicitação governamental; (ii) investigar possíveis violações de direitos; (iii) detectar ou impedir fraudes, bem como resolver questões técnicas ou de segurança; (iv) garantir a segurança dos Titulares de Dados e de terceiros; (v) resguardar direitos e prevenir responsabilidades da Serena; (vi) investigar, impedir ou tomar medidas relacionadas a atividades ilegais, suspeitas ou reais, ou para cooperar com órgãos públicos; e (vii) cumprir obrigações legais ou qualquer outra determinação perante órgãos do governo e do judiciário. Manteremos esse compartilhamento apenas no limite do exigido para cumprimento dessas obrigações.
                </li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">IX. Como protegemos seus Dados Pessoais?</h2>
              <p className="text-gray-700">
                A segurança dos seus Dados Pessoais é de extrema importância para nós. Por isso, estamos comprometidos a adotar medidas de segurança técnicas e administrativas aptas a proteger os seus Dados Pessoais de acessos não autorizados e de situações acidentais ou ilícitas de destruição, perda, alteração, comunicação ou qualquer forma de tratamento inadequado ou ilícito, bem como todas as medidas que são aconselháveis dado o estado da tecnologia, garantindo a integridade, segurança e confidencialidade dos Dados Pessoais Tratados.
              </p>
              <p className="text-gray-700 mt-4">
                Todavia, saiba que nenhum método de transmissão ou retenção de Dados Pessoais eletrônicos é plenamente seguro e pode estar sujeito a ataques externos. Tendo isso em vista, não seremos responsáveis por prejuízos que derivem de atos de terceiros que utilizem de meios indevidos, fraudulentos ou ilegais para acessar as informações armazenadas nos servidores ou nos bancos de Dados Pessoais utilizados.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">X. Quais são os seus direitos como Titulares de Dados?</h2>
              <p className="text-gray-700 mb-4">
                De acordo com a LGPD, você tem os seguintes direitos:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-gray-700">
                <li>Direito de confirmação da existência de tratamento;</li>
                <li>Direito de acesso aos dados;</li>
                <li>Direito de correção de dados incompletos, inexatos ou desatualizados;</li>
                <li>Direito à anonimização, bloqueio ou eliminação de dados desnecessários, excessivos ou tratados em desconformidade;</li>
                <li>Direito à portabilidade dos dados;</li>
                <li>Direito à eliminação dos dados tratados com consentimento;</li>
                <li>Direito à informação sobre compartilhamento;</li>
                <li>Direito à informação sobre a possibilidade de não fornecer consentimento;</li>
                <li>Direito à revogação do consentimento;</li>
                <li>Direito de peticionar perante a ANPD.</li>
              </ul>

              <p className="text-gray-700 mt-4">
                De toda forma, não hesite em entrar em contato conosco, por meio dos canais abaixo, antes de apresentar qualquer reclamação à ANPD, para que possamos tentar resolver seu questionamento ou reclamação de maneira imediata.
              </p>

              <p className="text-gray-700 mt-4">
                <strong>Canal para exercer os seus diretos:</strong> Para exercer os direitos acima elencados ou esclarecer qualquer dúvida quanto ao disposto neste Aviso, bastará enviar um e-mail para nós pelo e-mail <a href="mailto:dpo@omegaenergia.com.br" className="text-serena-blue hover:text-serena-darkblue">dpo@omegaenergia.com.br</a>. Note, por gentileza, que, para processar sua solicitação de exercício de direitos de forma segura, podemos, eventualmente, solicitar a você uma prova de sua identidade e mais informações sobre o direito que você deseja exercer.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">XI. Quem é o nosso Encarregado de Dados?</h2>
              <p className="text-gray-700 mb-4">
                De acordo com a LGPD, como regra, todos os Agentes de Tratamento deverão indicar um Encarregado, que será responsável por, dentre outras atividades, intermediar a relação entre a Serena e os Titulares de Dados e/ou a ANPD:
              </p>

              <div className="border border-gray-200 rounded-lg p-4 mb-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="font-bold text-gray-700">Nome</div>
                  <div className="text-gray-700">Daniel Biaggio</div>
                </div>
                <div className="grid grid-cols-2 gap-4 mt-2">
                  <div className="font-bold text-gray-700">E-mail</div>
                  <div className="text-gray-700"><a href="mailto:dpo@omegaenergia.com.br" className="text-serena-blue hover:text-serena-darkblue">dpo@omegaenergia.com.br</a></div>
                </div>
              </div>

              <p className="text-gray-700">
                Sinta-se à vontade para entrar em contato conosco pelo e-mail do DPO, conforme indicado acima.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">XII. Alterações a este Aviso de Privacidade</h2>
              <p className="text-gray-700 mb-4">
                Este Aviso pode ser revisto a qualquer momento, razão pela qual recomendamos que você consulte-o periodicamente para se manter atualizado. Porém, não se preocupe! Sempre que fizermos alterações significativas ao conteúdo deste Aviso, você será notificado. Além disso, caso alguma dessas alterações implique na necessidade de obtermos a sua autorização prévia e expressa, assim o faremos.
              </p>

              <div className="border border-gray-200 rounded-lg p-4 mb-4">
                <div className="grid grid-cols-3 gap-4 font-bold text-gray-700 border-b pb-2">
                  <div>Versão</div>
                  <div>Data</div>
                  <div>Motivos da alteração</div>
                </div>
                <div className="grid grid-cols-3 gap-4 text-gray-700 pt-2">
                  <div>1</div>
                  <div>24/01/2025</div>
                  <div>N/A</div>
                </div>
              </div>
            </section>

            <section>
              <p className="text-center font-bold text-serena-darkblue">
                FICAMOS FELIZES QUE VOCÊ TENHA LIDO O NOSSO AVISO E ESTAMOS À DISPOSIÇÃO CASO TENHA DÚVIDAS!
              </p>
            </section>
          </div>
        </div>
      </div>

      <Footer />
    </main>
  );
}