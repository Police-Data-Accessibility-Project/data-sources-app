<template>
	<main class="pdap-flex-container mx-auto max-w-2xl pb-24">
		<h1>Sign In</h1>

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
						You already have an account with this email address. Please sign in
						and link your existing account to Github from your profile.
					</p>
				</template>

				<Button
					class="border-2 border-neutral-950 border-solid [&>svg]:ml-0"
					intent="tertiary"
					:disabled="githubAuthData?.userExists"
					@click="async () => await beginOAuthLogin()"
				>
					<FontAwesomeIcon :icon="faGithub" />
					Sign in with Github
				</Button>
			</template>

			<h2>Or sign in with email</h2>
			<FormV2
				id="login"
				class="flex flex-col gap-2"
				data-test="login-form"
				name="login"
				:error="error"
				:schema="VALIDATION_SCHEMA"
				@submit="onSubmit"
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
					id="password"
					autocomplete="password"
					data-test="password"
					name="password"
					label="Password"
					type="password"
					placeholder="Your password"
				/>

				<Button
					class="max-w-full mt-4"
					:is-loading="loading"
					type="submit"
					data-test="submit-button"
				>
					Sign in
				</Button>
			</FormV2>
			<div
				class="flex flex-col items-start sm:flex-row sm:items-center sm:gap-4 w-full"
			>
				<RouterLink
					class="pdap-button-secondary flex-1 max-w-full"
					intent="secondary"
					data-test="toggle-button"
					to="/sign-up"
				>
					Create Account
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
	</main>
</template>

<script>
// Data loader - navigation guard and GH auth handling
// TODO (when GH auth is settled): abstract this into repeatable func. It's duplicated on `/sign-in` and `/sign-up`
import { NavigationResult } from 'unplugin-vue-router/data-loaders';
import { defineBasicLoader } from 'unplugin-vue-router/data-loaders/basic';
import { useAuthStore } from '@/stores/auth';
import { beginOAuthLogin, signInWithGithub } from '@/api/auth';

const auth = useAuthStore();

export const useGithubAuth = defineBasicLoader('/sign-in', async (route) => {
	if (auth.isAuthenticated())
		throw new NavigationResult(auth.redirectTo ?? { path: '/profile' });

	try {
		const githubAccessToken = route.query.gh_access_token;

		if (githubAccessToken) {
			const tokens = await signInWithGithub(githubAccessToken);

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
import { signInWithEmail } from '@/api/auth';
import {
	Button,
	FormV2,
	InputPassword,
	InputText,
	Spinner,
} from 'pdap-design-system';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faGithub } from '@fortawesome/free-brands-svg-icons';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// Constants
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
			// password: {
			// 	message: 'Please provide your password',
			// 	value: true,
			// },
		},
	},
];

// Store
const {
	data: githubAuthData,
	error: githubAuthError,
	isLoading: githubLoading,
} = useGithubAuth();

// Reactive vars
const error = ref(undefined);
const loading = ref(false);

// Handlers
/**
 * Logs user in
 */
async function onSubmit(formValues) {
	try {
		loading.value = true;
		const { email, password } = formValues;

		await signInWithEmail(email, password);

		error.value = undefined;
		router.push(auth.redirectTo ?? '/profile');
	} catch (err) {
		console.error(err);
		error.value =
			err.response?.status > 400 && err.response?.status < 500
				? err.response?.data.message
				: 'Something went wrong, please try again.';
	} finally {
		loading.value = false;
	}
}
</script>

<style scoped>
.error {
	@apply border-red-800 dark:border-red-300 items-center justify-start flex bg-red-300 text-red-800 text-sm rounded-sm max-w-full p-2;
}
</style>
