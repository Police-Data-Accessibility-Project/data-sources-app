<template>
	<div>
		<main v-if="error" class="pdap-flex-container-center">
			<h1>Oops, something went wrong!</h1>
			<p class="max-w-full" data-test="error-boundary-message">
				If you keep seeing this message, please email
				<a href="mailto:contact@pdap.io">contact@pdap.io</a> for assistance.
			</p>
		</main>
		<slot v-else />
	</div>
</template>
<script>
export default {
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
