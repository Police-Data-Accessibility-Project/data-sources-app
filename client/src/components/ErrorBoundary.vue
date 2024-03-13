<template>
	<component
		:is="component"
		v-if="error"
		class="pdap-flex-container-center h-[full]"
	>
		<h1>Oops, something went wrong!</h1>
		<p class="max-w-full" data-test="error-boundary-message">
			If you keep seeing this message, please email
			<a href="mailto:contact@pdap.io">contact@pdap.io</a> for assistance.
		</p>
	</component>
	<slot v-else />
</template>
<script>
export default {
	props: {
		component: {
			type: String,
			default: 'div',
		},
	},
	data() {
		return {
			error: false,
		};
	},
	errorCaptured(error) {
		this.interceptError(error);
	},
	methods: {
		interceptError(error) {
			this.error = error;
		},
	},
};
</script>
