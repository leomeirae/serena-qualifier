"use client";

import Image from 'next/image';

export default function Benefits() {
  return (
    <section className="bg-white py-6">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="w-full md:w-1/2 space-y-6">
            <div className="flex items-center gap-4">
              <Image
                src="/images/lgpd-selo-1.svg"
                alt="Selo LGPD"
                width={80}
                height={80}
                className="h-16 w-auto"
              />
              <Image
                src="/images/selo_ReclameAqui_RA1000.svg"
                alt="Selo Reclame Aqui"
                width={80}
                height={80}
                className="h-16 w-auto"
              />
            </div>

            <div className="space-y-4">
              <div className="benefit-item">
                <span className="benefit-dot"></span>
                <span>Garantimos seu <strong>desconto</strong> todos os meses</span>
              </div>
              <div className="benefit-item">
                <span className="benefit-dot"></span>
                <span><strong>Energia limpa</strong>, renovável e acessível</span>
              </div>
              <div className="benefit-item">
                <span className="benefit-dot"></span>
                <span>Contratação <strong>digital</strong>, <strong>rápida</strong> e <strong>segura</strong></span>
              </div>
            </div>
          </div>

          <div className="w-full md:w-1/2">
            <div className="flex justify-center">
              <Image
                src="/images/economia-grafico.webp"
                alt="Economia na conta de luz"
                width={400}
                height={300}
                className="rounded-lg shadow-serena"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
