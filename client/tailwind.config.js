import { tailwindConfig } from "pdap-design-system";

/** @type {import('tailwindcss').Config} */
export default {
	...tailwindConfig,
	content: ["index.html", "src/**/*.{vue,js,css}"],
	plugins: [],
};
