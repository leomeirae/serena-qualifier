"use client";

import Link from 'next/link';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-50 py-8 md:py-10">
      <div className="container mx-auto px-4 text-center">
        <p className="text-sm text-gray-600 mb-2">
          Você receberá as informações por onde for mais fácil para você.
        </p>
        <p className="text-sm text-gray-600 mb-3">
          © {currentYear} Serena Energia. Todos os direitos reservados.
        </p>
        <p className="text-xs text-gray-500 mb-2">
          <Link href="/politica-de-privacidade" className="text-primary-500 hover:text-primary-600 text-sm">
            Política de Privacidade
          </Link>
          {' | '}
          <Link href="/termos-de-uso" className="text-primary-500 hover:text-primary-600 text-sm">
            Termos de Uso
          </Link>
        </p>
      </div>
    </footer>
  );
}
