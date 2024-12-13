import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import svgLoader from 'vite-svg-loader';
import VueRouter from 'unplugin-vue-router/vite';
import path from 'path';

export default defineConfig(({ mode }) => {
	loadEnv(mode, process.cwd(), '');

	return {
		plugins: [
			VueRouter({
				routesFolder: 'src/pages',
				exclude: ['**/_*/{*,_*}.*'],
				extendRoute(route) {
					// Add meta from meta map (see below)
					if (ROUTES_TO_META.has(route.name)) {
						route.meta = { ...route.meta, ...ROUTES_TO_META.get(route.name) };
					}

					if (route.fullPath.startsWith('/test/') && mode === 'production') {
						route.delete();
					}
				},
			}),
			vue(),
			svgLoader({ defaultImport: 'url' }),
		],
		resolve: {
			alias: {
				'@': path.resolve(__dirname, './src'),
			},
		},
		server: {
			port: 8888,
		},
		test: {
			coverage: {
				all: true,
				include: ['src/components/*.vue', 'src/util/**/*.js'],
				provider: 'v8',
				reportsDirectory: './coverage',
			},
			environment: 'happy-dom',
			exclude: ['node_modules'],
			globals: true,
			include: ['src/{components,util}/{__tests__,__spec__}/*.test.js'],
			setupFiles: ['tools/testing/setup.js'],
		},
	};
});

/**
 * To override or add meta to a route, add a tuple to this `Map` which contains the route as the zeroth index and the meta object as the first index
 * Defining in vite.config rather than util/router because of import issues.
 *
 * TODO: remove this nonsense and set up in <route> tags at the page level instead.
 */
const ROUTES_TO_META = new Map([
	[
		'/',
		{
			title: 'Police Data Accessibility Project - Search',
			metaTags: [
				{
					property: 'og:title',
					title: 'Police Data Accessibility Project - Search',
				},
			],
		},
	],
]);
