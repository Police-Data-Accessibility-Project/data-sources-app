<template>
	<main class="pdap-flex-container" :class="{ 'mx-auto max-w-2xl': !success }">
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
				to="/request-reset-password"
				@click="
					isExpiredToken = false;
					error = undefined;
					token = undefined;
				"
			>
				Click here to request another
			</RouterLink>
		</p>

		<FormV2
			v-else
			id="reset-password"
			data-test="reset-password-form"
			class="flex flex-col"
			name="reset-password"
			:error="error"
			:schema="VALIDATION_SCHEMA_CHANGE_PASSWORD"
			@change="onChange"
			@submit="onSubmitChangePassword"
			@input="onResetInput"
		>
			<InputPassword
				v-for="input of FORM_INPUTS_CHANGE_PASSWORD"
				v-bind="{ ...input }"
				:key="input.name"
			/>

			<PasswordValidationChecker ref="passwordRef" />

			<Button class="max-w-full" :is-loading="loading" type="submit">
				Change password
			</Button>
		</FormV2>
	</main>
</template>

<script setup>
import { Button, FormV2, InputPassword } from 'pdap-design-system';
import PasswordValidationChecker from '@/components/PasswordValidationChecker.vue';
import { useUserStore } from '@/stores/user';
import parseJwt from '@/util/parseJwt';
import { onMounted, ref, watchEffect } from 'vue';
import { RouterLink, useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

// Constants
const FORM_INPUTS_CHANGE_PASSWORD = [
	{
		autocomplete: 'password',
		'data-test': 'password',
		id: 'password',
		name: 'password',
		label: 'Password',
		placeholder: 'Your updated password',
	},
	{
		autocomplete: 'password',
		'data-test': 'confirm-password',
		id: 'confirmPassword',
		name: 'confirmPassword',
		label: 'Confirm Password',
		placeholder: 'Confirm your updated password',
	},
];
const VALIDATION_SCHEMA_CHANGE_PASSWORD = [
	{
		name: 'password',
		label: 'Password',
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

const route = useRoute();
const router = useRouter();
// const token = search.token;
const token = route.query.token;

// Stores
const user = useUserStore();
const auth = useAuthStore();

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

	const decoded = parseJwt(token);

	if (decoded.exp < Date.now() / 1000) {
		isExpiredToken.value = true;
		user.setEmail(decoded.sub.email);
	}
	hasValidatedToken.value = true;
}
// Handlers
/**
 * Handles clearing pw-match form errors on change if they exist
 */
function onChange(formValues) {
	passwordRef.value?.updatePasswordValidation(formValues.password);

	if (error.value) {
		handleValidatePasswordMatch(formValues);
	}
}

function onResetInput(e) {
	if (e.target.name === 'password') {
		passwordRef.value?.updatePasswordValidation(e.target.value);
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

async function onSubmitChangePassword(formValues) {
	const isPasswordValid = passwordRef.value?.isPasswordValid();

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
		await auth.loginWithEmail(parseJwt(token).sub.email, password);

		router.push({ path: 'profile' });
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
