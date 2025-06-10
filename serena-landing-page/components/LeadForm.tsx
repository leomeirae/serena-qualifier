'use client';

import { useState, FormEvent, ChangeEvent } from 'react';
import { toast } from 'react-hot-toast';

type FormData = {
  nomeCompleto: string;
  email: string;
  whatsapp: string;
  faixaConta: string;
  consentimentoLGPD: boolean;
  tipoCliente: 'empresa' | 'casa';
};

const initialFormData: FormData = {
  nomeCompleto: '',
  email: '',
  whatsapp: '',
  faixaConta: '',
  consentimentoLGPD: false,
  tipoCliente: 'casa',
};

export default function LeadForm() {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Handle input changes
  const handleInputChange = (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;

    // Special handling for account value
    if (name === 'faixaConta') {
      // Only allow numbers, commas, and dots
      const sanitizedValue = value.replace(/[^\d,.-]/g, '');
      setFormData((prev) => ({ ...prev, [name]: sanitizedValue }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  // Handle checkbox change
  const handleCheckboxChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFormData((prev) => ({ ...prev, [name]: checked }));
  };

  // Format WhatsApp number with Brazilian mask
  const formatWhatsApp = (value: string) => {
    // Remove all non-digit characters
    const digits = value.replace(/\D/g, '');

    // Apply mask based on length
    if (digits.length <= 2) {
      return digits;
    } else if (digits.length <= 7) {
      return `(${digits.slice(0, 2)}) ${digits.slice(2)}`;
    } else {
      return `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7, 11)}`;
    }
  };

  // Handle WhatsApp input with mask
  const handleWhatsAppChange = (e: ChangeEvent<HTMLInputElement>) => {
    const formattedValue = formatWhatsApp(e.target.value);
    setFormData((prev) => ({ ...prev, whatsapp: formattedValue }));
  };

  // Form submission
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // Validate form
    if (!formData.nomeCompleto || !formData.email || !formData.whatsapp || !formData.faixaConta || !formData.consentimentoLGPD) {
      toast.error('Por favor, preencha todos os campos obrigatórios.');
      return;
    }

    // Validate account value (minimum R$ 200)
    const accountValue = Number(formData.faixaConta.replace(/[^\d,.-]/g, '').replace(',', '.'));
    if (isNaN(accountValue) || accountValue < 200) {
      toast.error('O valor mínimo da conta de luz deve ser R$ 200.');
      return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      toast.error('Por favor, insira um e-mail válido.');
      return;
    }

    // WhatsApp validation (should have at least 14 characters with the mask)
    if (formData.whatsapp.length < 14) {
      toast.error('Por favor, insira um número de WhatsApp válido.');
      return;
    }

    setIsSubmitting(true);

    try {
      // Prepare payload
      const payload = {
        ...formData,
        timestamp: new Date().toISOString(),
      };

      // Enviar dados diretamente para o Google Sheets via API Route
      const response = await fetch('/api/save-to-sheets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Falha ao enviar dados para o Google Sheets');
      }

      // Success
      toast.success('Obrigado! Entraremos em contato em breve.');
      setFormData(initialFormData);
    } catch (error) {
      console.error('Erro ao enviar formulário:', error);
      toast.error('Ocorreu um problema. Por favor, tente novamente.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle client type selection
  const handleClientTypeChange = (type: 'empresa' | 'casa') => {
    setFormData(prev => ({ ...prev, tipoCliente: type }));
  };

  return (
    <div className="bg-white bg-opacity-95 rounded-2xl shadow-md p-4 md:p-8 w-full max-w-md mx-auto relative">
      {/* Selo de desconto */}
      <div className="absolute -top-4 -right-4 w-20 h-20 z-10">
        <img
          src="/images/responsive/selinho_18_desc-png.avif"
          alt="Até 18% de desconto"
          className="w-full h-full object-contain"
        />
      </div>

      <h2 className="text-lg md:text-xl font-semibold text-gray-800 mb-3 md:mb-6 text-center">Confirme seus Dados</h2>

      <form onSubmit={handleSubmit} className="space-y-3 md:space-y-4">
        {/* Tipo de Cliente */}
        <div className="mb-3 md:mb-4">
          <p className="font-medium mb-2 text-sm md:text-base">Quero economizar para:</p>
          <div className="grid grid-cols-2 gap-2 md:gap-4">
            <button
              type="button"
              className={`py-2 md:py-3 px-2 md:px-4 border-2 rounded-lg transition-all cursor-pointer text-sm md:text-base ${
                formData.tipoCliente === 'empresa'
                  ? 'bg-primary-500 text-white border-primary-500'
                  : 'border-primary-500 text-primary-500 hover:bg-primary-50'
              }`}
              onClick={() => handleClientTypeChange('empresa')}
            >
              Minha empresa
            </button>
            <button
              type="button"
              className={`py-2 md:py-3 px-2 md:px-4 border-2 rounded-lg transition-all cursor-pointer text-sm md:text-base ${
                formData.tipoCliente === 'casa'
                  ? 'bg-primary-500 text-white border-primary-500'
                  : 'border-primary-500 text-primary-500 hover:bg-primary-50'
              }`}
              onClick={() => handleClientTypeChange('casa')}
            >
              Minha casa
            </button>
          </div>
        </div>

        {/* Nome Completo */}
        <div>
          <label htmlFor="nomeCompleto" className="block text-sm font-medium text-gray-700 mb-1">
            Nome Completo <span className="text-primary-500">*</span>
          </label>
          <input
            type="text"
            id="nomeCompleto"
            name="nomeCompleto"
            value={formData.nomeCompleto}
            onChange={handleInputChange}
            placeholder="Digite seu nome completo"
            className="w-full px-3 md:px-4 py-1.5 md:py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-secondary-400 focus:border-secondary-400 outline-none transition text-sm md:text-base"
            required
            aria-required="true"
          />
        </div>

        {/* E-mail */}
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
            E-mail <span className="text-primary-500">*</span>
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleInputChange}
            placeholder="Digite seu e-mail"
            className="w-full px-3 md:px-4 py-1.5 md:py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-secondary-400 focus:border-secondary-400 outline-none transition text-sm md:text-base"
            required
            aria-required="true"
          />
        </div>

        {/* WhatsApp */}
        <div>
          <label htmlFor="whatsapp" className="block text-sm font-medium text-gray-700 mb-1">
            WhatsApp <span className="text-primary-500">*</span>
          </label>
          <input
            type="tel"
            id="whatsapp"
            name="whatsapp"
            value={formData.whatsapp}
            onChange={handleWhatsAppChange}
            placeholder="(00) 00000-0000"
            className="w-full px-3 md:px-4 py-1.5 md:py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-secondary-400 focus:border-secondary-400 outline-none transition text-sm md:text-base"
            required
            aria-required="true"
          />
        </div>

        {/* Faixa da Conta de Luz */}
        <div>
          <label htmlFor="faixaConta" className="block text-sm font-medium text-gray-700 mb-1">
            Qual o valor da sua conta de luz por mês? <span className="text-primary-500">*</span>
          </label>
          <p className="text-xs text-gray-500 mb-2">
            <em>Valor mínimo: <strong>R$ 200</strong></em>
          </p>
          <div className="relative">
            <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">R$</span>
            <input
              type="text"
              inputMode="numeric"
              id="faixaConta"
              name="faixaConta"
              value={formData.faixaConta}
              onChange={handleInputChange}
              placeholder="0,00"
              className="w-full pl-10 pr-3 md:pr-4 py-1.5 md:py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-secondary-400 focus:border-secondary-400 outline-none transition text-sm md:text-base"
              required
              aria-required="true"
            />
          </div>
        </div>

        {/* Consentimento LGPD */}
        <div className="flex items-start mt-4">
          <div className="flex items-center h-5">
            <input
              type="checkbox"
              id="consentimentoLGPD"
              name="consentimentoLGPD"
              checked={formData.consentimentoLGPD}
              onChange={handleCheckboxChange}
              className="w-4 h-4 text-secondary-400 border-gray-300 rounded focus:ring-secondary-400"
              required
              aria-required="true"
            />
          </div>
          <label htmlFor="consentimentoLGPD" className="ml-2 text-sm text-gray-600">
            Autorizo a Serena Energia e seus representantes a me enviar mensagens. <span className="text-primary-500">*</span>
          </label>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-secondary-400 hover:bg-secondary-500 text-white font-medium py-2 md:py-2.5 px-4 rounded-lg transition duration-300 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-secondary-500 mt-4 md:mt-6 text-sm md:text-base"
        >
          {isSubmitting ? 'Enviando...' : 'Comece a economizar'}
        </button>
      </form>

      {/* Selo de certificação */}
      <div className="flex justify-center mt-6">
        <img
          src="/images/responsive/LP-selinho_v03-png.avif"
          alt="Certificação Serena Energia"
          className="h-16 object-contain"
        />
      </div>
    </div>
  );
}
