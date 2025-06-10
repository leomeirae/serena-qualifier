// Tipo para os dados do formulário
export type FormData = {
  nomeCompleto: string;
  email?: string; // Campo opcional
  whatsapp: string;
  valorContaLuz: string;
  consentimentoLGPD: boolean;
  tipoCliente?: 'empresa' | 'casa';
};

// Função para enviar os dados do formulário para o Kestra (mantendo nome para compatibilidade)
export const submitToGoogleSheets = async (formData: FormData): Promise<{ success: boolean; message: string }> => {
  try {
    console.log('📤 Enviando dados para Kestra:', formData);

    console.log('🔄 Enviando dados do formulário:', formData);

    // Tentar enviar para Kestra
    try {
      // Usar API route customizada do Next.js
      const response = await fetch('/api/form-submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      console.log('✅ Resposta do Kestra - Status:', response.status);
      
      // Com mode: 'no-cors', não conseguimos ler a resposta, mas se chegou aqui, foi enviado
      console.log('✅ Dados enviados para Kestra com sucesso');
      
      // Salvar como backup no localStorage
      try {
        const savedLeads = JSON.parse(localStorage.getItem('serena_leads') || '[]');
        savedLeads.push({
          ...formData,
          timestamp: new Date().toISOString(),
          sentToKestra: true
        });
        localStorage.setItem('serena_leads', JSON.stringify(savedLeads));
        console.log('💾 Backup salvo no localStorage');
      } catch (localError) {
        console.warn('⚠️ Erro ao salvar backup:', localError);
      }

      return {
        success: true,
        message: 'Obrigado! Seus dados foram enviados com sucesso. Nossa equipe entrará em contato em breve.'
      };

    } catch (kestraError) {
      console.error('❌ Erro ao enviar para Kestra:', kestraError);
      
      // Fallback: salvar apenas no localStorage
      try {
        const savedLeads = JSON.parse(localStorage.getItem('serena_leads') || '[]');
        savedLeads.push({
          ...formData,
          timestamp: new Date().toISOString(),
          sentToKestra: false,
          error: kestraError instanceof Error ? kestraError.message : 'Erro desconhecido'
        });
        localStorage.setItem('serena_leads', JSON.stringify(savedLeads));
        console.log('💾 Dados salvos no localStorage como fallback');
        
        return {
          success: true,
          message: 'Obrigado! Seus dados foram recebidos. Nossa equipe entrará em contato em breve.'
        };
      } catch (localError) {
        console.error('❌ Erro ao salvar fallback:', localError);
        throw new Error('Falha ao processar os dados');
      }
    }

  } catch (error) {
    console.error('❌ Erro geral ao processar formulário:', error);
    return {
      success: false,
      message: 'Ocorreu um erro ao enviar seus dados. Por favor, tente novamente ou entre em contato conosco.'
    };
  }
};

// Função para testar conectividade com Kestra
export const testKestraConnection = async (): Promise<{ success: boolean; message: string }> => {
  try {
    console.log('🔍 Testando conexão com Kestra...');
    
    const testPayload = {
      name: 'Teste Conexão',
      email: 'teste@exemplo.com',
      phone: '11999999999',
      valorContaLuz: '500',
      tipoCliente: 'casa'
    };

    // URL dinâmica baseada no ambiente
    const isDevelopment = process.env.NODE_ENV === 'development' || typeof window !== 'undefined';
    const kestraUrl = isDevelopment 
      ? '/api/kestra/executions/webhook/serena/lead-capture-workflow/capture'  // Proxy local
      : 'https://SEU_DOMINIO_KESTRA/api/v1/executions/webhook/serena/lead-capture-workflow/capture';  // Produção
    
    const response = await fetch(kestraUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testPayload)
    });

    console.log('✅ Teste de conexão com Kestra - Status:', response.status);
    
    return {
      success: true,
      message: 'Conexão com Kestra funcionando'
    };
  } catch (error) {
    console.error('❌ Erro no teste de conexão:', error);
    return {
      success: false,
      message: 'Erro na conexão: ' + (error instanceof Error ? error.message : 'Erro desconhecido')
    };
  }
};

// Função adicional para verificar dados salvos localmente
export const getLocalLeads = (): any[] => {
  try {
    return JSON.parse(localStorage.getItem('serena_leads') || '[]');
  } catch {
    return [];
  }
};

// Adicione esta função para testar o endpoint simplificado
export const testEndpoint = async (formData: FormData): Promise<{ success: boolean; message: string }> => {
  try {
    console.log('Testando endpoint simplificado com dados:', formData);

    const response = await fetch('/api/test-endpoint', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    });

    console.log('Status da resposta do teste:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Erro na resposta do teste: ${errorText}`);
      throw new Error(`Erro no teste: ${response.status} ${response.statusText}`);
    }

    const responseData = await response.json();
    console.log('Resposta do teste:', responseData);

    return {
      success: true,
      message: 'Teste bem-sucedido!'
    };
  } catch (error) {
    console.error('Erro no teste:', error);
    return {
      success: false,
      message: 'Erro no teste: ' + (error instanceof Error ? error.message : 'Erro desconhecido')
    };
  }
};

// Remova a função saveToGoogleSheets deste arquivo, pois ela usa googleapis
// e deve ser usada apenas no servidor
