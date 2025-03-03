module.exports = {
	root: true,
	parser: 'vue-eslint-parser',
	extends: [
		'eslint:recommended',
		'plugin:vue/vue3-essential',
		'plugin:vue/vue3-recommended',
		'plugin:vue/strongly-recommended',
		'@vue/eslint-config-prettier',
	],
	env: {
		node: true
	},
	plugins: ['prettier'],
	rules: {
		'vue/require-default-prop': 'off',
		indent: 'off',
		'vue/no-reserved-component-names': 'off',
		'vue/html-self-closing': [
			'error',
			{
				html: {
					void: 'always',
					normal: 'always',
					component: 'always',
				},
				svg: 'always',
				math: 'always',
			},
		],
		'prettier/prettier': [
			'warn',
			{
				indent: [
					'warn',
					'tab',
					{
						SwitchCase: 2,
					},
				],
				tabWidth: 2,
				useTabs: true,
				singleQuote: true,
				quotes: [2, "single", { "avoidEscape": true }]
			},
		],
		'vue/no-multiple-template-root': 'off',
	},
};
