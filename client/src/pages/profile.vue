<route>
  {
    meta: {
      auth: true
    }
  }
</route>

<template>
	<main>
		<h1>Placeholder page</h1>
		<p>
			Just created this for now in order to test various profile-related
			functionality.
		</p>

		<template v-if="profileData.followedSearches">
			<h2>Followed searches</h2>
			<div
				v-for="followed of profileData.followedSearches"
				:key="JSON.stringify(followed)"
				class="w-full flex justify-between max-w-2xl"
			>
				<RouterLink :to="{ path: '/search/results', query: followed }">
					{{ getLocationText(followed) }}
				</RouterLink>
				<Button
					intent="secondary"
					class="max-w-max"
					@click="() => unFollow(followed)"
				>
					Un-follow
				</Button>
			</div>
		</template>

		<template v-if="profileData.gitHubIsLinked">
			<p>
				<FontAwesomeIcon :icon="faGithub" /> Your account is linked with Github
			</p>
		</template>

		<template v-else>
			<Button
				class="border-2 border-neutral-950 border-solid [&>svg]:ml-0"
				intent="tertiary"
				@click="async () => await beginOAuthLogin('/profile')"
			>
				<FontAwesomeIcon :icon="faGithub" />
				Link account with Github
			</Button>
		</template>

		<div class="mt-4">
			<Button @click="signOutWithRedirect">Sign out</Button>
		</div>
	</main>
</template>

<script>
import { NavigationResult } from 'unplugin-vue-router/data-loaders';
import { defineBasicLoader } from 'unplugin-vue-router/data-loaders/basic';
import { useAuthStore } from '@/stores/auth';
import { useUserStore } from '@/stores/user';
import getLocationText from '@/util/getLocationText';
import { getFollowedSearches, deleteFollowedSearch } from '@/api/search';
import { linkAccountWithGithub, signOut, beginOAuthLogin } from '@/api/auth';

const auth = useAuthStore();
const user = useUserStore();

export const useProfileData = defineBasicLoader('/profile', async (route) => {
	let gitHubIsLinked = false;
	// TODO: do logic here to determine whether user signed up with GH, so we don't have to use this `linked` param
	if (route.query.linked) gitHubIsLinked = true;

	const githubAccessToken = route.query.gh_access_token;
	if (githubAccessToken && user.id)
		return new NavigationResult({ path: '/profile', query: { linked: true } });

	if (githubAccessToken) {
		await linkAccountWithGithub(githubAccessToken);
		gitHubIsLinked = true;
	}
	const followedSearches = (await getFollowedSearches()).data.data;

	return {
		followedSearches,
		gitHubIsLinked,
	};
});
</script>

<script setup>
import { Button } from 'pdap-design-system';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faGithub } from '@fortawesome/free-brands-svg-icons';
import { useRoute, useRouter } from 'vue-router';
import { toast } from 'vue3-toastify';

const route = useRoute();
const router = useRouter();

const {
	data: profileData,
	// loading: profileLoading,
	// error: profileError,
	reload,
} = useProfileData();

async function signOutWithRedirect() {
	auth.setRedirectTo(route);
	await signOut();
	router.replace('/sign-in');
}

async function unFollow(followed) {
	const text = getLocationText(followed);
	try {
		await deleteFollowedSearch(followed);
		toast.success(`Un-followed search for ${text}`);
		reload();
	} catch (error) {
		toast.error(`Error un-following search for ${text}, please try again.`);
	}
}
</script>
