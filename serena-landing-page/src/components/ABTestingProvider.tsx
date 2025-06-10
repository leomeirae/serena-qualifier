'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { HeadlineVariant, getRandomHeadlineVariant, headlineVariants } from '@/utils/headlines';

// Create context for A/B testing
type ABTestingContextType = {
  headlineVariant: HeadlineVariant;
  trackImpression: (variantId: string) => void;
  trackConversion: (variantId: string) => void;
};

const ABTestingContext = createContext<ABTestingContextType | undefined>(undefined);

// Default variant to prevent hydration mismatch
const DEFAULT_VARIANT = headlineVariants[0];

// Provider component
export function ABTestingProvider({ children }: { children: React.ReactNode }) {
  // Start with default variant during SSR
  const [headlineVariant, setHeadlineVariant] = useState<HeadlineVariant>(DEFAULT_VARIANT);
  const [isClientReady, setIsClientReady] = useState(false);

  // Initialize on client-side only to prevent hydration mismatch
  useEffect(() => {
    // Mark client as ready
    setIsClientReady(true);
    
    // Check if we already have a variant stored in session storage
    const storedVariantId = sessionStorage.getItem('ab_headline_variant');
    
    let selectedVariant: HeadlineVariant;
    
    if (storedVariantId) {
      // If we have a stored variant, use it
      selectedVariant = headlineVariants.find(v => v.id === storedVariantId) || getRandomHeadlineVariant();
    } else {
      // If we don't have a stored variant, get a random one
      selectedVariant = getRandomHeadlineVariant();
      sessionStorage.setItem('ab_headline_variant', selectedVariant.id);
    }
    
    // Update the variant only if it's different from the default
    if (selectedVariant.id !== DEFAULT_VARIANT.id) {
      setHeadlineVariant(selectedVariant);
    }
    
    // Track impression only after client is ready
    trackImpression(selectedVariant.id);
  }, []);

  // Track impression (view) of a variant
  const trackImpression = (variantId: string) => {
    // Only run on client-side
    if (typeof window === 'undefined') return;
    
    // In a real implementation, this would send data to an analytics service
    console.log(`Impression tracked for variant: ${variantId}`);
    
    // Example implementation with Google Analytics
    if ('gtag' in window) {
      // @ts-ignore
      window.gtag('event', 'headline_impression', {
        'variant_id': variantId,
        'headline': headlineVariant.title,
      });
    }
  };

  // Track conversion (e.g., form submission) for a variant
  const trackConversion = (variantId: string) => {
    // Only run on client-side
    if (typeof window === 'undefined') return;
    
    // In a real implementation, this would send data to an analytics service
    console.log(`Conversion tracked for variant: ${variantId}`);
    
    // Example implementation with Google Analytics
    if ('gtag' in window) {
      // @ts-ignore
      window.gtag('event', 'headline_conversion', {
        'variant_id': variantId,
        'headline': headlineVariant.title,
      });
    }
  };

  return (
    <ABTestingContext.Provider value={{ headlineVariant, trackImpression, trackConversion }}>
      {children}
    </ABTestingContext.Provider>
  );
}

// Hook to use the A/B testing context
export function useABTesting() {
  const context = useContext(ABTestingContext);
  if (context === undefined) {
    throw new Error('useABTesting must be used within an ABTestingProvider');
  }
  return context;
}
