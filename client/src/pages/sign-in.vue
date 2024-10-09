<template>
	<main class="pdap-flex-container mx-auto max-w-2xl">
		<h1>Sign In</h1>
		<FormV2
			id="login"
			class="flex flex-col"
			data-test="login-form"
			name="login"
			:error="error"
			:schema="VALIDATION_SCHEMA"
			@submit="onSubmit"
		>
			<InputText
				id="email"
				autofill="email"
				data-test="email"
				name="email"
				label="Email"
				type="text"
				placeholder="Your email address"
			/>
			<InputPassword
				id="password"
				autofill="password"
				data-test="password"
				name="password"
				label="Password"
				type="password"
				placeholder="Your password"
			/>

			<Button
				class="max-w-full"
				:is-loading="loading"
				type="submit"
				data-test="submit-button"
			>
				<Spinner v-if="loading" :show="loading" />
				{{ !loading ? 'Sign in' : '' }}
			</Button>
		</FormV2>
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
import {
	Button,
	FormV2,
	InputPassword,
	InputText,
	Spinner,
} from 'pdap-design-system';
import { onMounted, ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const router = useRouter();

// Constants
const VALIDATION_SCHEMA = [
	{
		name: 'email',
		validators: {
			required: {
				value: true,
			},
			email: {
				message: 'Please provide your email address',
				value: true,
			},
		},
	},
	{
		name: 'password',
		validators: {
			required: {
				value: true,
			},
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
