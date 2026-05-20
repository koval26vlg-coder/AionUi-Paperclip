/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0A0A0B",
        foreground: "#FFFFFF",
        amber: {
          industrial: "#F59E0B",
        },
        cyan: {
          data: "#06B6D4",
        },
      },
      fontFamily: {
        sans: ["Space Grotesk", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      animation: {
        'kinetic-grid': 'grid 20s linear infinite',
      },
      keyframes: {
        grid: {
          '0%': { transform: 'translateY(0)' },
          '100%': { transform: 'translateY(100px)' },
        },
      },
    },
  },
  plugins: [],
}
