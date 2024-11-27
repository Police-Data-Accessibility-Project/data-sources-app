<template>
	<main class="pdap-flex-container">
		<h1>
			{{ error ? 'Error validating your account' : 'Validating your account' }}
		</h1>
		<p
			v-if="error || (hasValidatedToken && isExpiredToken)"
			data-test="token-expired"
			class="flex flex-col items-start sm:gap-4"
		>
			Sorry, that token has expired.
			<Button intent="primary" @click="requestResendValidationEmail">
				Click here to request another
			</Button>
		</p>

		<div v-if="error">
			<p class="max-w-full">
				Error validating your email. Try again, or contact
				<a href="mailto:contact@pdap.io">contact@pdap.io</a> for assistance.
			</p>
		</div>

		<Spinner v-else class="h-full w-full" :show="true" :size="64" />
	</main>
</template>

<script setup>
import { Button, Spinner } from 'pdap-design-system';
import { useUserStore } from '@/stores/user';
import parseJwt from '@/util/parseJwt';
import { h, onMounted, ref, watchEffect } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { toast } from 'vue3-toastify';

// Composables
const route = useRoute();
const router = useRouter();
// const token = search.token;
const token = route.query.token;

// Stores
const user = useUserStore();
const auth = useAuthStore();

// Reactive vars
const error = ref(undefined);
const isExpiredToken = ref(false);
const hasValidatedToken = ref(false);
const success = ref(false);

// Effects
// Clear error on success
watchEffect(() => {
	if (success.value) error.value = undefined;
});

// Functions
// Lifecycle methods
onMounted(async () => {
	try {
		await validateToken();
		await auth.validateEmail(token);
		router.replace({ path: '/profile' });
	} catch (err) {
		error.value = err.message;
	}
});

// Handlers
async function validateToken() {
	return new Promise((resolve) => {
		if (!token) resolve();

		const decoded = parseJwt(token);
		user.setEmail(decoded.sub.email);

		if (decoded.exp < Date.now() / 1000) {
			isExpiredToken.value = true;
		}
		hasValidatedToken.value = true;

		resolve();
	});
}

// Handlers
async function requestResendValidationEmail() {
	isExpiredToken.value = false;
	error.value = undefined;

	try {
		await auth.resendValidationEmail();
		toast.success('A new email has been sent to ' + user.email);
	} catch (err) {
		error.value = err.message;
		toast.error(
			h('p', [
				`There was an error sending the email to ${user.email ? user.email : 'your email address'}. Try again or contact `,
				h(
					'a',
					{
						href: 'mailto:contact@pdap.io',
					},
					'contact@pdap.io',
				),
				' for assistance.',
			]),
		);
	}
}
</script>

<style scoped>
main {
	height: calc(100vh - 80px - 400px);
}
</style>
