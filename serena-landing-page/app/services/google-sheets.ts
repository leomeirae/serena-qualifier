import { GoogleSpreadsheet } from 'google-spreadsheet';
import { JWT } from 'google-auth-library';
import type { FormData } from '@/utils/api';

// Cache para o cliente autenticado
let authClient: JWT | null = null;
let authExpiry = 0;

/**
 * Obtém um cliente JWT autenticado para o Google Sheets
 * Implementa cache para evitar autenticações desnecessárias
 */
export async function getAuthClient(): Promise<JWT> {
  const now = Date.now();

  // Se o cliente ainda é válido, retorna-o
  if (authClient && authExpiry > now) {
    console.log('Serviço Google Sheets: Usando cliente autenticado em cache');
    return authClient;
  }

  console.log('Serviço Google Sheets: Criando novo cliente autenticado');

  // Caso contrário, cria um novo cliente
  const credentials = {
    client_email: process.env.GOOGLE_SHEETS_CLIENT_EMAIL,
    private_key: process.env.GOOGLE_SHEETS_PRIVATE_KEY?.replace(/\\n/g, '\n'),
  };

  if (!credentials.client_email || !credentials.private_key) {
    throw new Error('Credenciais incompletas para autenticação com o Google Sheets');
  }

  authClient = new JWT({
    email: credentials.client_email,
    key: credentials.private_key,
    scopes: ['https://www.googleapis.com/auth/spreadsheets'],
  });

  // Define a expiração para 55 minutos (tokens JWT do GCP geralmente duram 1 hora)
  authExpiry = now + (55 * 60 * 1000);

  return authClient;
}

/**
 * Adiciona uma linha à planilha do Google Sheets
 * Implementa retry para lidar com falhas temporárias
 */
export async function appendToSheet(formData: FormData, retries = 3): Promise<{ success: boolean; message: string; rowNumber?: number }> {
  try {
    console.log('Serviço Google Sheets: Iniciando adição de linha à planilha');

    const SPREADSHEET_ID = process.env.GOOGLE_SHEETS_SPREADSHEET_ID;
    const SHEET_NAME = 'Página1';

    if (!SPREADSHEET_ID) {
      throw new Error('ID da planilha não configurado');
    }

    // Obter cliente autenticado
    const auth = await getAuthClient();

    // Inicializar o documento
    const doc = new GoogleSpreadsheet(SPREADSHEET_ID, auth);

    // Carregar informações do documento
    console.log('Serviço Google Sheets: Carregando documento');
    await doc.loadInfo();
    console.log(`Serviço Google Sheets: Documento carregado: ${doc.title}`);

    // Obter a planilha pelo título ou criar uma nova se não existir
    let sheet = doc.sheetsByTitle[SHEET_NAME];

    if (!sheet) {
      console.log(`Serviço Google Sheets: Planilha "${SHEET_NAME}" não encontrada, criando nova planilha`);
      sheet = await doc.addSheet({ title: SHEET_NAME, headerValues: ['Data/Hora', 'Nome Completo', 'WhatsApp', 'Valor Conta Luz', 'Tipo Cliente'] });
    } else {
      console.log(`Serviço Google Sheets: Planilha encontrada: ${sheet.title}`);
    }

    // Verificar se a planilha tem os cabeçalhos corretos
    const headerRow = await sheet.headerValues;
    console.log('Serviço Google Sheets: Cabeçalhos atuais:', headerRow);

    // Se não tiver cabeçalhos, adicionar
    if (!headerRow || headerRow.length === 0) {
      console.log('Serviço Google Sheets: Adicionando cabeçalhos à planilha');
      await sheet.setHeaderRow(['Data/Hora', 'Nome Completo', 'WhatsApp', 'Valor Conta Luz', 'Tipo Cliente']);
    }

    // Preparar os dados para inserção
    const rowData = {
      'Data/Hora': new Date().toISOString(),
      'Nome Completo': formData['Nome Completo'],
      'WhatsApp': formData['WhatsApp'],
      'Valor Conta Luz': formData['Valor Conta Luz'],
      'Tipo Cliente': formData['Tipo Cliente'] || 'casa'
    };

    console.log('Serviço Google Sheets: Dados preparados para inserção:', rowData);

    // Adicionar linha à planilha
    console.log('Serviço Google Sheets: Adicionando linha à planilha');
    const addedRow = await sheet.addRow(rowData);
    console.log('Serviço Google Sheets: Linha adicionada com sucesso, ID:', addedRow._rowNumber);

    return {
      success: true,
      message: 'Dados salvos com sucesso no Google Sheets',
      rowNumber: addedRow._rowNumber
    };
  } catch (error) {
    console.error('Serviço Google Sheets: Erro ao adicionar linha:', error);

    // Implementação de retry para falhas temporárias
    if (retries > 0 && isRetryableError(error)) {
      console.log(`Serviço Google Sheets: Tentativa falhou, tentando novamente. Restantes: ${retries-1}`);
      await new Promise(resolve => setTimeout(resolve, 1000)); // Espera 1 segundo antes de tentar novamente
      return appendToSheet(formData, retries - 1);
    }

    return {
      success: false,
      message: `Falha ao salvar dados no Google Sheets: ${error instanceof Error ? error.message : 'Erro desconhecido'}`
    };
  }
}

/**
 * Verifica se o erro permite retry
 */
function isRetryableError(error: any): boolean {
  // Códigos de erro que geralmente são temporários
  const retryCodes = [429, 500, 503];

  // Verifica se o erro tem um código HTTP
  if (error && error.code && retryCodes.includes(Number(error.code))) {
    return true;
  }

  // Verifica se é um erro de rede ou timeout
  if (error && error.message && (
    error.message.includes('network') ||
    error.message.includes('timeout') ||
    error.message.includes('ECONNRESET') ||
    error.message.includes('ETIMEDOUT')
  )) {
    return true;
  }

  return false;
}
