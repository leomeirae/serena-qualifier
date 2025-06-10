/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'primary': {
          50: '#fff5f4',
          100: '#ffe6e4',
          200: '#ffd1cd',
          300: '#ffb0a9',
          400: '#ff8177',
          500: '#ff5247', // Main primary color (coral)
          600: '#ff2f22',
          700: '#ff1a0a',
          800: '#e50d00',
          900: '#c30b00',
          950: '#670600',
        },
        'secondary': {
          50: '#f0fdf9',
          100: '#ccfaec',
          200: '#99f1d9',
          300: '#5ee3c0',
          400: '#31caa1', // Main secondary color (verde-água)
          500: '#1aad85',
          600: '#0e8c6b',
          700: '#0c7058',
          800: '#0c5a47',
          900: '#0b4a3c',
          950: '#052922',
        },
        'serena': {
          coral: '#ff5247',
          green: '#31caa1',
          darkred: '#e50d00',
          lightgreen: '#5ee3c0',
          gray: '#64748b',
          lightgray: '#f1f5f9',
        },
      },
      fontFamily: {
        inter: ['var(--font-inter)', 'sans-serif'],
        sans: ['var(--font-inter)', 'ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
      boxShadow: {
        'serena': '0 4px 20px rgba(255, 82, 71, 0.08)',
        'serena-lg': '0 10px 30px rgba(255, 82, 71, 0.12)',
        'serena-xl': '0 20px 40px rgba(255, 82, 71, 0.15)',
        'serena-inner': 'inset 0 2px 4px 0 rgba(255, 82, 71, 0.05)',
        'serena-green': '0 4px 20px rgba(49, 202, 161, 0.08)',
      },
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}
