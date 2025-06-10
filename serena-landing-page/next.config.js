/** @type {import('next').NextConfig} */
const nextConfig = {
  /* config options here */
  // Configuração diferente para dev vs produção
  output: process.env.NODE_ENV === 'production' ? 'export' : undefined,
  images: {
    domains: ['serena-energia.com.br', 'www.saasia.com.br', 'saasia.com.br'],
    unoptimized: true,
  },
  // Excluir diretórios de backup do build
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  // Definir variáveis de ambiente para o build
  env: {
    NEXT_PUBLIC_GOOGLE_SHEETS_APPS_SCRIPT_URL: process.env.NEXT_PUBLIC_GOOGLE_SHEETS_APPS_SCRIPT_URL,
  },
  
  // Configuração de rewrites para proxy durante desenvolvimento
  async rewrites() {
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/api/kestra/:path*',
          destination: 'http://localhost:8080/api/v1/:path*',
        },
      ];
    }
    return [];
  },
  // Configuração para lidar com módulos Node.js
  webpack: (config, { isServer }) => {
    if (!isServer) {
      // Não tente carregar módulos Node.js no lado do cliente
      config.resolve.fallback = {
        ...config.resolve.fallback,
        net: false,
        tls: false,
        fs: false,
        child_process: false,
        http: false,
        https: false,
        stream: false,
        crypto: false,
        os: false,
        path: false,
        zlib: false,
      };
    }
    return config;
  },
};

module.exports = nextConfig;
