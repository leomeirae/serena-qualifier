import Link from 'next/link';

export default function ObrigadoPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-center">
            <h1 className="text-2xl font-bold text-primary-600">
              ☀️ Serena Energia
            </h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex items-center justify-center min-h-[80vh] px-4">
        <div className="max-w-2xl mx-auto text-center">
          {/* Success Icon */}
          <div className="mb-8">
            <div className="mx-auto w-24 h-24 bg-green-100 rounded-full flex items-center justify-center">
              <svg 
                className="w-12 h-12 text-green-600" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M5 13l4 4L19 7" 
                />
              </svg>
            </div>
          </div>

          {/* Thank You Message */}
          <div className="bg-white/80 backdrop-blur-md rounded-xl shadow-lg p-8 md:p-12">
            <h1 className="text-3xl md:text-4xl font-bold text-primary-600 mb-6">
              Obrigado! 🎉
            </h1>
            
            <p className="text-lg md:text-xl text-gray-700 mb-8 leading-relaxed">
              Seus dados foram recebidos com sucesso! Nossa equipe de especialistas 
              em energia solar entrará em contato com você em breve para apresentar 
              sua simulação personalizada.
            </p>

            {/* Next Steps */}
            <div className="bg-primary-50 rounded-lg p-6 mb-8">
              <h2 className="text-xl font-semibold text-primary-700 mb-4">
                Próximos passos:
              </h2>
              <ul className="text-left space-y-3 text-gray-700">
                <li className="flex items-start">
                  <span className="text-secondary-500 font-bold mr-3">1.</span>
                  Analisaremos seu perfil de consumo
                </li>
                <li className="flex items-start">
                  <span className="text-secondary-500 font-bold mr-3">2.</span>
                  Criaremos uma simulação personalizada
                </li>
                <li className="flex items-start">
                  <span className="text-secondary-500 font-bold mr-3">3.</span>
                  Entraremos em contato via WhatsApp em até 24h
                </li>
                <li className="flex items-start">
                  <span className="text-secondary-500 font-bold mr-3">4.</span>
                  Apresentaremos sua economia estimada
                </li>
              </ul>
            </div>

            {/* CTA Button */}
            <Link
              href="/"
              className="inline-block px-8 py-4 bg-secondary-400 hover:bg-secondary-500 text-white font-semibold rounded-full shadow-lg transition-all duration-300 transform hover:scale-105"
            >
              ← Voltar ao início
            </Link>
          </div>

          {/* Additional Info */}
          <div className="mt-8 text-sm text-gray-600">
            <p>
              Dúvidas? Entre em contato conosco pelo WhatsApp{' '}
              <span className="font-semibold text-primary-600">(11) 99999-9999</span>
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white/80 backdrop-blur-md mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-600">
            <p>© 2024 Serena Energia. Todos os direitos reservados.</p>
          </div>
        </div>
      </footer>
    </div>
  );
} 