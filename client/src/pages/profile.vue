<template>
	<main>
		<h1>Placeholder page</h1>
		<p>
			Just created this for now in order to test linking GH account to existing
			email account. Eventually this GH linking flow will be conditionally
			rendered based on whether the user is linked via OAuth.
		</p>

		<div
			v-if="githubAuthLoading"
			class="flex items-center justify-center h-full w-full"
		>
			<Spinner :show="githubLoading" text="Logging in" />
		</div>

		<template v-else-if="githubAuthIsLinked">
			<p>
				<FontAwesomeIcon :icon="faGithub" /> Your account is linked with Github
			</p>
		</template>

		<template v-else>
			<template v-if="githubAuthError">
				<p class="error">
					There was an error logging you in with Github. Please try again
				</p>
			</template>
			<template v-else>
				<Button
					class="border-2 border-neutral-950 border-solid [&>svg]:ml-0"
					intent="tertiary"
					@click="async () => await auth.beginOAuthLogin('/profile')"
				>
					<FontAwesomeIcon :icon="faGithub" />
					Link account with Github
				</Button>
			</template>
		</template>

		<div class="mt-4">
			<Button @click="signOut"> Sign out </Button>
		</div>
	</main>
</template>

<script>
import { NavigationResult } from 'unplugin-vue-router/data-loaders';
import { defineBasicLoader } from 'unplugin-vue-router/data-loaders/basic';
import { useAuthStore } from '@/stores/auth';
import { useUserStore } from '@/stores/user';

const auth = useAuthStore();
const user = useUserStore();

export const useGithubAuth = defineBasicLoader('/profile', async (route) => {
	// TODO: do logic here to determine whether user signed up with GH, so we don't have to use this `linked` param
	if (route.query.linked) return true;

	const githubAccessToken = route.query.gh_access_token;
	if (githubAccessToken && user.id)
		return new NavigationResult({ path: '/profile', query: { linked: true } });

	if (githubAccessToken) {
		await auth.linkAccountWithGithub(githubAccessToken);
		return true;
	}
});
</script>

<script setup>
import { Button, Spinner } from 'pdap-design-system';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faGithub } from '@fortawesome/free-brands-svg-icons';
import { useRoute } from 'vue-router';

const route = useRoute();

const {
	data: githubAuthIsLinked,
	loading: githubAuthLoading,
	error: githubAuthError,
} = useGithubAuth();

async function signOut() {
	await auth.logout({ ...route });
}
</script>

<route>
  {
    meta: {
      auth: true
    }
  }
</route>
