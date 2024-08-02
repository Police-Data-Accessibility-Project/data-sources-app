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
			@change="handleChangeOnError"
			@submit="onSubmit"
		>
			<Button class="max-w-full" type="submit">
				{{ loading ? 'Loading...' : 'Change password' }}
			</Button>
		</Form>
	</main>
</template>

<script setup>
import { Button, Form } from 'pdap-design-system';
import { useUserStore } from '@/stores/user';
import { ref } from 'vue';

// Constants
const FORM_SCHEMA = [
	{
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
const error = ref(undefined);
const loading = ref(false);
const success = ref(false);

// Functions
// Handlers
/**
 * Handles clearing pw-match form errors on change if they exist
 */
function handleChangeOnError(formValues) {
	if (error.value && formValues.password !== formValues.confirmPassword) {
		handlePasswordValidation(formValues);
	}
}

/**
 * Validates that passwords match
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
 * Updates user's password
 */
async function onSubmit(formValues) {
	if (!handlePasswordValidation(formValues)) return;

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
