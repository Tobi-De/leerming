/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    'leerming/templates/**/*.html',
    'node_modules/preline/dist/*.js',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#6b6969', // Muted Grayish Purple
          dark: '#4e4c4c', // Dark Grayish Purple for Dark Mode
        },
        secondary: {
          light: '#b7a57a', // Warm Taupe
          dark: '#8e8461', // Dark Taupe for Dark Mode
        },
        accent: {
          light: '#d99666', // Soft Coral
          dark: '#bb7e53', // Dark Coral for Dark Mode
        },
        background: {
          light: '#f0ede5', // Off-White
          dark: '#222222', // Dark Background for Dark Mode
        },
        "gray-dark": "#333333",
        neutral: {
          light: '#c8c3ba', // Light Gray
          dark: '#666666', // Dark Gray for Dark Mode
        },
        error: {
          light: '#ff6666', // Light Red
          dark: '#ff3333', // Dark Red for Dark Mode
        },
      },
    },
    fontFamily: {
      sans: [
        'Roboto', // Primary font
        'Open Sans',
        'Arial',
        'sans-serif',
      ],
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('preline/plugin'),
  ]
}
