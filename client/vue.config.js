const { defineConfig } = require('@vue/cli-service');
module.exports = defineConfig({
	transpileDependencies: true,
	devServer: {
		public: 'https://data-sources-app-dev-8vdb2.ondigitalocean.app'
  },
});
