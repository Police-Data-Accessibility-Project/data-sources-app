<template>
	<main class="pdap-flex-container">
		<!-- User has logged in / signed up successfully, display success message -->
		<div v-if="success">
			<h1>Success</h1>
			{{ success }}
		</div>

		<!-- Otherwise, the form (form handles error UI on its own) -->
		<div v-else>
			<h1>Sign In</h1>
			<Form
				id="login"
				class="flex flex-col"
				name="login"
				:error="error"
				:schema="formSchemas[type]"
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
	</main>
</template>

<script>
import axios from 'axios';
import { Button, Form } from 'pdap-design-system';

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

export default {
	name: FORM_TYPES.login,
	components: {
		Button,
		Form,
	},
	data() {
		return {
			error: undefined,
			type: FORM_TYPES.login,
			formSchemas: {
				[FORM_TYPES.login]: LOGIN_SCHEMA,
				[FORM_TYPES.signup]: SIGNUP_SCHEMA,
			},
			// Adding enum-like obj for use in markup
			FORM_TYPES,
			loading: false,
			success: undefined,
			url: `${import.meta.env.VITE_VUE_APP_BASE_URL}/user`,
		};
	},
	methods: {
		/**
		 * When signing up: handles clearing pw-match form errors on change if they exist
		 */
		handleChangeOnError(formValues) {
			if (
				this.type === FORM_TYPES.signup &&
				this.error &&
				formValues.password !== formValues.confirmPassword
			) {
				this.handlePasswordValidation(formValues);
			}
		},

		/**
		 * When signing up: validates that passwords match
		 * @returns {boolean} `false` if passwords do not match, `true` if they do
		 */
		handlePasswordValidation(formValues) {
			if (formValues.password !== formValues.confirmPassword) {
				if (!this.error) {
					this.error = 'Passwords do not match, please try again.';
				}
				return false;
			} else {
				this.error = undefined;
				return true;
			}
		},

		async login(data) {
			return await axios.get(this.url, data, {
				headers: { 'Content-Type': 'application/json' },
			});
		},

		async signup(data) {
			// Destructure to remove "confirmPassword" field — backend doesn't need it.
			const { email, password } = data;

			return await axios.post(
				this.url,
				{
					email,
					password,
				},
				{
					headers: { 'Content-Type': 'application/json' },
				},
			);
		},

		/**
		 * Logs user in or signs user up
		 */
		async onSubmit(formValues) {
			if (this.type === FORM_TYPES.signup) {
				if (!this.handlePasswordValidation(formValues)) return;
			}

			try {
				this.loading = true;
				const response =
					this.type === FORM_TYPES.signup
						? await this.signup(formValues)
						: await this.login(formValues);
				if (response.error) this.error = response.error;
			} catch (error) {
				this.error = error;
			} finally {
				if (!this.error) {
					this.success = SUCCESS_COPY[this.type];
				}
				this.loading = false;
			}
		},

		/**
		 * Toggles between login and signup actions
		 */
		toggleType() {
			switch (this.type) {
				case FORM_TYPES.signup:
					this.type = FORM_TYPES.login;
					break;
				case FORM_TYPES.login:
					this.type = FORM_TYPES.signup;
					break;
				default:
					return;
			}
		},
	},
};
</script>
