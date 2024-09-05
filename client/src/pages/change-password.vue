<template>
	<main v-if="success" class="pdap-flex-container">
		<h1>Success</h1>
		<p>Your password has been successfully updated</p>
	</main>
	<main v-else class="pdap-flex-container mx-auto max-w-2xl">
		<h1>Change your password</h1>
		<Form
			id="change-password"
			class="flex flex-col"
			data-test="change-password-form"
			name="change-password"
			:error="error"
			:schema="FORM_SCHEMA"
			@change="onChange"
			@submit="onSubmit"
		>
			<PasswordValidationChecker ref="passwordRef" />

			<Button class="max-w-full" type="submit">
				{{ loading ? 'Loading...' : 'Change password' }}
			</Button>
		</Form>
	</main>
</template>

<script setup>
import { Button, Form } from 'pdap-design-system';
import { useUserStore } from '@/stores/user';
import PasswordValidationChecker from '@/components/PasswordValidationChecker.vue';
import { ref } from 'vue';

// Constants
const FORM_SCHEMA = [
	{
		autofill: 'new-password',
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
		autofill: 'new-password',
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

// Stores
const user = useUserStore();

// Reactive vars
const passwordRef = ref();
const error = ref(undefined);
const loading = ref(false);
const success = ref(false);

// Functions
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

async function onSubmit(formValues) {
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
		await user.changePassword(user.email, password);

		success.value = true;
	} catch (err) {
		error.value = err.message;
	} finally {
		loading.value = false;
	}
}
</script>

<route>
	{
		meta: {
			auth: true
		}
	}
</route>
