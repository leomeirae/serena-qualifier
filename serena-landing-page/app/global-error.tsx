'use client';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body>
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
          <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full">
            <h2 className="text-2xl font-bold text-red-600 mb-4">Algo deu errado!</h2>
            <p className="text-gray-700 mb-4">
              Ocorreu um erro ao carregar a página. Por favor, tente novamente.
            </p>
            <p className="text-gray-500 text-sm mb-4">
              Detalhes do erro: {error.message}
            </p>
            <button
              onClick={() => reset()}
              className="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded"
            >
              Tentar novamente
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}