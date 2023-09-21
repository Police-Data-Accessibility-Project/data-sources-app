const { defineConfig } = require('@vue/cli-service');
module.exports = defineConfig({
	transpileDependencies: true,
	devServer: {
		allowedHosts: 'all',
		devMiddleWare:{ '/data-sources-app-client/'
		},
  },
	
});
