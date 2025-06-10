import Link from 'next/link';
import Image from 'next/image';
import Footer from '@/components/Footer';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Termos de Uso | Serena Energia',
  description: 'Termos de Uso da Serena Energia. Conheça as condições para utilização dos nossos serviços.',
};

export function generateViewport() {
  return {
    themeColor: '#ff5247',
    viewport: "width=device-width, initial-scale=1",
  };
}

export default function TermsOfUse() {
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
              Termos de Uso
            </h1>
            <p className="mt-4 text-gray-600 max-w-2xl mx-auto">
              Conheça as condições para utilização dos serviços da Serena Energia
            </p>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 md:px-6 py-12">
        <div className="max-w-3xl mx-auto bg-white p-8 rounded-xl shadow-serena">
          <div className="mb-8 pb-6 border-b border-gray-100">
            <p className="text-gray-500">
              <strong>Última atualização:</strong> 03 de dezembro de 2021
            </p>
          </div>

          <div className="space-y-8">
            <section>
              <p className="text-gray-700">
                <strong>SERENA ENERGIA S.A.</strong>, inscrita no CNPJ sob o nº 14.797.440/0001-26, é uma pessoa jurídica de direito privado ("Serena") que possibilita a compra de energia elétrica ("Fornecimento") para possíveis compradores ("Compradores"), por meio do Software da Serena ("Plataforma").
              </p>
              <p className="text-gray-700 mt-4">
                Por intermédio destes Termos e Condições Gerais de Uso e Privacidade ("Termos"), a Serena apresenta aos usuários e Compradores da Plataforma (todos em conjunto denominados "Usuários") as condições essenciais para o uso dos serviços oferecidos nesta Plataforma.
              </p>
              <p className="text-gray-700 mt-4">
                Ao utilizar a Plataforma ou adquirir o Fornecimento ofertado por Serena, os Usuários aceitam e se submetem às condições destes Termos.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">1. Objeto</h2>
              <p className="text-gray-700 mb-2">
                <strong>1.1.</strong> O serviço objeto dos presentes Termos permite que os Usuários que utilizem a Plataforma para livremente adquirir o Fornecimento da Serena para seus estabelecimentos comerciais.
              </p>
              <p className="text-gray-700 mb-2">
                <strong>1.2.</strong> A efetivação da contratação do Fornecimento se dará após o aceite da proposta pelo Comprador. Todas as informações fornecidas na Plataforma somente se concretizarão com o aceite pelo Comprador da proposta apresentada pela Serena.
              </p>
              <p className="text-gray-700 mb-2">
                <strong>1.3.</strong> Ao aceitar estes Termos os Usuários concordam e anuem com os termos e condições pré-estabelecidos nos Contratos de Compra e Venda de Energia Elétrica.
              </p>
              <p className="text-gray-700 mb-2">
                <strong>1.3.1.</strong> O aceite expresso na proposta comercial vincula os Usuários ao cumprimento dos termos e condições do respectivo Contrato, independentemente da assinatura de tal documento.
              </p>
              <p className="text-gray-700 mb-2">
                <strong>1.3.2.</strong> Na hipótese do COMPRADOR não realizar a assinatura do CONTRATO em 5 dias, a VENDEDORA, ao seu critério, poderá atualizar as condições comerciais. A obrigação inicial de assinatura da COMPRADORA continuará em vigor caso as condições comerciais sejam mantidas.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">2. Capacidade para cadastrar-se</h2>
              <p className="text-gray-700 mb-2">
                <strong>2.1.</strong> O Fornecimento pela Serena está disponível apenas para pessoas jurídicas regularmente inscritas nos cadastros de contribuintes federal e estaduais que tenham capacidade legal para contratá-los e que não estejam inabilitadas pela Serena (temporária ou definitivamente).
              </p>
              <p className="text-gray-700 mb-2">
                <strong>2.2.</strong> É vedada a criação de mais de um cadastro por Usuário. Em caso de multiplicidade de cadastros elaborados por um só Usuário, Serena reserva-se o direito de, a seu exclusivo critério e sem necessidade de prévia anuência dos ou comunicação aos Usuários, inabilitar todos os cadastros existentes e impedir eventuais cadastros futuros vinculados a estes.
              </p>
              <p className="text-gray-700 mb-2">
                <strong>2.3.</strong> A Serena pode unilateralmente excluir o cadastro dos Usuários quando verificado que a conduta do Usuário é ou será prejudicial ou ofensiva a outros Usuários, a Serena e seus funcionários ou a terceiros.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">3. Cadastro</h2>
              <p className="text-gray-700 mb-2">
                <strong>3.1.</strong> É necessário o preenchimento completo de todos os dados exigidos pela Serena para que o Usuário esteja habilitado a realizar eventual contratação do Fornecimento.
              </p>
              <p className="text-gray-700 mb-2">
                <strong>3.2.</strong> É de exclusiva responsabilidade dos Usuários fornecer, atualizar e garantir a veracidade dos dados cadastrais, não cabendo a Serena qualquer tipo de responsabilidade civil e criminal resultante de dados inverídicos, incorretos ou incompletos fornecidos pelos Usuários.
              </p>
              <p className="text-gray-700 mb-2">
                <strong>3.3.</strong> A Serena se reserva o direito de utilizar todos os meios válidos e possíveis para identificar seus Usuários, bem como de solicitar dados adicionais e documentos que entenda serem pertinentes a fim de conferir as informações inseridas.
              </p>
              <p className="text-gray-700 mb-2">
                <strong>3.4.</strong> Caso Serena considere um cadastro, ou as informações nele contidas, suspeito de conter dados errôneos e/ou inverídicos e/ou desalinhados com as diretrizes internas da Serena, a Serena se reserva o direito de suspender, temporária ou definitivamente, o Usuário responsável pelo cadastramento, e/ou a empresa atrelada ao cadastro, assim como impedir e bloquear qualquer cadastro realizado por estes, sem prejuízo de outras medidas que entenda necessárias e oportunas. No caso de aplicação de quaisquer destas sanções, não assistirá aos Usuários ou as empresas direito a qualquer tipo de indenização ou ressarcimento por perdas e danos, lucros cessantes ou danos morais.
              </p>
              <p className="text-gray-700 mb-2">
                <strong>3.5.</strong> O Usuário acessará sua conta por meio de e-mail e senha, comprometendo-se a não informar a terceiros esses dados, responsabilizando-se integralmente pelo uso que deles seja feito.
              </p>
              <p className="text-gray-700 mb-2">
                <strong>3.6.</strong> O Usuário compromete-se a notificar Serena imediatamente, por meio dos canais de contato mantidos por Serena na Plataforma, a respeito de qualquer uso não autorizado de sua conta. O Usuário será o único responsável pelas operações efetuadas em sua conta, uma vez que o acesso só será possível mediante a utilização de senha de seu exclusivo conhecimento.
              </p>
              <p className="text-gray-700 mb-2">
                <strong>3.7.</strong> Em nenhuma hipótese será permitida a cessão, a venda, o aluguel ou outra forma de transferência da conta. Não se permitirá, ainda, a criação de novos cadastros por pessoas cujos cadastros originais tenham sido cancelados por infrações às políticas de Serena.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">4. Modificações dos termos e condições gerais</h2>
              <p className="text-gray-700 mb-2">
                <strong>4.1.</strong> A Serena poderá alterar, a qualquer tempo e a seu único e exclusivo critério, estes Termos.
              </p>
              <p className="text-gray-700 mb-2">
                <strong>4.2.</strong> Caso ocorra quaisquer alterações nos Termos, os novos Termos entrarão em vigor em 10 (dez) dias depois de publicados na Plataforma. No prazo de 5 (cinco) dias contados da publicação das modificações, o Usuário deverá se manifestar, através dos canais de contato, caso não concorde com os termos alterados. Não havendo manifestação no prazo estipulado, entender-se-á que o Usuário aceitou tacitamente os novos Termos, e o contrato continuará vinculando as partes.
              </p>
              <p className="text-gray-700 mb-2">
                <strong>4.3.</strong> As alterações não vigorarão em relação as negociações entre Fornecedor e Comprador já firmadas ao tempo em que tais alterações sejam publicadas. Apenas para estes, os Termos valerão com a redação anterior.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">5. Práticas vedadas</h2>
              <p className="text-gray-700 mb-2">
                <strong>5.1.</strong> É terminantemente vedado aos Usuários, entre outras atitudes previstas nestes Termos, manipular, direta ou indiretamente, os preços de Fornecimento anunciados.
              </p>
              <p className="text-gray-700 mb-2">
                <strong>5.2.</strong> Os Usuários não poderão: (i) obter, guardar, divulgar, comercializar e/ou utilizar dados pessoais sobre outros Usuários para quaisquer fins; (ii) usar meios automáticos, incluindo spiders, robôs, crawlers, ferramentas de captação de dados ou similares para baixar dados do site (exceto ferramentas de busca na Internet e arquivos públicos não comerciais); (iii) burlar, ou tentar burlar, de qualquer forma que seja, o sistema, mecanismo e/ou a plataforma do site.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">6. Violação no sistema ou da base de dados</h2>
              <p className="text-gray-700 mb-2">
                <strong>6.1.</strong> É vedada a utilização de dispositivo, software ou outro recurso que possa interferir nas atividades e nas operações de Plataforma, bem como nos anúncios, nas descrições, nas contas ou em seus bancos de dados. Qualquer intromissão, tentativa de, ou atividade que viole ou contrarie as leis de direito de propriedade intelectual e as proibições estipuladas nestes Termos tornará o responsável passível de sofrer os efeitos das ações legais pertinentes, bem como das sanções aqui previstas, sendo ainda responsável por indenizar Serena ou seus Usuários por eventuais danos causados.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">7. Sanções</h2>
              <p className="text-gray-700 mb-2">
                <strong>7.1.</strong> Sem prejuízo de outras medidas, Serena poderá, a seu exclusivo critério e sem necessidade de prévia anuência dos ou comunicação aos Usuários, advertir, suspender ou cancelar, temporária ou permanentemente, o cadastro do Usuário, podendo aplicar sanção que impacte negativamente em sua reputação, a qualquer tempo, iniciando as ações legais cabíveis e suspendendo a prestação de seus Fornecimento, se: (i) o Usuário não cumprir qualquer dispositivo destes Termos e as demais políticas de Serena; (ii) descumprir com seus deveres de Usuário; (iii) praticar atos delituosos ou criminais; (iv) não puder ser verificada a identidade do Usuário, qualquer informação fornecida por ele esteja incorreta ou se as informações prestadas levarem a crer que o cadastro seja falso ou de pessoa diversa; (v) Serena entender que a contratação ou qualquer outra atitude do Usuário tenham causado algum dano a terceiros ou a Serena ou tenham a potencialidade de assim o fazer.
              </p>
              <p className="text-gray-700 mb-2">
                <strong>7.2.</strong> Serena se reserva o direito de, a qualquer momento e a seu exclusivo critério, solicitar o envio de qualquer documento que comprove a veracidade das informações cadastrais.
              </p>
              <p className="text-gray-700 mb-2">
                <strong>7.3.</strong> Em caso de requisição de documentos, quaisquer prazos determinados nestes Termos só serão aplicáveis a partir da data de recebimento dos documentos solicitados ao Fornecedor pela Serena.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">8. Responsabilidades</h2>
              <p className="text-gray-700 mb-2">
                <strong>8.1.</strong> Em nenhum caso Serena será responsável pelo lucro cessante ou por qualquer outro dano e/ou prejuízo que o Usuário possa sofrer devido às negociações não realizadas por meio de Plataforma.
              </p>
              <p className="text-gray-700 mb-2">
                <strong>8.2.</strong> A Serena se reserva o direito de auxiliar e cooperar com qualquer autoridade judicial ou órgão governamental, podendo enviar informações cadastrais ou negociais de seus Usuários, quando considerar que seu auxilio ou cooperação sejam necessários para proteger seus Usuários, funcionários, colaboradores, administradores, sócios ou qualquer pessoa que possa ser prejudicada pela ação ou omissão combatida.
              </p>
              <p className="text-gray-700 mb-2">
                <strong>8.3.</strong> Estes Termos não geram nenhum contrato de sociedade, de mandato, de franquia, de comercialização ou relação de trabalho entre a Serena e o Usuário.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">9. Problemas decorrente do uso do sistema</h2>
              <p className="text-gray-700 mb-2">
                <strong>9.1.</strong> Serena não se responsabiliza por qualquer dano, vício, defeitos técnicos/operacionais, prejuízo ou perda sofridos pelo Usuário em razão de ato ou fato externo a Serena.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">10. Mandato</h2>
              <p className="text-gray-700 mb-2">
                <strong>10.1.</strong> Caso os Usuários estejam vinculados na Plataforma à empresa consultora independente ("Consultoria"), estes desde já outorgaram poderes especiais e específicos para a respectiva empresa representá-los na Plataforma, nos termos do Art. 653 e seguintes do Código Civil Brasileiro.
              </p>
              <p className="text-gray-700 mb-2">
                <strong>10.2.</strong> Sendo aplicável a cláusula 11.1 acima e caso seja autorizado o nível de permissão "Gestão Completa" pelos Usuários, a Consultoria poderá firmar operações de compra e venda de energia elétrica no mercado de curto prazo em nome de seus respectivos Usuários.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">11. Propriedade intelectual e links</h2>
              <p className="text-gray-700 mb-2">
                <strong>11.1.</strong> O uso comercial da expressão "Serena" como marca, nome empresarial ou nome de domínio, bem como os logos, marcas, insígnias, conteúdo das telas relativas ao Fornecimento da Plataforma e o conjunto de programas, bancos de dados, redes e arquivos que permitem que o Usuário acesse e use sua conta, são propriedade de Serena e estão protegidos pelas leis e pelos tratados internacionais de direito autoral, de marcas, de patentes, de modelos e de desenhos industriais. O uso indevido e a reprodução total ou parcial dos referidos conteúdos são proibidos, salvo com autorização expressa de Serena.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-serena-darkblue mb-4">12. Legislação aplicável e foro de eleição</h2>
              <p className="text-gray-700 mb-2">
                <strong>12.1.</strong> Todos os itens destes Termos são regidos pelas leis vigentes na República Federativa do Brasil. Para todos os assuntos referentes à interpretação, ao cumprimento ou a qualquer outro questionamento relacionado a estes Termos, as partes concordam em se submeter ao Foro da Comarca de São Paulo.
              </p>
            </section>
          </div>
        </div>
      </div>

      <Footer />
    </main>
  );
}
