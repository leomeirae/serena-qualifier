// Validação de nome completo
export const validateName = (name: string): boolean => {
  // Nome deve ter pelo menos 3 caracteres e não conter números ou caracteres especiais (exceto espaços)
  const nameRegex = /^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$/;
  return name.trim().length >= 3 && nameRegex.test(name);
};

// Validação de email
export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Validação de WhatsApp (formato brasileiro)
export const validateWhatsApp = (whatsapp: string): boolean => {
  // Formato esperado: (XX) XXXXX-XXXX
  const whatsappRegex = /^\(\d{2}\)\s\d{5}-\d{4}$/;
  return whatsappRegex.test(whatsapp);
};

// Aplicar máscara ao número de WhatsApp
export const maskWhatsApp = (value: string): string => {
  // Remove todos os caracteres não numéricos
  const numbers = value.replace(/\D/g, '');

  // Aplica a máscara conforme o usuário digita
  if (numbers.length <= 2) {
    return numbers.replace(/^(\d{0,2})/, '($1');
  } else if (numbers.length <= 7) {
    return numbers.replace(/^(\d{2})(\d{0,5})/, '($1) $2');
  } else {
    return numbers.replace(/^(\d{2})(\d{5})(\d{0,4})/, '($1) $2-$3');
  }
};

// Validação do valor da conta de luz
export const validateBillValue = (value: string): boolean => {
  if (value === '') return false;

  // Convert to number, handling comma as decimal separator
  const numValue = Number(value.replace(/[^\d,.-]/g, '').replace(',', '.'));

  // Minimum value is R$ 200
  return !isNaN(numValue) && numValue >= 200;
};

// Validação do consentimento LGPD
export const validateConsent = (consent: boolean): boolean => {
  return consent === true;
};

// Validação completa do formulário
export const validateForm = (formData: {
  nomeCompleto: string;
  email?: string;
  whatsapp: string;
  valorContaLuz: string;
  consentimentoLGPD: boolean;
}): { isValid: boolean; errors: Record<string, string> } => {
  const errors: Record<string, string> = {};

  if (!validateName(formData.nomeCompleto)) {
    errors.nomeCompleto = 'Por favor, insira seu nome completo válido';
  }

  // Email é opcional, só valida se foi fornecido
  if (formData.email && formData.email.trim() !== '' && !validateEmail(formData.email)) {
    errors.email = 'Por favor, insira um email válido';
  }

  if (!validateWhatsApp(formData.whatsapp)) {
    errors.whatsapp = 'Por favor, insira um número de WhatsApp válido no formato (XX) XXXXX-XXXX';
  }

  if (!validateBillValue(formData.valorContaLuz)) {
    errors.valorContaLuz = 'O valor mínimo da conta de luz deve ser R$ 200';
  }

  if (!validateConsent(formData.consentimentoLGPD)) {
    errors.consentimentoLGPD = 'Você precisa concordar com os termos para prosseguir';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};
