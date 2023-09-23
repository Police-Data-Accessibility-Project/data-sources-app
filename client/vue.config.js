const { defineConfig } = require('@vue/cli-service');
module.exports = defineConfig({
	transpileDependencies: true,
	publicPath: './data-sources-app-client',
	devServer: {
		allowedHosts: 'all',
	},
});
