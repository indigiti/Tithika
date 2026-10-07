/** Production Tailwind build for the standalone Choghadiya surface. */
module.exports = {
  content: ['./choghadiya.php', './assets/app.js'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        card: '0 18px 55px rgba(45,32,20,.08)',
        float: '0 22px 70px rgba(38,24,63,.18)',
      },
    },
  },
  plugins: [],
};
