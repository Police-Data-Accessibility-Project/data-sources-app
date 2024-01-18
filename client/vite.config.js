import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import svgLoader from "vite-svg-loader";

export default defineConfig({
	plugins: [vue(), svgLoader({ defaultImport: "url" })],
	resolve: {
		paths: {
			"@/*": ["src/*"],
		},
	},
	test: {
		coverage: {
			all: true,
			include: ["src/**/*.vue", "src/util/**/*.js"],
			provider: "v8",
			reportsDirectory: "./coverage",
		},
		environment: "happy-dom",
		exclude: ["node_modules"],
		globals: true,
		include: ["src/**/{__tests__,__spec__}/*.test.js"],
		setupFiles: ["tools/testing/setup.js"],
	},
});
