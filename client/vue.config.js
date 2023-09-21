const { defineConfig } = require('@vue/cli-service');
module.exports = defineConfig({
	transpileDependencies: true,
	devServer: {
		allowedHosts: [
			'https://data-sources-app-dev-8vdb2.ondigitalocean.app'
		],
  },
});
