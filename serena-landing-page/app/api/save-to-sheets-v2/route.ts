import { NextResponse } from 'next/server';
import type { FormData } from '../../utils/api';
import { appendToSheet } from '../../services/google-sheets';

export async function POST(request: Request) {
  try {
    console.log('API Route V2: Recebendo solicitação para salvar no Google Sheets');
    const formData = await request.json();
    console.log('API Route V2: Dados recebidos:', formData);

    // Usar o serviço dedicado para adicionar a linha à planilha
    const result = await appendToSheet(formData);

    if (result.success) {
      console.log('API Route V2: Dados salvos com sucesso, linha:', result.rowNumber);
      return NextResponse.json({
        success: true,
        message: 'Dados salvos com sucesso no Google Sheets (V2)',
        rowNumber: result.rowNumber
      });
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    console.error('API Route V2: Erro ao salvar no Google Sheets:', error);
    return NextResponse.json(
      {
        success: false,
        error: 'Falha ao salvar dados no Google Sheets (V2)',
        details: error instanceof Error ? error.message : 'Erro desconhecido'
      },
      { status: 500 }
    );
  }
}
