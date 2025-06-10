"use client";

import Image from 'next/image';
import Link from 'next/link';

export default function Hero() {
  return (
    <section className="bg-white py-8 md:py-12 overflow-hidden">
      <div className="container mx-auto px-4 md:px-6 relative">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <Link href="/">
            <Image
              src="/images/logo.svg"
              alt="Serena Energia"
              width={150}
              height={50}
              className="h-10 w-auto"
              priority
            />
          </Link>
        </div>

        <div className="flex flex-col md:flex-row items-center justify-between gap-8 md:gap-16 mt-8 md:mt-12">
          <div className="flex-1 space-y-6 md:space-y-8 z-10">
            <div className="flex justify-start">
              <Image
                src="/images/header_aspas_cima.svg"
                alt="Aspas"
                width={30}
                height={30}
                className="h-6 w-auto mb-2"
              />
            </div>

            <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 leading-tight">
              Quer economizar na conta de energia?
            </h1>

            <p className="text-lg md:text-xl">
              Milhares de pessoas e negócios têm desconto garantido todos os meses com a Serena.
            </p>

            <p className="text-lg md:text-xl">
              Coloque a sua energia no lugar certo!
            </p>

            <ul className="space-y-3 mt-6">
              <li className="benefit-item">
                <span className="benefit-dot"></span>
                <span>Garantimos seu <strong>desconto</strong></span>
              </li>
              <li className="benefit-item">
                <span className="benefit-dot"></span>
                <span><strong>Energia limpa</strong>, renovável e acessível</span>
              </li>
              <li className="benefit-item">
                <span className="benefit-dot"></span>
                <span>Contratação <strong>digital</strong>, <strong>rápida</strong> e <strong>segura</strong></span>
              </li>
            </ul>
          </div>

          <div className="flex-1 w-full">
            <div className="bg-white p-6 md:p-8 rounded-xl shadow-serena">
              <h2 className="text-2xl md:text-3xl font-bold text-primary-500 mb-6 text-center">
                Contrate agora
              </h2>

              <form id="form_cadastro" className="space-y-6">
                <div className="space-y-4">
                  <div>
                    <p className="font-medium mb-2">Quero economizar para:</p>
                    <div className="grid grid-cols-2 gap-4">
                      <button type="button" className="py-3 px-4 border-2 border-primary-500 text-primary-500 font-medium rounded-lg hover:bg-primary-500 hover:text-white transition-all">
                        Minha empresa
                      </button>
                      <button type="button" className="py-3 px-4 bg-primary-500 text-white font-medium rounded-lg">
                        Minha casa
                      </button>
                    </div>
                  </div>

                  <div>
                    <label htmlFor="nome" className="block text-sm font-medium text-gray-700 mb-1">
                      Nome completo <span className="text-primary-500">*</span>
                    </label>
                    <input
                      type="text"
                      id="nome"
                      name="nome"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      placeholder="Digite seu nome completo"
                      required
                    />
                  </div>

                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                      Seu melhor e-mail <span className="text-primary-500">*</span>
                    </label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      placeholder="Digite seu e-mail"
                      required
                    />
                  </div>

                  <div>
                    <label htmlFor="whatsapp" className="block text-sm font-medium text-gray-700 mb-1">
                      Seu WhatsApp <span className="text-primary-500">*</span>
                    </label>
                    <input
                      type="tel"
                      id="whatsapp"
                      name="whatsapp"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      placeholder="Seu WhatsApp"
                      required
                    />
                  </div>

                  <div>
                    <label htmlFor="valorConta" className="block text-sm font-medium text-gray-700 mb-1">
                      Qual o valor da sua conta de luz por mês? <span className="text-primary-500">*</span>
                    </label>
                    <p className="text-sm text-gray-500 mb-2">
                      <em>Valor mínimo: <strong>R$ 200</strong></em>
                    </p>
                    <div className="bg-gray-100 p-4 rounded-lg text-center">
                      <span className="text-xl font-bold">R$ 0,00</span>
                    </div>
                  </div>

                  <div className="flex items-start">
                    <div className="flex items-center h-5">
                      <input
                        id="lgpd"
                        name="lgpd"
                        type="checkbox"
                        className="h-4 w-4 text-primary-500 border-gray-300 rounded focus:ring-primary-500"
                        required
                      />
                    </div>
                    <div className="ml-3 text-xs">
                      <label htmlFor="lgpd" className="text-gray-700">
                        Ao continuar você concorda em receber contato da Serena e com os
                        {' '}
                        <a href="#" className="text-primary-500 hover:text-primary-600">
                          Termos e Condições
                        </a>.
                      </label>
                    </div>
                  </div>
                </div>

                <button
                  type="submit"
                  className="w-full py-4 px-6 bg-secondary-400 hover:bg-secondary-500 text-white font-medium rounded-full shadow-serena-green transition-all duration-300"
                >
                  calcular desconto
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
