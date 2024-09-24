import { tailwindConfig } from 'pdap-design-system';

/** @type {import('tailwindcss').Config} */
export default {
	...tailwindConfig,
	content: ['index.html', 'src/**/*.{vue,js,css}'],
	plugins: [require('@tailwindcss/container-queries')],
	theme: {
		...tailwindConfig.theme,
		containers: {
			xs: '480px',
			sm: '640px',
			md: '768px',
			lg: '1024px',
			xl: '1280px',
		},
	},
};
