/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: '#1e293b',
          deep: '#0f172a',
          light: '#334155',
        },
        purple: {
          DEFAULT: '#7c3aed',
          light: '#a78bfa',
          dark: '#5b21b6',
        },
        teal: {
          DEFAULT: '#14b8a6',
          light: '#5eead4',
          dark: '#0f766e',
        }
      }
    },
  },
  plugins: [],
}
