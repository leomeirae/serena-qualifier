
// Tipo para os dados do formulário
export type FormData = {
  nomeCompleto?: string;
  whatsapp?: string;
  valorContaLuz?: string;
  consentimentoLGPD?: boolean;
  tipoCliente?: 'empresa' | 'casa';
  // Formato usado pelo formulário
  'Nome Completo'?: string;
  'WhatsApp'?: string;
  'Valor Conta Luz'?: string;
  'Tipo Cliente'?: string;
  'Data/Hora'?: string;
};

// Função para enviar os dados do formulário para o Google Sheets
export const submitToGoogleSheets = async (formData: FormData): Promise<{ success: boolean; message: string }> => {
  try {
    // Converte os dados para o formato esperado pela API
    const dataToSubmit = {
      'Data/Hora': new Date().toISOString(),
      'Nome Completo': formData.nomeCompleto,
      'WhatsApp': formData.whatsapp,
      'Valor Conta Luz': formData.valorContaLuz,
      'Tipo Cliente': formData.tipoCliente === 'empresa' ? 'Empresa' : 'Residencial'
    };

    console.log('Preparando dados para envio ao Google Sheets:', dataToSubmit);

    // Envia para o Google Sheets via API Route
    console.log('Enviando para Google Sheets via API Route');
    let success = false;

    try {
      // Tentativa 1: Rota principal
      console.log('Tentando rota principal para Google Sheets');
      const sheetsResponse = await fetch('/api/save-to-sheets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dataToSubmit),
      });

      if (sheetsResponse.ok) {
        const sheetsResponseData = await sheetsResponse.json().catch(() => ({ success: true }));
        console.log('Resposta da rota principal do Google Sheets:', sheetsResponseData);
        success = true;
      } else {
        const errorData = await sheetsResponse.json().catch(() => ({ error: 'Erro ao processar resposta' }));
        console.error('Erro ao salvar no Google Sheets (rota principal):', errorData);

        // Tentativa 2: Rota alternativa
        console.log('Tentando rota alternativa para Google Sheets');
        try {
          const altSheetsResponse = await fetch('/api/save-to-sheets-alt', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(dataToSubmit),
          });

          if (altSheetsResponse.ok) {
            const altSheetsResponseData = await altSheetsResponse.json().catch(() => ({ success: true }));
            console.log('Resposta da rota alternativa do Google Sheets:', altSheetsResponseData);
            success = true;
          } else {
            const altErrorData = await altSheetsResponse.json().catch(() => ({ error: 'Erro ao processar resposta' }));
            console.error('Erro na rota alternativa do Google Sheets:', altErrorData);

            // Tentativa 3: Nova rota usando google-spreadsheet
            console.log('Tentando nova rota V2 para Google Sheets');
            try {
              const v2SheetsResponse = await fetch('/api/save-to-sheets-v2', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify(dataToSubmit),
              });

              if (v2SheetsResponse.ok) {
                const v2Result = await v2SheetsResponse.json().catch(() => ({ success: true }));
                console.log('Resposta da rota V2 do Google Sheets:', v2Result);
                success = true;
              } else {
                const v2ErrorData = await v2SheetsResponse.json().catch(() => ({ error: 'Erro ao processar resposta' }));
                console.error('Erro na rota V2 do Google Sheets:', v2ErrorData);
              }
            } catch (v2SheetsError) {
              console.error('Erro ao tentar rota V2:', v2SheetsError);
            }
          }
        } catch (altSheetsError) {
          console.error('Erro detalhado ao chamar API alternativa de Google Sheets:', altSheetsError);
        }
      }
    } catch (sheetsError) {
      console.error('Erro detalhado ao chamar API de Google Sheets:', sheetsError);
    }

    // Mesmo que o Google Sheets falhe, tentamos salvar localmente
    try {
      // Salvar em localStorage como fallback
      const savedLeads = JSON.parse(localStorage.getItem('serena_leads') || '[]');
      savedLeads.push({
        ...dataToSubmit,
        timestamp: new Date().toISOString()
      });
      localStorage.setItem('serena_leads', JSON.stringify(savedLeads));
      console.log('Dados salvos no localStorage como fallback');
      success = true;
    } catch (localError) {
      console.error('Erro ao salvar no localStorage:', localError);
    }

    if (success) {
      return {
        success: true,
        message: 'Obrigado! Entraremos em contato em breve.'
      };
    } else {
      throw new Error('Todas as tentativas de salvar os dados falharam');
    }
  } catch (error) {
    console.error('Erro detalhado ao enviar formulário:', error);
    return {
      success: false,
      message: 'Ocorreu um erro. Por favor, tente novamente.'
    };
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
