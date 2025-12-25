/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],

    safelist: [
      {
        pattern:
          /(bg|border|text)-(emerald|amber|rose|sky|violet|teal|fuchsia|lime)-(50|200|400|900)/,
      },
    ],

  theme: {
    extend: {},
  },

  plugins: [],
};
