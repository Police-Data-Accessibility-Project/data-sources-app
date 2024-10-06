<template>
	<main v-if="success" class="pdap-flex-container">
		<h1>Success</h1>
		<p data-test="success-subheading">
			{{
				token
					? 'Your password has been successfully updated'
					: 'We sent you an email with a link to reset your password. Please follow the link in the email to proceed'
			}}
		</p>
	</main>
	<main
		v-else-if="!success && token"
		class="pdap-flex-container mx-auto max-w-2xl"
	>
		<h1>Change your password</h1>
		<p v-if="!hasValidatedToken" class="flex flex-col items-start sm:gap-4">
			Loading...
		</p>
		<p
			v-else-if="hasValidatedToken && isExpiredToken"
			data-test="token-expired"
			class="flex flex-col items-start sm:gap-4"
		>
			Sorry, that token has expired.
			<RouterLink
				data-test="re-request-link"
				to="/reset-password"
				@click="
					isExpiredToken = false;
					error = undefined;
					token = undefined;
				"
			>
				Click here to request another
			</RouterLink>
		</p>

		<Form
			v-else
			id="reset-password"
			data-test="reset-password-form"
			class="flex flex-col"
			name="reset-password"
			:error="error"
			:schema="FORM_SCHEMA_CHANGE_PASSWORD"
			@change="onChange"
			@submit="onSubmitChangePassword"
		>
			<PasswordValidationChecker ref="passwordRef" />

			<Button class="max-w-full" type="submit">
				{{ loading ? 'Loading...' : 'Change password' }}
			</Button>
		</Form>
	</main>

	<main v-else class="pdap-flex-container mx-auto max-w-2xl">
		<h1>Request a link to reset your password</h1>
		<Form
			id="reset-password"
			data-test="reset-password-form"
			class="flex flex-col"
			name="reset-password"
			:error="error"
			:schema="FORM_SCHEMA_REQUEST_PASSWORD"
			@submit="onSubmitRequestReset"
		>
			<Button class="max-w-full" type="submit">
				{{ loading ? 'Loading...' : 'Request password reset' }}
			</Button>
		</Form>
	</main>
</template>

<script setup>
import { Button, Form } from 'pdap-design-system';
import PasswordValidationChecker from '@/components/PasswordValidationChecker.vue';
import { useUserStore } from '@/stores/user';
import { onMounted, ref, watchEffect } from 'vue';
import { RouterLink, useRoute } from 'vue-router';

// Constants
const FORM_SCHEMA_CHANGE_PASSWORD = [
	{
		autofill: 'password',
		'data-test': 'password',
		id: 'password',
		name: 'password',
		label: 'Password',
		type: 'password',
		placeholder: 'Your updated password',
		value: '',
		validators: {
			password: {
				message: 'Please provide your password',
				value: true,
			},
		},
	},
	{
		autofill: 'password',
		'data-test': 'confirm-password',
		id: 'confirmPassword',
		name: 'confirmPassword',
		label: 'Confirm Password',
		type: 'password',
		placeholder: 'Confirm your updated password',
		value: '',
		validators: {
			password: {
				message: 'Please confirm your password',
				value: true,
			},
		},
	},
];

const FORM_SCHEMA_REQUEST_PASSWORD = [
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
];

const {
	params: { token },
} = useRoute();

// Stores
const user = useUserStore();

// Reactive vars
const passwordRef = ref();
const error = ref(undefined);
const isExpiredToken = ref(false);
const hasValidatedToken = ref(false);
const loading = ref(false);
const success = ref(false);

// Effects
// Clear error on success
watchEffect(() => {
	if (success.value) error.value = undefined;
});

// Functions
// Lifecycle methods
onMounted(validateToken);

// Handlers
async function validateToken() {
	if (!token) return;

	try {
		const response = await user.validateResetPasswordToken(token);

		if (300 < response.status >= 200) {
			isExpiredToken.value = false;
		}
	} catch (error) {
		isExpiredToken.value = true;
	} finally {
		hasValidatedToken.value = true;
	}
}
// Handlers
/**
 * Handles clearing pw-match form errors on change if they exist
 */
function onChange(formValues) {
	passwordRef.value.updatePasswordValidation(formValues.password);

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

async function onSubmitRequestReset(formValues) {
	try {
		loading.value = true;
		const { email } = formValues;
		await user.requestPasswordReset(email);
		success.value = true;
	} catch (err) {
		error.value = err.message;
	} finally {
		loading.value = false;
	}
}

async function onSubmitChangePassword(formValues) {
	const isPasswordValid = passwordRef.value.isPasswordValid();

	if (!isPasswordValid) {
		error.value = 'Password is not valid';
	} else {
		if (error.value) error.value = undefined;
	}

	if (!handleValidatePasswordMatch(formValues) || !isPasswordValid) return;

	try {
		loading.value = true;
		const { password } = formValues;
		await user.resetPassword(password, token);

		success.value = true;
	} catch (err) {
		if (err.message === 'The submitted token is invalid') {
			isExpiredToken.value = true;
		}
		error.value = err.message;
	} finally {
		loading.value = false;
	}
}
</script>
