'use client';

/**
 * Configuração do URL do Kestra - ajuste conforme seu ambiente
 */
const KESTRA_BASE_URL = 'http://localhost:8080'; // URL local do Kestra

/**
 * Manipula o envio do formulário para o webhook Kestra
 * @param {Event} event - O evento de submissão do formulário
 */
async function submitForm(event) {
  // Previne o comportamento padrão do formulário
  event.preventDefault();
  
  // Extrai dados dos campos do formulário
  const formData = {
    name: document.getElementById('name').value,
    email: document.getElementById('email').value,
    phone: document.getElementById('phone').value,
    city: document.getElementById('city').value
  };
  
  // Obtém o botão de envio e define o estado de carregamento
  const submitButton = document.getElementById('submit-button') || event.target.querySelector('button[type="submit"]');
  if (submitButton) {
    submitButton.disabled = true;
    submitButton.textContent = 'Enviando...';
  }
  
  // Mostra mensagem de carregamento
  const feedbackElement = document.getElementById('form-feedback');
  feedbackElement.textContent = 'Enviando...';
  feedbackElement.className = 'loading-message';
  
  try {
    // Constrói o URL completo do webhook do Kestra
    const webhookUrl = `${KESTRA_BASE_URL}/api/v1/executions/webhook/serena/lead-capture-workflow/capture`;
    
    // Envia requisição HTTP POST
    const response = await fetch(webhookUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    });
    
    // Verifica se a requisição foi bem-sucedida
    if (response.ok) {
      // Exibe mensagem de sucesso
      feedbackElement.textContent = "Formulário enviado com sucesso!";
      feedbackElement.className = "success-message";
      
      // Limpa campos do formulário após envio bem-sucedido
      document.getElementById('name').value = '';
      document.getElementById('email').value = '';
      document.getElementById('phone').value = '';
      document.getElementById('city').value = '';
      
      // Remove automaticamente a mensagem de sucesso após 5 segundos
      setTimeout(() => {
        feedbackElement.textContent = '';
        feedbackElement.className = '';
      }, 5000);
    } else {
      // Exibe mensagem de erro
      feedbackElement.textContent = "Erro ao enviar formulário. Por favor, tente novamente.";
      feedbackElement.className = "error-message";
      
      // Remove automaticamente a mensagem de erro após 5 segundos
      setTimeout(() => {
        feedbackElement.textContent = '';
        feedbackElement.className = '';
      }, 5000);
    }
  } catch (error) {
    // Trata quaisquer erros que ocorram durante a operação de fetch
    console.error('Erro ao enviar formulário:', error);
    feedbackElement.textContent = "Erro ao enviar formulário. Por favor, tente novamente.";
    feedbackElement.className = "error-message";
    
    // Remove automaticamente a mensagem de erro após 5 segundos
    setTimeout(() => {
      feedbackElement.textContent = '';
      feedbackElement.className = '';
    }, 5000);
  } finally {
    // Restaura o estado do botão independentemente do resultado
    if (submitButton) {
      submitButton.disabled = false;
      submitButton.textContent = 'Enviar';
    }
  }
}

// Nota: Se você encontrar problemas de CORS, considere usar uma API route Next.js para proxy
// Crie app/api/submit-form/route.ts que encaminha requisições para o Kestra
// E altere webhookUrl para '/api/submit-form'

export default submitForm;
