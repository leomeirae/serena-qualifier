
import { useState, FormEvent, ChangeEvent } from 'react';
import { useRouter } from 'next/navigation';
import Input from './ui/Input';
import Select from './ui/Select';
import Checkbox from './ui/Checkbox';
import Alert from './ui/Alert';
import { validateForm, maskWhatsApp } from '@/utils/validation';
import { submitToGoogleSheets, FormData } from '@/utils/api';
import { useABTesting } from './ABTestingProvider';

const billValueOptions = [
  { value: 'R$100 - R$200', label: 'R$100 - R$200' },
  { value: 'R$201 - R$500', label: 'R$201 - R$500' },
  { value: 'Acima de R$500', label: 'Acima de R$500' },
];

export default function LeadForm() {
  // Get A/B testing context for tracking conversions
  const { headlineVariant, trackConversion } = useABTesting();
  const router = useRouter();

  // Estado do formulário
  const [formData, setFormData] = useState<FormData & { tipoCliente: 'empresa' | 'casa' }>({
    nomeCompleto: '',
    email: '', // Campo opcional
    whatsapp: '',
    valorContaLuz: '',
    consentimentoLGPD: false,
    tipoCliente: 'casa',
  });

  // Estado de erros de validação
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Estado de submissão
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState<{ success: boolean; message: string } | null>(null);

  // Manipuladores de eventos
  const handleInputChange = (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;

    // Special handling for account value
    if (name === 'valorContaLuz') {
      // Only allow numbers, commas, and dots
      const sanitizedValue = value.replace(/[^\d,.-]/g, '');
      setFormData(prev => ({ ...prev, [name]: sanitizedValue }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }

    // Limpa o erro do campo quando o usuário começa a digitar novamente
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleWhatsAppChange = (e: ChangeEvent<HTMLInputElement>) => {
    const maskedValue = maskWhatsApp(e.target.value);
    setFormData(prev => ({ ...prev, whatsapp: maskedValue }));

    // Limpa o erro do campo quando o usuário começa a digitar novamente
    if (errors.whatsapp) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors.whatsapp;
        return newErrors;
      });
    }
  };

  const handleCheckboxChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFormData(prev => ({ ...prev, [name]: checked }));

    // Limpa o erro do campo quando o usuário marca o checkbox
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // Valida o formulário
    const validation = validateForm(formData);

    if (!validation.isValid) {
      setErrors(validation.errors);
      return;
    }

    // Inicia o processo de submissão
    setIsSubmitting(true);
    setErrors({});

    try {
      console.log('Enviando dados do formulário:', formData);

      // Usar a função simplificada para enviar para o Google Sheets
      const result = await submitToGoogleSheets(formData);

      if (result.success) {
        // Rastreia a conversão
        trackConversion(headlineVariant.id);

        // Redireciona para a página de agradecimento após um pequeno delay
        setTimeout(() => {
          router.push('/obrigado');
        }, 1000);

        // Atualiza o estado com o resultado (será exibido brevemente antes do redirect)
        setSubmitResult({
          success: true,
          message: 'Redirecionando...'
        });

        // Limpa o formulário
        setFormData({
          nomeCompleto: '',
          email: '',
          whatsapp: '',
          valorContaLuz: '',
          consentimentoLGPD: false,
          tipoCliente: 'casa',
        });
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      console.error('Erro detalhado ao enviar formulário:', error);
      setSubmitResult({
        success: false,
        message: 'Ocorreu um erro ao enviar seus dados. Por favor, tente novamente.'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Limpa a mensagem de resultado
  const clearSubmitResult = () => {
    setSubmitResult(null);
  };

  return (
    <div id="formulario">
        {submitResult && (
          <Alert
            type={submitResult.success ? 'success' : 'error'}
            message={submitResult.message}
            onClose={clearSubmitResult}
          />
        )}

        <form
          id="form_cadastro"
          onSubmit={handleSubmit}
          className="max-w-md mx-auto p-6 md:p-8 backdrop-blur-md bg-white/80 rounded-lg shadow-lg"
        >
          <div className="text-center mb-6">
            <h2 className="text-xl font-bold text-primary-500 drop-shadow-sm">Confirme seus Dados</h2>
          </div>

          <div className="mb-6">
            <p className="font-medium mb-2 text-gray-800">Quero economizar para:</p>
            <div className="grid grid-cols-2 gap-4">
              <button
                type="button"
                className={`py-3 px-4 border-2 rounded-lg transition-all cursor-pointer ${
                  formData.tipoCliente === 'empresa'
                    ? 'bg-primary-500 text-white border-primary-500'
                    : 'border-primary-500 text-primary-500 hover:bg-primary-50'
                }`}
                onClick={() => setFormData(prev => ({ ...prev, tipoCliente: 'empresa' }))}
              >
                Minha empresa
              </button>
              <button
                type="button"
                className={`py-3 px-4 border-2 rounded-lg transition-all cursor-pointer ${
                  formData.tipoCliente === 'casa'
                    ? 'bg-primary-500 text-white border-primary-500'
                    : 'border-primary-500 text-primary-500 hover:bg-primary-50'
                }`}
                onClick={() => setFormData(prev => ({ ...prev, tipoCliente: 'casa' }))}
              >
                Minha casa
              </button>
            </div>
          </div>

          <Input
            label={<>Nome completo <span className="text-primary-500">*</span></>}
            id="nomeCompleto"
            name="nomeCompleto"
            type="text"
            placeholder="Digite seu nome completo"
            value={formData.nomeCompleto}
            onChange={handleInputChange}
            error={errors.nomeCompleto}
            required
          />



          <Input
            label={<>Seu WhatsApp <span className="text-primary-500">*</span></>}
            id="whatsapp"
            name="whatsapp"
            type="tel"
            placeholder="Seu WhatsApp"
            value={formData.whatsapp}
            onChange={handleWhatsAppChange}
            error={errors.whatsapp}
            required
            maxLength={15}
          />

          <div className="mb-5">
            <label htmlFor="valorContaLuz" className="block text-sm font-medium text-gray-800 mb-1.5 drop-shadow-sm">
              Qual o valor da sua conta de luz por mês? <span className="text-primary-500">*</span>
            </label>
            <p className="text-sm text-gray-700 mb-2 drop-shadow-sm">
              <em>Valor mínimo: <strong>R$ 200</strong></em>
            </p>
            <div className="relative">
              <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-700 font-medium">R$</span>
              <input
                type="text"
                inputMode="numeric"
                id="valorContaLuz"
                name="valorContaLuz"
                value={formData.valorContaLuz}
                onChange={handleInputChange}
                placeholder="0,00"
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-secondary-400 focus:border-secondary-400 outline-none transition"
                required
                aria-required="true"
              />
            </div>
            {errors.valorContaLuz && (
              <p className="mt-1.5 text-sm text-red-600 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                {errors.valorContaLuz}
              </p>
            )}
          </div>

          <Checkbox
            label={
              <span className="text-xs">
                Ao continuar você concorda em receber contato da Serena e com os Termos e Condições.
              </span>
            }
            id="consentimentoLGPD"
            name="consentimentoLGPD"
            checked={formData.consentimentoLGPD}
            onChange={handleCheckboxChange}
            error={errors.consentimentoLGPD}
            required
          />

          <div className="mt-6">
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full px-6 py-3 bg-secondary-400 hover:bg-secondary-500 text-white font-medium rounded-full shadow-serena-green transition-all duration-300 text-center flex items-center justify-center"
            >
              {isSubmitting ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processando...
                </>
              ) : (
                <>
                  Comece a economizar
                </>
              )}
            </button>
          </div>
        </form>
      </div>
  );
}
