/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "index.html",
    "src/**/*.{vue,js,css}",
  ],
  theme: {
    extend: {
      colors: {
				brand: {
					blue: {
						light: 'rgba(var(--color-brand-blue-light)/<alpha-value>)',
						medium: 'rgba(var(--color-brand-blue-medium)/<alpha-value>)',
					},
					gold: 'rgba(var(--color-brand-gold)/<alpha-value>)',
					wine: 'rgba(var(--color-brand-wine)/<alpha-value>)',
				},
				neutral: {
					50: 'rgba(var(--color-neutral-50)/<alpha-value>)',
					100: 'rgba(var(--color-neutral-100)/<alpha-value>)',
					200: 'rgba(var(--color-neutral-200)/<alpha-value>)',
					300: 'rgba(var(--color-neutral-300)/<alpha-value>)',
					400: 'rgba(var(--color-neutral-400)/<alpha-value>)',
					500: 'rgba(var(--color-neutral-500)/<alpha-value>)',
					600: 'rgba(var(--color-neutral-600)/<alpha-value>)',
					700: 'rgba(var(--color-neutral-700)/<alpha-value>)',
					800: 'rgba(var(--color-neutral-800)/<alpha-value>)',
					900: 'rgba(var(--color-neutral-900)/<alpha-value>)',
					950: 'rgba(var(--color-neutral-950)/<alpha-value>)',
				},
			},
    },
  },
  plugins: [],
}

