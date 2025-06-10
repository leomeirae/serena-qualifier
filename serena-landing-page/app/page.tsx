'use client';

import { ABTestingProvider } from '@/components/ABTestingProvider';
import Footer from '@/components/Footer';
import Image from 'next/image';
import Link from 'next/link';
import { useState } from 'react';

export default function Home() {
  // Verificar se há um parâmetro de sucesso na URL
  const hasSuccessParam = typeof window !== 'undefined' && window.location.search.includes('success=true');
  const [clientType, setClientType] = useState<'empresa' | 'casa'>('casa');
  const [formData, setFormData] = useState({
    nomeCompleto: '',
    whatsapp: '',
    valorContaLuz: '',
    consentimentoLGPD: false
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formSuccess, setFormSuccess] = useState(hasSuccessParam);

  const handleClientTypeChange = (type: 'empresa' | 'casa') => {
    setClientType(type);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  // Função para lidar com o envio do formulário via Google Apps Script
  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); // Previne o comportamento padrão do formulário

    // Validação básica dos campos
    if (!formData.nomeCompleto || !formData.whatsapp || !formData.valorContaLuz || !formData.consentimentoLGPD) {
      alert('Por favor, preencha todos os campos obrigatórios.');
      return;
    }

    // Validação do valor da conta (mínimo R$ 200)
    const valorConta = Number(formData.valorContaLuz.replace(/[^\d,.-]/g, '').replace(',', '.'));
    if (isNaN(valorConta) || valorConta < 200) {
      alert('O valor mínimo da conta de luz deve ser R$ 200.');
      return;
    }

    // Mostrar o spinner de carregamento
    setIsSubmitting(true);

    try {
      // Preparar os dados para envio conforme esperado pelo Apps Script
      const dataToSubmit = {
        nomeCompleto: formData.nomeCompleto,
        whatsapp: formData.whatsapp,
        valorContaLuz: formData.valorContaLuz,
        tipoCliente: clientType
      };

      console.log('Enviando dados para o Google Apps Script:', dataToSubmit);

      // Obter a URL do Apps Script do ambiente
      const PROXY_URL = "/api/form-submit";


      // Enviar os dados para o proxy PHP
      const response = await fetch(PROXY_URL, {
        method: 'POST',
        
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dataToSubmit),
      });

      // Verificar a resposta
      if (!response.ok) {
        const errorText = await response.text().catch(() => 'Erro desconhecido');
        console.error('Erro na resposta do Apps Script:', errorText);
        throw new Error(`Falha ao enviar dados: ${response.status} ${response.statusText}`);
      }

      // Processar a resposta JSON
      const responseData = await response.json().catch(() => ({ status: 'error', message: 'Erro ao processar resposta' }));
      console.log('Resposta do Google Apps Script:', responseData);

      // Verificar o status da resposta
      if (responseData.status === 'success') {
        // Salvar também no localStorage como backup
        try {
          const savedLeads = JSON.parse(localStorage.getItem('serena_leads') || '[]');
          savedLeads.push({
            ...dataToSubmit,
            timestamp: new Date().toISOString()
          });
          localStorage.setItem('serena_leads', JSON.stringify(savedLeads));
          console.log('Dados salvos no localStorage como backup');
        } catch (localError) {
          console.error('Erro ao salvar no localStorage:', localError);
        }

        // Mostrar mensagem de sucesso
        setFormSuccess(true);

        // Limpar o formulário
        setFormData({
          nomeCompleto: '',
          whatsapp: '',
          valorContaLuz: '',
          consentimentoLGPD: false
        });
      } else {
        throw new Error(responseData.message || 'Erro ao salvar dados');
      }
    } catch (error) {
      console.error('Erro ao enviar formulário:', error);
      alert('Ocorreu um erro ao enviar seus dados. Por favor, tente novamente.');

      // Tenta salvar no localStorage como fallback em caso de erro
      try {
        const savedLeads = JSON.parse(localStorage.getItem('serena_leads') || '[]');
        savedLeads.push({
          ...formData,
          tipoCliente: clientType,
          timestamp: new Date().toISOString()
        });
        localStorage.setItem('serena_leads', JSON.stringify(savedLeads));
        console.log('Dados salvos no localStorage como fallback após erro');
      } catch (localError) {
        console.error('Erro ao salvar no localStorage:', localError);
      }
    } finally {
      // Esconder o spinner de carregamento
      setIsSubmitting(false);
    }
  };

  return (
    <ABTestingProvider>
      <main>
        <section className="hero">
          <div className="container mx-auto px-4 md:px-6 relative">
            {/* Header */}
            <div className="flex justify-between items-center pt-6">
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

            <div className="hero-content">
              <div className="flex flex-col md:flex-row gap-8 items-start md:items-center justify-between">
                {/* Formulário */}
                <div className="form-container z-10">
                  <div className="bg-white/95 backdrop-blur-sm p-6 md:p-8 rounded-xl shadow-serena">
                    {formSuccess ? (
                      <div className="flex flex-col items-center justify-center text-center py-8 h-full">
                        <div className="mb-6 text-secondary-500">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <div className="max-w-md mx-auto">
                          <h3 className="text-xl font-bold text-gray-800 mb-4">Dados enviados com sucesso!</h3>
                          <p className="text-gray-600 mb-8">
                            Obrigado pelo seu interesse! Entraremos em contato pelo WhatsApp informado em breve com detalhes sobre como economizar na sua conta de energia.
                          </p>
                          <button
                            onClick={() => setFormSuccess(false)}
                            className="py-3 px-6 bg-secondary-400 hover:bg-secondary-500 text-white font-medium rounded-full shadow-serena-green transition-all duration-300"
                          >
                            Enviar novos dados
                          </button>
                        </div>
                      </div>
                    ) : (
                      <>
                        <h2 className="text-2xl md:text-3xl font-bold text-primary-500 mb-4 text-center">
                          Pague menos na sua conta de luz
                        </h2>
                        <p className="text-center text-gray-700 mb-6">
                          Milhares de pessoas já deram o primeiro passo para reduzir a conta de energia.
                        </p>
                        <form
                          className="space-y-6"
                          onSubmit={handleFormSubmit}
                        >
                        <div className="space-y-4">
                          <div>
                            <p className="font-medium mb-2">Quero economizar para:</p>
                            <div className="grid grid-cols-2 gap-4">
                              <button
                                type="button"
                                className={`py-3 px-4 font-medium rounded-lg transition-all ${
                                  clientType === 'empresa'
                                    ? 'bg-primary-500 text-white'
                                    : 'border-2 border-primary-500 text-primary-500 hover:bg-primary-500 hover:text-white'
                                }`}
                                onClick={() => handleClientTypeChange('empresa')}
                              >
                                Minha empresa
                              </button>
                              <button
                                type="button"
                                className={`py-3 px-4 font-medium rounded-lg transition-all ${
                                  clientType === 'casa'
                                    ? 'bg-primary-500 text-white'
                                    : 'border-2 border-primary-500 text-primary-500 hover:bg-primary-500 hover:text-white'
                                }`}
                                onClick={() => handleClientTypeChange('casa')}
                              >
                                Minha casa
                              </button>
                            </div>
                          </div>

                          <div>
                            <label htmlFor="nomeCompleto" className="block text-sm font-medium text-gray-700 mb-1">
                              Nome completo <span className="text-primary-500">*</span>
                            </label>
                            <input
                              type="text"
                              id="nomeCompleto"
                              name="nomeCompleto"
                              value={formData.nomeCompleto}
                              onChange={handleInputChange}
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                              placeholder="Digite seu nome completo"
                              required
                            />
                          </div>

                          <div>
                            <label htmlFor="whatsapp" className="block text-sm font-medium text-gray-700 mb-1">
                              WhatsApp <span className="text-primary-500">*</span>
                            </label>
                            <input
                              type="tel"
                              id="whatsapp"
                              name="whatsapp"
                              value={formData.whatsapp}
                              onChange={handleInputChange}
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                              placeholder="(00) 00000-0000"
                              required
                            />
                          </div>

                          <div>
                            <label htmlFor="valorContaLuz" className="block text-sm font-medium text-gray-700 mb-1">
                              Qual o valor da sua conta de luz por mês? <span className="text-primary-500">*</span>
                            </label>
                            <p className="text-sm text-gray-500 mb-2">
                              <em>Valor mínimo: <strong>R$ 200</strong></em>
                            </p>
                            <input
                              type="text"
                              id="valorContaLuz"
                              name="valorContaLuz"
                              value={formData.valorContaLuz}
                              onChange={handleInputChange}
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                              placeholder="R$ 0,00"
                              required
                            />
                          </div>

                          <div className="flex items-start">
                            <div className="flex items-center h-5">
                              <input
                                id="consentimentoLGPD"
                                name="consentimentoLGPD"
                                type="checkbox"
                                checked={formData.consentimentoLGPD}
                                onChange={handleInputChange}
                                className="h-4 w-4 text-primary-500 border-gray-300 rounded focus:ring-primary-500"
                                required
                              />
                            </div>
                            <div className="ml-3 text-xs">
                              <label htmlFor="consentimentoLGPD" className="text-gray-700">
                                Ao continuar você concorda em receber contato da Serena e com os
                                {' '}
                                <Link href="/termos-de-uso" className="text-primary-500 hover:text-primary-600">
                                  Termos e Condições
                                </Link>.
                              </label>
                            </div>
                          </div>
                        </div>

                        <div className="text-center text-xs text-gray-600 mb-4">
                          Fique tranquilo, seus dados estão seguros.
                        </div>

                        <button
                          type="submit"
                          disabled={isSubmitting}
                          className="w-full py-4 px-6 bg-secondary-400 hover:bg-secondary-500 text-white font-medium rounded-full shadow-serena-green transition-all duration-300"
                        >
                          {isSubmitting ? (
                            <>
                              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                              Processando...
                            </>
                          ) : (
                            'Saiba como economizar energia'
                          )}
                        </button>

                        <div className="text-center text-xs text-gray-600 mt-4">
                          Sem spam. Apenas informações úteis sobre como reduzir sua conta.
                        </div>
                      </form>
                      </>
                    )}
                  </div>
                </div>

                {/* Conteúdo */}
                <div className="content-container z-10 text-white">
                  <div className="space-y-6">
                    <h1 className="hero-title">
                      Você está pagando mais do que deveria na sua conta de luz.
                    </h1>

                    <p className="hero-subtitle">
                    Economize até 18% com uma solução limpa e acessível com zero de investimento. Confirme seus dados e saiba mais.
                    </p>

                    <ul className="space-y-3 mt-6">
                      <li className="flex items-center">
                        <span className="w-2 h-2 bg-white rounded-full mr-2 flex-shrink-0"></span>
                        <span className="hero-benefit"><strong>Não pague caro por energia</strong> — mude para solar com zero de investimento</span>
                      </li>
                      <li className="flex items-center">
                        <span className="w-2 h-2 bg-white rounded-full mr-2 flex-shrink-0"></span>
                        <span className="hero-benefit"><strong>Sua casa na energia solar</strong> sem obra, sem investimento</span>
                      </li>
                      <li className="flex items-center">
                        <span className="w-2 h-2 bg-white rounded-full mr-2 flex-shrink-0"></span>
                        <span className="hero-benefit">Exclusivo, digital e prático — <strong>aderir nunca foi tão fácil</strong></span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Selos e Benefícios */}
        <section className="bg-white py-12">
          <div className="container mx-auto px-4">
            <div className="flex flex-col md:flex-row items-center justify-between gap-8">
              <div className="w-full md:w-1/2 space-y-6">
                <div className="flex items-center gap-4">
                  <Image
                    src="/images/lgpd-selo-1.svg"
                    alt="Selo LGPD"
                    width={80}
                    height={80}
                    className="h-16 w-auto"
                  />
                  <Image
                    src="/images/selo_ReclameAqui_RA1000.svg"
                    alt="Selo Reclame Aqui"
                    width={80}
                    height={80}
                    className="h-16 w-auto"
                  />
                </div>

                <div className="space-y-4">
                  <div className="benefit-item">
                    <span className="benefit-dot"></span>
                    <span>Garantimos seu <strong>desconto</strong> todos os meses</span>
                  </div>
                  <div className="benefit-item">
                    <span className="benefit-dot"></span>
                    <span><strong>Energia limpa</strong>, renovável e acessível</span>
                  </div>
                  <div className="benefit-item">
                    <span className="benefit-dot"></span>
                    <span>Contratação <strong>digital</strong>, <strong>rápida</strong> e <strong>segura</strong></span>
                  </div>
                </div>
              </div>

              <div className="w-full md:w-1/2">
                <div className="flex justify-center">
                  <Image
                    src="/images/selinho_18_desc-png.avif"
                    alt="Economia na conta de luz"
                    width={400}
                    height={300}
                    className="rounded-lg shadow-serena"
                  />
                </div>
              </div>
            </div>
          </div>
        </section>

        <Footer />
      </main>
    </ABTestingProvider>
  );
}
