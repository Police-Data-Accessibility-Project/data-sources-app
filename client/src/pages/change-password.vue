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

			<Button class="max-w-full" type="submit">
				{{ loading ? 'Loading...' : 'Change password' }}
			</Button>
		</Form>
	</main>
</template>

<script setup>
import { Button, Form } from 'pdap-design-system';
import { useUserStore } from '@/stores/user';
import { reactive, ref } from 'vue';

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
const error = ref(undefined);
const loading = ref(false);
const success = ref(false);

const validation = reactive({
	uppercase: false,
	lowercase: false,
	number: false,
	specialCharacter: false,
});

// Functions
// Handlers
/**
 * Handles clearing pw-match form errors on change if they exist
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

<style scoped>
.valid {
	@apply text-green-700 dark:text-green-300;
}
</style>

<route>
	{
		meta: {
			auth: true
		}
	}
</route>
