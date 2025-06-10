
import { NextResponse } from 'next/server';
import { google } from 'googleapis';
import type { FormData } from '../../utils/api';

export async function POST(request: Request) {
  try {
    console.log('API Route: Recebendo solicitação para salvar no Google Sheets');
    const formData = await request.json();
    console.log('API Route: Dados recebidos:', formData);

    // Configurações do Google Sheets - Simplificado para teste
    const SPREADSHEET_ID = process.env.GOOGLE_SHEETS_SPREADSHEET_ID;
    const SHEET_NAME = 'Página1';

    console.log('API Route: Configurações:', {
      spreadsheetId: SPREADSHEET_ID,
      sheetName: SHEET_NAME
    });

    // Verificar se o ID da planilha existe
    if (!SPREADSHEET_ID) {
      throw new Error('ID da planilha não configurado');
    }

    // Método simplificado usando variáveis de ambiente
    console.log('API Route: Configurando autenticação');
    const credentials = {
      client_email: process.env.GOOGLE_SHEETS_CLIENT_EMAIL,
      private_key: process.env.GOOGLE_SHEETS_PRIVATE_KEY?.replace(/\\n/g, '\n'),
    };

    if (!credentials.private_key) {
      throw new Error('Chave privada não configurada');
    }

    if (!credentials.client_email) {
      throw new Error('Email do cliente não configurado');
    }

    const auth = new google.auth.JWT(
      credentials.client_email,
      undefined,
      credentials.private_key,
      ['https://www.googleapis.com/auth/spreadsheets']
    );

    console.log('API Route: Autenticação configurada, criando cliente do Google Sheets');
    const sheets = google.sheets({ version: 'v4', auth });

    // Prepara os dados para inserção conforme as colunas da planilha
    // Colunas: Data/Hora | Nome Completo | WhatsApp | Valor Conta Luz | Tipo Cliente
    const values = [
      [
        new Date().toISOString(), // Timestamp em formato ISO para consistência
        formData['Nome Completo'],
        formData['WhatsApp'],
        formData['Valor Conta Luz'],
        formData['Tipo Cliente'] || 'casa'
      ]
    ];

    console.log('API Route: Dados preparados para inserção:', values);

    // Adiciona os dados à planilha
    console.log('API Route: Enviando dados para o Google Sheets');
    const response = await sheets.spreadsheets.values.append({
      spreadsheetId: SPREADSHEET_ID,
      range: `${SHEET_NAME}!A:E`, // Ajustado para 5 colunas (A até E)
      valueInputOption: 'USER_ENTERED',
      requestBody: {
        values,
      },
    }).catch(async (appendError) => {
      console.error('API Route: Erro específico ao anexar dados:', appendError);

      // Verificar se a planilha existe
      try {
        const getResponse = await sheets.spreadsheets.get({
          spreadsheetId: SPREADSHEET_ID
        });
        console.log('API Route: Planilha existe, verificando abas disponíveis:',
          getResponse.data.sheets?.map(s => s.properties?.title).join(', '));
      } catch (getError) {
        console.error('API Route: Erro ao verificar planilha:', getError);
      }

      throw appendError;
    });

    console.log('API Route: Resposta completa da API:', JSON.stringify(response.data));
    console.log('API Route: Dados salvos no Google Sheets com sucesso:', response.data);

    return NextResponse.json({
      success: true,
      message: 'Dados salvos com sucesso no Google Sheets'
    });
  } catch (error) {
    console.error('API Route: Erro ao salvar no Google Sheets:', error);
    return NextResponse.json(
      {
        success: false,
        error: 'Falha ao salvar dados no Google Sheets',
        details: error instanceof Error ? error.message : 'Erro desconhecido'
      },
      { status: 500 }
    );
  }
}
