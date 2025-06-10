import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    console.log('Test Endpoint: Recebendo solicitação');
    const data = await request.json();
    console.log('Test Endpoint: Dados recebidos:', data);
    
    // Simplesmente retorna os dados recebidos
    return NextResponse.json({ 
      success: true,
      message: 'Dados recebidos com sucesso',
      receivedData: data
    });
  } catch (error) {
    console.error('Test Endpoint: Erro:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Falha ao processar dados',
        details: error instanceof Error ? error.message : 'Erro desconhecido'
      },
      { status: 500 }
    );
  }
}