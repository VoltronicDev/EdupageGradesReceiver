/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./pages/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        muted: {
          DEFAULT: '#94a3b8',
          foreground: '#cbd5e1'
        },
        glass: {
          surface: 'rgba(148, 163, 184, 0.08)',
          highlight: 'rgba(148, 163, 184, 0.18)'
        },
        accent: {
          500: '#7c3aed',
          400: '#a78bfa'
        }
      },
      backdropFilter: {
        none: 'none'
      },
      borderRadius: {
        xl: '1rem'
      },
      boxShadow: {
        glass: '0 10px 45px rgba(0,0,0,0.25)'
      }
    }
  },
  plugins: [],
};
