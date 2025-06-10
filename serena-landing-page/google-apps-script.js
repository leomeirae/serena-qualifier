// Configuração da planilha
const SPREADSHEET_ID = '1GHqLJCI0dEEsMPLmq3VMJQ5XNcPFNFi-q9lKFSNlaNk';
const SHEET_NAME = 'Leads Serena';

// Versão da API: 2024-05-19

// Função para lidar com requisições POST
function doPost(e) {
  try {
    // Obter e analisar os dados JSON da requisição
    const data = JSON.parse(e.postData.contents);

    // Abrir a planilha e a aba específica
    const spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
    let sheet = spreadsheet.getSheetByName(SHEET_NAME);

    // Se a aba não existir, criar uma nova
    if (!sheet) {
      sheet = spreadsheet.insertSheet(SHEET_NAME);
      // Adicionar cabeçalhos
      sheet.appendRow(['Data/Hora', 'Nome Completo', 'WhatsApp', 'Valor Conta Luz', 'Tipo Cliente']);
    }

    // Preparar os dados para inserção
    const timestamp = new Date().toISOString();
    const rowData = [
      timestamp,
      data.nomeCompleto || '',
      data.whatsapp || '',
      data.valorContaLuz || '',
      data.tipoCliente || 'casa'
    ];

    // Adicionar os dados à planilha
    sheet.appendRow(rowData);

    // Retornar resposta como JSON
    return ContentService.createTextOutput(JSON.stringify({
      status: 'success',
      message: 'Dados salvos com sucesso',
      timestamp: timestamp
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    // Retornar resposta de erro como JSON
    return ContentService.createTextOutput(JSON.stringify({
      status: 'error',
      message: 'Erro ao processar requisição: ' + error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

// Função para lidar com requisições GET (restrita apenas para testes internos)
function doGet(e) {
  // Verificar se a requisição tem um token de segurança
  const token = e && e.parameter && e.parameter.token;

  // Se não tiver token ou o token for inválido, retornar erro
  if (!token || token !== 'serena_energia_2024_secret') {
    return ContentService.createTextOutput(JSON.stringify({
      status: 'error',
      message: 'Acesso não autorizado'
    })).setMimeType(ContentService.MimeType.JSON);
  }

  // Se o token for válido, retornar status da API
  return ContentService.createTextOutput(JSON.stringify({
    status: 'success',
    message: 'API ativa e funcionando',
    timestamp: new Date().toISOString()
  })).setMimeType(ContentService.MimeType.JSON);
}
