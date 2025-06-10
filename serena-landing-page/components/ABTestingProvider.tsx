'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Defina os tipos para as variantes de teste
type HeadlineVariant = {
  id: string;
  text: string;
};

// Defina o tipo para o contexto
type ABTestingContextType = {
  headlineVariant: HeadlineVariant;
  trackConversion: (variantId: string) => void;
};

// Variantes de teste para os títulos
const headlineVariants: HeadlineVariant[] = [
  {
    id: 'variant-a',
    text: 'Economize até 20% na sua conta de luz com energia limpa',
  },
  {
    id: 'variant-b',
    text: 'Reduza sua conta de luz e ajude o planeta com energia solar',
  },
];

// Crie o contexto
const ABTestingContext = createContext<ABTestingContextType | undefined>(undefined);

// Função simples para selecionar uma variante aleatoriamente
const getRandomVariant = (): HeadlineVariant => {
  const randomIndex = Math.floor(Math.random() * headlineVariants.length);
  return headlineVariants[randomIndex];
};

// Provedor do contexto
export function ABTestingProvider({ children }: { children: ReactNode }) {
  // Estado para armazenar a variante selecionada
  const [headlineVariant, setHeadlineVariant] = useState<HeadlineVariant>(headlineVariants[0]);

  // Efeito para selecionar uma variante quando o componente montar
  useEffect(() => {
    try {
      console.log('Inicializando A/B Testing...');
      
      // Verifica se já existe uma variante armazenada no localStorage
      const storedVariantId = localStorage.getItem('ab_headline_variant');
      
      if (storedVariantId) {
        // Se existir, usa a variante armazenada
        const storedVariant = headlineVariants.find(v => v.id === storedVariantId);
        if (storedVariant) {
          setHeadlineVariant(storedVariant);
          console.log('Usando variante armazenada:', storedVariant.id);
          return;
        }
      }
      
      // Se não existir ou for inválida, seleciona uma nova variante
      const newVariant = getRandomVariant();
      setHeadlineVariant(newVariant);
      localStorage.setItem('ab_headline_variant', newVariant.id);
      console.log('Nova variante selecionada:', newVariant.id);
    } catch (error) {
      console.error('Erro ao inicializar A/B Testing:', error);
      // Em caso de erro, usa a primeira variante como fallback
      setHeadlineVariant(headlineVariants[0]);
    }
  }, []);

  // Função para rastrear conversões
  const trackConversion = (variantId: string) => {
    try {
      console.log(`Conversão registrada para variante: ${variantId}`);
      // Aqui você poderia implementar a lógica para enviar dados para um sistema de analytics
    } catch (error) {
      console.error('Erro ao rastrear conversão:', error);
    }
  };

  return (
    <ABTestingContext.Provider value={{ headlineVariant, trackConversion }}>
      {children}
    </ABTestingContext.Provider>
  );
}

// Hook personalizado para usar o contexto
export function useABTesting() {
  const context = useContext(ABTestingContext);
  if (context === undefined) {
    throw new Error('useABTesting deve ser usado dentro de um ABTestingProvider');
  }
  return context;
}