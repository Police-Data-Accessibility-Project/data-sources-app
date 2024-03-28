<template>
	<!-- User is already logged in -->
	<main v-if="auth.userId" class="pdap-flex-container">
		<h1 data-test="success-heading">
			{{ success ? 'Success' : "You're already logged in" }}
		</h1>
		<p data-test="success-subheading">
			{{ success ? success : 'Enjoy the data sources app!' }}
		</p>

		<Button
			class="mt-6"
			data-test="logout-button"
			@click="
				() => {
					auth.logout();
					success = '';
				}
			"
			>Log out</Button
		>
	</main>

	<!-- Otherwise, the form (form handles error UI on its own) -->
	<main v-else class="pdap-flex-container mx-auto max-w-2xl">
		<h1>Sign In</h1>
		<Form
			id="login"
			class="flex flex-col"
			data-test="login-form"
			name="login"
			:error="error"
			:schema="FORM_SCHEMAS[type]"
			@change="handleChangeOnError"
			@submit="onSubmit"
		>
			<ul v-if="type === FORM_TYPES.signup" class="text-med mb-8">
				Passwords must be at least 8 characters and include:
				<li>1 uppercase letter</li>
				<li>1 lowercase letter</li>
				<li>1 number</li>
				<li>1 special character</li>
			</ul>

			<Button class="max-w-full" type="submit" data-test="submit-button">
				{{ getSubmitButtonCopy() }}
			</Button>
		</Form>
		<div
			class="flex flex-col items-start sm:flex-row sm:items-center sm:gap-4 w-full"
		>
			<Button
				class="flex-1 max-w-full"
				intent="secondary"
				data-test="toggle-button"
				@click="toggleType"
			>
				{{ type === FORM_TYPES.login ? 'Create Account' : 'Log In' }}
			</Button>
			<RouterLink
				class="pdap-button-secondary flex-1 max-w-full"
				data-test="reset-link"
				to="/reset-password"
				>Reset Password</RouterLink
			>
		</div>
	</main>
</template>

<script setup>
// Imports
import { Button, Form } from 'pdap-design-system';
import { ref, watchEffect } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useUserStore } from '../stores/user';

// Constants
const LOGIN_SCHEMA = [
	{
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

// Signing up we want to validate that PW matches, so we add that field
const SIGNUP_SCHEMA = LOGIN_SCHEMA.concat({
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
});

const SUCCESS_COPY = {
	login: "You're now logged in!",
	signup: 'Your account is now active!',
};

/**
 * Enum-like object for TS stans 😊
 */
const FORM_TYPES = {
	login: 'login',
	signup: 'signup',
};

const FORM_SCHEMAS = {
	[FORM_TYPES.login]: LOGIN_SCHEMA,
	[FORM_TYPES.signup]: SIGNUP_SCHEMA,
};

// Store
const auth = useAuthStore();
const user = useUserStore();

// Reactive vars
const error = ref(undefined);
const loading = ref(false);
const success = ref(undefined);
const type = ref(FORM_TYPES.login);

// Effects
// Clear error on success
watchEffect(() => {
	if (success.value) error.value = undefined;
});

// Functions
// Handlers
/**
 * When signing up: handles clearing pw-match form errors on change if they exist
 */
function handleChangeOnError(formValues) {
	if (
		type.value === FORM_TYPES.signup &&
		error.value &&
		formValues.password !== formValues.confirmPassword
	) {
		handlePasswordValidation(formValues);
	}
}

/**
 * When signing up: validates that passwords match
 * @returns {boolean} `false` if passwords do not match, `true` if they do
 */
function handlePasswordValidation(formValues) {
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

/**
 * Logs user in or signs user up
 */
async function onSubmit(formValues) {
	if (type.value === FORM_TYPES.signup) {
		if (!handlePasswordValidation(formValues)) return;
	}

	try {
		loading.value = true;
		const { email, password } = formValues;

		type.value === FORM_TYPES.signup
			? await user.signup(email, password)
			: await auth.login(email, password);

		success.value = SUCCESS_COPY[type.value];
	} catch (err) {
		error.value = 'Something went wrong, please try again.';
	} finally {
		loading.value = false;
	}
}

// Utils
/**
 * Toggles between login and signup actions
 */
function toggleType() {
	switch (type.value) {
		case FORM_TYPES.login:
			type.value = FORM_TYPES.signup;
			break;
		case FORM_TYPES.signup:
		default:
			type.value = FORM_TYPES.login;
			break;
	}
}

function getSubmitButtonCopy() {
	switch (true) {
		case loading.value:
			return 'Loading...';
		case type.value === FORM_TYPES.signup:
			return 'Create account';
		case type.value === FORM_TYPES.login:
		default:
			return 'Login';
	}
}
</script>
