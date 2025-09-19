/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      boxShadow: {
        'soft': '0 10px 25px -10px rgba(0,0,0,0.15)'
      }
    },
  },
  plugins: [],
}
