import { NextResponse } from 'next/server';
import { google } from 'googleapis';

export async function POST(request: Request) {
  try {
    const formData = await request.json();

    // Configurações do Google Sheets
    const SPREADSHEET_ID = process.env.GOOGLE_SHEETS_SPREADSHEET_ID;
    const SHEET_NAME = 'Página1';
    const API_KEY = process.env.GOOGLE_SHEETS_API_KEY;

    // Verificar se temos o ID da planilha e a API key
    if (!SPREADSHEET_ID || !API_KEY) {
      throw new Error('ID da planilha ou API key não configurados');
    }

    // Usar a API key para autenticação simples (somente leitura)
    // Para escrita, precisamos usar o JWT ou OAuth2
    const sheets = google.sheets({
      version: 'v4',
      auth: API_KEY
    });

    // Para escrita, precisamos usar o JWT
    // Obter as credenciais do ambiente
    const credentials = {
      client_email: process.env.GOOGLE_SHEETS_CLIENT_EMAIL,
      private_key: process.env.GOOGLE_SHEETS_PRIVATE_KEY?.replace(/\\n/g, '\n'),
    };

    if (!credentials.private_key) {
      throw new Error('Chave privada não configurada');
    }

    const jwtClient = new google.auth.JWT(
      credentials.client_email,
      undefined,
      credentials.private_key,
      ['https://www.googleapis.com/auth/spreadsheets']
    );

    await jwtClient.authorize();

    const sheetsAuth = google.sheets({ version: 'v4', auth: jwtClient });

    // Prepara os dados para inserção
    const values = [
      [
        new Date().toISOString(), // Timestamp atual
        formData['Nome Completo'],
        formData['WhatsApp'],
        formData['Valor Conta Luz'],
        formData['Tipo Cliente'] || 'casa'
      ]
    ];

    // Adiciona os dados à planilha
    const response = await sheetsAuth.spreadsheets.values.append({
      spreadsheetId: SPREADSHEET_ID,
      range: `${SHEET_NAME}!A:E`,
      valueInputOption: 'USER_ENTERED',
      requestBody: {
        values,
      },
    });

    console.log('Dados salvos no Google Sheets com sucesso:', response.data);

    return NextResponse.json({
      success: true,
      message: 'Dados salvos com sucesso no Google Sheets'
    });
  } catch (error) {
    console.error('Erro ao salvar no Google Sheets:', error);
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