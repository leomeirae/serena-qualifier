import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.json();
    console.log('📥 Recebido no API route:', formData);

    // Mapear dados para o formato esperado pelo Kestra
    const kestraPayload = {
      name: formData.nomeCompleto,
      email: formData.email || '',
      phone: formData.whatsapp,
      valorContaLuz: formData.valorContaLuz,
      tipoCliente: formData.tipoCliente || 'casa'
    };

    console.log('🔄 Enviando para Kestra:', kestraPayload);

    // Enviar para Kestra
    const kestraResponse = await fetch('http://localhost:8080/api/v1/executions/webhook/serena/lead-capture-workflow/capture', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(kestraPayload)
    });

    if (!kestraResponse.ok) {
      throw new Error(`Kestra error: ${kestraResponse.status}`);
    }

    const kestraResult = await kestraResponse.json();
    console.log('✅ Resposta do Kestra:', kestraResult);

    return NextResponse.json({
      status: 'success',
      message: 'Dados enviados com sucesso!',
      executionId: kestraResult.id
    });

  } catch (error) {
    console.error('❌ Erro no API route:', error);
    return NextResponse.json({
      status: 'error',
      message: 'Erro ao processar os dados'
    }, { status: 500 });
  }
} 