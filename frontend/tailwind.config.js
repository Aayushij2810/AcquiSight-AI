/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  "#eef6f7",
          100: "#d4eaed",
          200: "#a8d5da",
          300: "#6bb8c0",
          400: "#3d9ba6",
          500: "#2a7f8a",
          600: "#1f6470",
          700: "#184f59",
          800: "#123d45",
          900: "#0c2c32",
        },
        surface: {
          DEFAULT: "#0f1117",
          card:    "#161b22",
          raised:  "#1c2330",
          border:  "#21262d",
        }
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      animation: {
        "count-up": "countUp 1s ease-out forwards",
      }
    },
  },
  plugins: [],
};
