<template>
	<main class="pdap-flex-container" :class="{ 'mx-auto max-w-2xl': !success }">
		<template v-if="success">
			<h1>Success</h1>
			<p>Your password has been successfully updated</p>
		</template>

		<template v-else>
			<h1>Change your password</h1>
			<!-- TODO: make this copy conditional based on whether or not user signed up via GH -->
			<p>
				You signed up with a Github account linked to the email address you
				provided.
			</p>
			<p>
				Sign in with Github, or create a password to sign in with this email
				address.
			</p>
			<!-- END TODO -->

			<Button
				class="border-2 border-neutral-950 border-solid [&>svg]:ml-0"
				intent="tertiary"
				@click="() => beginOAuthLogin('/profile')"
			>
				<FontAwesomeIcon :icon="faGithub" />
				Sign in with Github
			</Button>

			<FormV2
				id="change-password"
				class="flex flex-col gap-2"
				data-test="change-password-form"
				name="change-password"
				:error="error"
				:schema="VALIDATION_SCHEMA"
				@change="onChange"
				@submit="onSubmit"
				@input="onInput"
			>
				<InputPassword
					v-for="input of INPUTS"
					v-bind="{ ...input }"
					:key="input.name"
				/>

				<PasswordValidationChecker ref="passwordRef" class="mt-2" />

				<Button class="max-w-full" :is-loading="loading" type="submit">
					Change password
				</Button>
			</FormV2>
		</template>
	</main>
</template>

<script setup>
import { Button, FormV2, InputPassword } from 'pdap-design-system';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faGithub } from '@fortawesome/free-brands-svg-icons';
import { useAuthStore } from '@/stores/auth';
import { useUserStore } from '@/stores/user';
import PasswordValidationChecker from '@/components/PasswordValidationChecker.vue';
import { ref } from 'vue';

// Constants
const INPUTS = [
	{
		autocomplete: 'new-password',
		'data-test': 'password',
		id: 'password',
		name: 'password',
		label: 'Password',
		type: 'password',
		placeholder: 'Your updated password',
	},
	{
		autocomplete: 'new-password',
		'data-test': 'confirm-password',
		id: 'confirmPassword',
		name: 'confirmPassword',
		label: 'Confirm Password',
		type: 'password',
		placeholder: 'Confirm your updated password',
	},
];
const VALIDATION_SCHEMA = [
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
	{
		name: 'confirmPassword',
		validators: {
			required: {
				value: true,
			},
			password: {
				message: 'Please confirm your password',
				value: true,
			},
		},
	},
];

// Stores
const user = useUserStore();
const { beginOAuthLogin } = useAuthStore();

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

function onInput(e) {
	if (e.target.name === 'password') {
		passwordRef.value.updatePasswordValidation(e.target.value);
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
