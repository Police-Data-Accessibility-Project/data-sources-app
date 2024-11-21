<template>
	<main class="pdap-flex-container mx-auto max-w-2xl">
		<template v-if="!auth.userId">
			<h1>Sign Up</h1>

			<!-- TODO: when GH auth is complete, encapsulate duplicate UI from this and `/sign-up` -->
			<div
				v-if="githubLoading"
				class="flex items-center justify-center h-full w-full"
			>
				<Spinner :show="githubLoading" text="Logging in" />
			</div>

			<template v-else>
				<template v-if="githubAuthError">
					<p class="error">
						There was an error logging you in with Github. Please try again
					</p>
				</template>
				<template v-else>
					<template v-if="githubAuthData?.userExists">
						<p class="error">
							You already have an account with this email address. Please
							<RouterLink to="/profile">sign in</RouterLink>
							and link your existing account to Github from your profile.
						</p>
					</template>

					<Button
						class="border-2 border-neutral-950 border-solid [&>svg]:ml-0"
						intent="tertiary"
						:disabled="githubAuthData?.userExists"
						@click="async () => await auth.beginOAuthLogin('/sign-up')"
					>
						<FontAwesomeIcon :icon="faGithub" />
						Sign up with Github
					</Button>
				</template>

				<h2>Or sign up with email</h2>
				<FormV2
					id="login"
					class="flex flex-col gap-2"
					data-test="login-form"
					name="login"
					:error="error"
					:schema="VALIDATION_SCHEMA"
					@change="onChange"
					@submit="onSubmit"
					@input="onInput"
				>
					<InputText
						id="email"
						autocomplete="email"
						data-test="email"
						name="email"
						label="Email"
						type="text"
						placeholder="Your email address"
					/>

					<InputPassword
						v-for="input of PASSWORD_INPUTS"
						v-bind="{ ...input }"
						:key="input.name"
					/>

					<PasswordValidationChecker ref="passwordRef" class="mt-2" />

					<Button
						class="max-w-full"
						:disabled="loading"
						:is-loading="loading"
						type="submit"
						data-test="submit-button"
					>
						Create Account
					</Button>
				</FormV2>
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
						to="/request-reset-password"
					>
						Reset Password
					</RouterLink>
				</div>
			</template>
		</template>

		<RouterView v-else />
	</main>
</template>

<script>
// Data loader - navigation guard and GH auth handling
// TODO (when GH auth is settled): abstract this into repeatable func. It's duplicated on `/sign-in` and `/sign-up`
import { NavigationResult } from 'unplugin-vue-router/data-loaders';
import { defineBasicLoader } from 'unplugin-vue-router/data-loaders/basic';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();

export const useGithubAuth = defineBasicLoader('/sign-up', async (route) => {
	if (auth.isAuthenticated())
		return new NavigationResult(auth.redirectTo ?? { path: '/profile' });

	try {
		const githubAccessToken = route.query.gh_access_token;

		if (githubAccessToken) {
			const tokens = await auth.loginWithGithub(githubAccessToken);

			if (tokens)
				return new NavigationResult(
					auth.redirectTo ?? { path: '/profile', query: { linked: true } },
				);
		}
	} catch (error) {
		if (error.response.data.message.includes('already exists')) {
			auth.setRedirectTo({ path: '/profile' });
			return { userExists: true };
		} else throw error;
	}
});
</script>

<script setup>
// Imports
import {
	Button,
	FormV2,
	InputText,
	InputPassword,
	Spinner,
} from 'pdap-design-system';
import PasswordValidationChecker from '@/components/PasswordValidationChecker.vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faGithub } from '@fortawesome/free-brands-svg-icons';
import { ref } from 'vue';
import { useUserStore } from '@/stores/user';
import { RouterView, useRouter } from 'vue-router';

// Constants
const PASSWORD_INPUTS = [
	{
		autocomplete: 'new-password',
		'data-test': 'password',
		id: 'password',
		name: 'password',
		label: 'Password',
		placeholder: 'Your password',
	},
	{
		autocomplete: 'new-password',
		'data-test': 'confirm-password',
		id: 'confirmPassword',
		name: 'confirmPassword',
		label: 'Confirm Password',
		placeholder: 'Confirm your password',
	},
];
const VALIDATION_SCHEMA = [
	{
		name: 'email',
		validators: {
			required: {
				value: true,
			},
			email: {
				message: 'Please provide your email address',
				value: true,
			},
		},
	},
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

// Data loader
const {
	data: githubAuthData,
	error: githubAuthError,
	isLoading: githubLoading,
} = useGithubAuth();

// Router
const router = useRouter();

// Store
const user = useUserStore();

// Reactive vars
const passwordRef = ref();
const error = ref(undefined);
const loading = ref(false);

// Functions
// Handlers
/**
 * When signing up: handles clearing pw-match form errors on change if they exist
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
		const { email, password } = formValues;

		await user.signupWithEmail(email, password);
		await router.push(auth.redirectTo ?? { path: '/sign-up/success' });
	} catch (err) {
		console.error(err);
		error.value =
			500 < err.response.status > 400
				? err.response.data.message
				: 'Something went wrong, please try again.';
	} finally {
		loading.value = false;
	}
}
</script>
