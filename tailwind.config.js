/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Dark mode colors (ChatGPT style)
        dark: {
          bg: '#212121',
          sidebar: '#171717',
          input: '#2f2f2f',
          hover: '#2a2a2a',
          border: '#404040',
          text: '#ececec',
          textSecondary: '#b4b4b4',
        },
        // Light mode colors
        light: {
          bg: '#ffffff',
          sidebar: '#f7f7f8',
          input: '#ffffff',
          hover: '#f7f7f8',
          border: '#e5e5e5',
          text: '#0d0d0d',
          textSecondary: '#6e6e80',
        },
      },
    },
  },
  plugins: [],
}
