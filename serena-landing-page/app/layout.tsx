import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Serena Energia – Landing de Desconto",
  description: "Economize na conta de luz com Serena Energia. Preencha seus dados e receba descontos garantidos.",
  manifest: '/site.webmanifest',
  icons: {
    icon: [
      { url: '/images/favicon/favicon.ico' },
      { url: '/images/favicon/favicon.svg', type: 'image/svg+xml' },
    ],
    apple: { url: '/images/favicon/apple-touch-icon.png', type: 'image/png' },
    other: [
      { url: '/images/favicon/favicon-96x96.png', type: 'image/png', sizes: '96x96' },
      { url: '/images/favicon/web-app-manifest-192x192.png', type: 'image/png', sizes: '192x192' },
      { url: '/images/favicon/web-app-manifest-512x512.png', type: 'image/png', sizes: '512x512' },
    ],
  },
};

export function generateViewport() {
  return {
    themeColor: '#ff5247',
    viewport: "width=device-width, initial-scale=1",
  };
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className={`scroll-smooth ${inter.variable}`}>
      <body className="font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
