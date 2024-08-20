<template>
	<!-- User is already logged in -->
	<main v-if="auth.userId" class="pdap-flex-container">
		<h1>Your account is now active</h1>
		<p data-test="success-subheading">Enjoy the data sources app.</p>

		<RouterLink class="pdap-button-secondary mt-6" to="/">
			Search data sources
		</RouterLink>
	</main>

	<!-- Otherwise, the form (form handles error UI on its own) -->
	<main v-else class="pdap-flex-container mx-auto max-w-2xl">
		<h1>Sign Up</h1>
		<Form
			id="login"
			class="flex flex-col"
			data-test="login-form"
			name="login"
			:error="error"
			:reset-on="success"
			:schema="FORM_SCHEMA"
			@change="onChange"
			@submit="onSubmit"
		>
			<ul class="text-med mb-8">
				Passwords must be at least 8 characters and include:
				<li
					:class="{
						valid: validation.uppercase,
					}"
				>
					1 uppercase letter
				</li>
				<li
					:class="{
						valid: validation.lowercase,
					}"
				>
					1 lowercase letter
				</li>
				<li
					:class="{
						valid: validation.number,
					}"
				>
					1 number
				</li>
				<li
					:class="{
						valid: validation.specialCharacter,
					}"
				>
					1 special character
				</li>
			</ul>

			<Button class="max-w-full" type="submit" data-test="submit-button">
				Create account
			</Button>
		</Form>
		<div
			class="flex flex-col items-start gap-3 sm:flex-row sm:items-center sm:gap-4 sm:flex-wrap w-full"
		>
			<p class="w-full max-w-[unset]">Already have an account?</p>

			<RouterLink
				class="pdap-button-secondary flex-1 max-w-full"
				data-test="toggle-button"
				to="/sign-in"
			>
				Log in
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
import { Button, Form } from 'pdap-design-system';
import { ref, onMounted, reactive } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useUserStore } from '@/stores/user';
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
		autofill: 'new-password',
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
	{
		autofill: 'new-password',
		'data-test': 'confirm-password',
		id: 'confirmPassword',
		name: 'confirmPassword',
		label: 'Confirm Password',
		type: 'password',
		placeholder: 'Confirm your password',
		value: '',
		validators: {
			password: {
				message: 'Please confirm your password',
				value: true,
			},
		},
	},
];

// Store
const auth = useAuthStore();
const user = useUserStore();

// Reactive vars
const error = ref(undefined);
const loading = ref(false);
const success = ref(false);
const validation = reactive({
	uppercase: false,
	lowercase: false,
	number: false,
	specialCharacter: false,
});

onMounted(async () => {
	// User signed up and logged in
	if (auth.userId) await router.push({ path: '/' });
});

// Functions
// Handlers
/**
 * When signing up: handles clearing pw-match form errors on change if they exist
 */
function onChange(formValues) {
	updatePasswordValidation(formValues);

	if (error.value) {
		handleValidatePasswordMatch(formValues);
	}
}

function handleValidatePasswordMatch(formValues) {
	if (formValues.password !== formValues.confirmPassword) {
		if (!error.value) {
			error.value = 'Passwords do not match, please try again.';
		}
		return false;
	} else {
		error.value = undefined;
		return true;
	}
}

function isPasswordValid() {
	if (!Object.values(validation).every(Boolean)) {
		error.value = 'Password is not valid';
		return false;
	} else {
		if (error.value) error.value = undefined;
		return true;
	}
}

function updatePasswordValidation({ password }) {
	// Test uppercase
	if (/[A-Z]/gm.test(password)) {
		validation.uppercase = true;
	} else {
		validation.uppercase = false;
	}

	// Test lowercase
	if (/[a-z]/gm.test(password)) {
		validation.lowercase = true;
	} else {
		validation.lowercase = false;
	}

	// Test number
	if (/[0-9]/gm.test(password)) {
		validation.number = true;
	} else {
		validation.number = false;
	}

	// Test special char
	if (/[#?!@$%^&*-]/gm.test(password)) {
		validation.specialCharacter = true;
	} else {
		validation.specialCharacter = false;
	}
}

async function onSubmit(formValues) {
	if (!handleValidatePasswordMatch(formValues) || !isPasswordValid()) return;

	try {
		loading.value = true;
		const { email, password } = formValues;

		await user.signup(email, password);
		success.value = true;
	} catch (err) {
		error.value = 'Something went wrong, please try again.';
	} finally {
		loading.value = false;
	}
}
</script>

<style scoped>
.valid {
	@apply text-green-700 dark:text-green-300;
}
</style>
