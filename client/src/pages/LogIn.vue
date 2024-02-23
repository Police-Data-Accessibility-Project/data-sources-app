<template>
	<main class="pdap-flex-container">
		<!-- User is already logged in -->
		<div v-if="!success && auth.userId">
			<h1>You're already logged in</h1>
			<p>Enjoy the data sources app!</p>
		</div>

		<!-- User has logged in / signed up successfully, display success message -->
		<div v-else-if="success && auth.userId">
			<h1>Success</h1>
			<p>{{ success }}</p>
		</div>

		<!-- Otherwise, the form (form handles error UI on its own) -->
		<div v-else>
			<h1>Sign In</h1>
			<Form
				id="login"
				class="flex flex-col"
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

				<Button class="max-w-full" type="submit">{{
					type === FORM_TYPES.signup ? 'Sign Up' : 'Log In'
				}}</Button>
			</Form>
			<p>
				{{
					type === FORM_TYPES.login
						? "Don't have an account?"
						: 'Already have an account?'
				}}
				<Button intent="tertiary" @click="toggleType">{{
					type === FORM_TYPES.login ? 'Sign Up' : 'Log In'
				}}</Button>
			</p>
		</div>

		<div>
			Log out (for testing)
			<Button
				@click="
					() => {
						auth.logout();
						success = '';
					}
				"
				>Log out</Button
			>
		</div>
	</main>
</template>

<script setup>
// Imports
import { Button, Form } from 'pdap-design-system';
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';

// Constants
const LOGIN_SCHEMA = [
	{
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

// Reactive vars
const error = ref(undefined);
const loading = ref(false);
const success = ref(undefined);
const type = ref(FORM_TYPES.login);

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

		const response =
			type.value === FORM_TYPES.signup
				? await auth.signup(email, password)
				: await auth.login(email, password);

		success.value = SUCCESS_COPY[type.value] ?? response.message;
	} catch (error) {
		error.value = error;
	} finally {
		loading.value = false;
	}
}

/**
 * Toggles between login and signup actions
 */
function toggleType() {
	switch (type.value) {
		case FORM_TYPES.signup:
			type.value = FORM_TYPES.login;
			break;
		case FORM_TYPES.login:
			type.value = FORM_TYPES.signup;
			break;
		default:
			return;
	}
}
</script>
