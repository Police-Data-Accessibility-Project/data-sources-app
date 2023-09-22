const { defineConfig } = require('@vue/cli-service');
module.exports = defineConfig({
	transpileDependencies: true,
	publicPath: 'client/',
	devServer: {
		allowedHosts: 'all',
	},
	outputDir: 'dist',
});
