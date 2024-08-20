<template>
	<main class="pdap-flex-container mx-auto max-w-2xl">
		<h1>Sign In</h1>
		<Form
			id="login"
			class="flex flex-col"
			data-test="login-form"
			name="login"
			:error="error"
			:schema="FORM_SCHEMA"
			@submit="onSubmit"
		>
			<Button
				class="max-w-full"
				:is-loading="loading"
				type="submit"
				data-test="submit-button"
			>
				<Spinner v-if="loading" :show="loading" />
				{{ !loading ? 'Sign in' : '' }}
			</Button>
		</Form>
		<div
			class="flex flex-col items-start sm:flex-row sm:items-center sm:gap-4 w-full"
		>
			<RouterLink
				class="pdap-button-secondary flex-1 max-w-full"
				intent="secondary"
				data-test="toggle-button"
				to="/sign-up"
			>
				Create Account
			</RouterLink>
			<RouterLink
				class="pdap-button-secondary flex-1 max-w-full"
				data-test="reset-link"
				to="/reset-password"
			>
				Reset Password
			</RouterLink>
		</div>
	</main>
</template>

<script setup>
// Imports
import { Button, Form, Spinner } from 'pdap-design-system';
import { onMounted, ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const router = useRouter();

// Constants
const FORM_SCHEMA = [
	{
		autofill: 'email',
		'data-test': 'email',
		id: 'email',
		name: 'email',
		label: 'Email',
		type: 'text',
		placeholder: 'Your email address',
		value: '',
		validators: {
			email: {
				message: 'Please provide your email address',
				value: true,
			},
		},
	},
	{
		autofill: 'password',
		'data-test': 'password',
		id: 'password',
		name: 'password',
		label: 'Password',
		type: 'password',
		placeholder: 'Your password',
		value: '',
		validators: {
			password: {
				message: 'Please provide your password',
				value: true,
			},
		},
	},
];

// Store
const auth = useAuthStore();

// Reactive vars
const error = ref(undefined);
const loading = ref(false);

onMounted(() => {
	// If user already logged in, navigate to home page
	if (auth.userId) router.push({ path: '/' });
});

// Handlers
/**
 * Logs user in
 */
async function onSubmit(formValues) {
	try {
		loading.value = true;
		const { email, password } = formValues;

		await auth.login(email, password);

		error.value = undefined;
		router.push({ path: auth.redirectTo || '/' });
	} catch (err) {
		error.value = 'Something went wrong, please try again.';
	} finally {
		loading.value = false;
	}
}
</script>
