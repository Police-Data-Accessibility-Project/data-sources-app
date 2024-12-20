<route>
  {
    meta: {
      auth: true
    }
  }
</route>

<template>
	<main>
		<h1>Profile</h1>

		<h2>Basic information</h2>
		<div class="flex flex-col gap-6">
			<section>
				<h3 class="like-h4">Email</h3>
				<div :class="{ 'profile-loading h-12': profileLoading }">
					<p>
						{{ profileData?.email }}
					</p>
				</div>
			</section>

			<!-- Github info -->
			<section>
				<h3 class="like-h4">Github account</h3>
				<div :class="{ 'profile-loading h-12': profileLoading }">
					<template
						v-if="didLinkGithub || profileData?.external_accounts.github"
					>
						<p>
							<FontAwesomeIcon :icon="faGithub" /> Your account is linked with
							Github
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
				</div>
			</section>

			<!-- API Key -->
			<section>
				<h3 class="like-h4">API Key</h3>

				<div :class="{ 'profile-loading h-12': profileLoading }">
					<Button
						:class="{ 'mb-5': apiKey }"
						intent="secondary"
						type="button"
						@click="createAPIKey"
					>
						Regenerate API Key
					</Button>
				</div>

				<transition name="dropdown" appear>
					<div v-if="apiKey && !apiKeyIsDismissed">
						<ProfileAPIKey
							:api-key="apiKey"
							:on-dismiss="
								() => {
									apiKeyIsDismissed = true;
								}
							"
						/>
					</div>
				</transition>
			</section>

			<!-- Permissions -->
			<section v-if="profileData?.permissions.length">
				<h3 class="like-h4">Permissions</h3>
				<ul>
					<li v-for="permission of profileData.permissions" :key="permission">
						{{ permission }}
					</li>
				</ul>
			</section>

			<div>
				<Button @click="signOutWithRedirect">Sign out</Button>
			</div>
		</div>

		<h2>My stuff</h2>

		<!-- Requests -->
		<h3 class="like-h4">My requests</h3>
		<div v-if="profileLoading" class="profile-loading h-20" />
		<ProfileTable v-else :items="requests">
			<template #left="{ item }">
				<p>
					{{ item.title }}
				</p>
			</template>
			<template #center="{ item }">
				<p
					v-for="(location, i) of item.locations"
					:key="'profile-request' + getFullLocationText(location)"
				>
					{{
						getFullLocationText(location) +
						(i === item.locations.length - 1 ? '' : ', ')
					}}
				</p>
			</template>
			<template #right="{ item }">
				<a
					v-if="item.github_issue_url"
					:href="item.github_issue_url"
					target="_blank"
					rel="noopener noreferrer"
					@keydown.stop.enter=""
					@click.stop=""
				>
					<FontAwesomeIcon :icon="faLink" />
					Github
				</a>
			</template>
		</ProfileTable>

		<!-- Followed searches -->
		<h3 class="like-h4">Followed searches</h3>
		<div v-if="profileLoading" class="profile-loading h-20" />
		<ProfileTable v-else :items="followedSearches">
			<template #left="{ item }">
				<p class="flex items-center justify-start">
					{{ getFullLocationText(item) }}
				</p>
			</template>
			<template #center> <span /></template>
			<template #right="{ item }">
				<Button
					class="h-full w-full max-w-full text-right"
					intent="tertiary"
					type="button"
					@keydown.stop.prevent.enter="() => unFollow(item)"
					@click.stop.prevent="() => unFollow(item)"
				>
					<FontAwesomeIcon :icon="faCircleXmark" />
					Unfollow
				</Button>
			</template>
		</ProfileTable>

		<!-- Recent searches -->
		<h3 class="like-h4">Recent searches</h3>
		<div v-if="profileLoading" class="profile-loading h-20" />
		<ProfileTable v-else :items="recentSearches">
			<template #left="{ item }">
				<div class="max-1/3">
					<p
						v-for="category of item.record_categories"
						:key="category"
						class="pill w-max text-xxs"
					>
						<RecordTypeIcon :record-type="category" />
						{{ category }}
					</p>
				</div>
			</template>
			<template #center="{ item }">
				<p class="flex items-center justify-start">
					{{ getFullLocationText(item) }}
				</p>
			</template>
			<template #right>
				<span />
			</template>
		</ProfileTable>
	</main>
</template>

<script>
import { defineBasicLoader } from 'unplugin-vue-router/data-loaders/basic';
import { useAuthStore } from '@/stores/auth';
// import { useUserStore } from '@/stores/user';
import {
	getFullLocationText,
	mapLocationToSearchParams,
} from '@/util/locationFormatters';
import { deleteFollowedSearch } from '@/api/search';
import { linkAccountWithGithub, signOut, beginOAuthLogin } from '@/api/auth';
import { getUser } from '@/api/user';
import { computed, ref } from 'vue';

const auth = useAuthStore();
// const user = useUserStore();

export const useGithubLink = defineBasicLoader('/profile', async (route) => {
	let linked = false;

	const githubAccessToken = route.query.gh_access_token;

	if (githubAccessToken) {
		await linkAccountWithGithub(githubAccessToken);
		linked = true;
	}

	return linked;
});

export const useProfileData = defineBasicLoader(
	'/profile',
	async () => {
		const response = await getUser();
		return response.data.data;
	},
	{ lazy: true },
);
</script>

<script setup>
import { Button, RecordTypeIcon } from 'pdap-design-system';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faGithub } from '@fortawesome/free-brands-svg-icons';
import { useRoute, useRouter } from 'vue-router';
import { toast } from 'vue3-toastify';
import ProfileAPIKey from './_components/APIKey.vue';
import ProfileTable from './_components/ThreeColumnTable.vue';
import { faLink } from '@fortawesome/free-solid-svg-icons';
import { faCircleXmark } from '@fortawesome/free-regular-svg-icons';
import { generateAPIKey } from '@/api/auth';

const route = useRoute();
const router = useRouter();

const {
	data: didLinkGithub,
	// loading: githubLinking,
	// error: githubLinkingError,
	// reload,
} = useGithubLink();

const {
	data: profileData,
	isLoading: profileLoading,
	// error: profileError,
	reload: refetchProfile,
} = useProfileData();

const requests = computed(() =>
	profileData.value?.data_requests.data.map((req) => ({
		...req,
		to: `/data-request/${req.id}`,
	})),
);
const followedSearches = computed(() =>
	profileData.value?.followed_searches.data.map((search) => {
		const params = new URLSearchParams(mapLocationToSearchParams(search));

		return {
			...search,
			to: `/search/results?${params.toString()}`,
		};
	}),
);
const recentSearches = computed(() =>
	profileData.value?.recent_searches.data.map((search) => {
		const allAt = search.record_categories.indexOf('All');
		const catWithOutAll =
			allAt === -1
				? search.record_categories
				: search.record_categories.toSpliced(allAt);
		const params = new URLSearchParams({
			...mapLocationToSearchParams(search),
			...(catWithOutAll.length
				? {
						record_categories: [...catWithOutAll],
					}
				: {}),
		});

		return {
			...search,
			to: `/search/results?${params.toString()}`,
		};
	}),
);

const apiKey = ref();
const apiKeyIsDismissed = ref(false);

async function createAPIKey() {
	const response = await generateAPIKey();
	apiKey.value = response.data.api_key;
}

async function signOutWithRedirect() {
	auth.setRedirectTo(route);
	await signOut();
	router.replace('/sign-in');
}

async function unFollow(followed) {
	const text = getFullLocationText(followed);
	try {
		await deleteFollowedSearch(followed.id ?? followed.location_id);
		toast.success(`Un-followed search for ${text}`);
		await refetchProfile();
	} catch (error) {
		if (error instanceof Error) {
			console.error(error);
		}
		toast.error(`Error un-following search for ${text}, please try again.`);
	}
}
</script>

<style scoped>
@tailwind utilities;
.dropdown-enter-active,
.dropdown-leave-active {
	transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.dropdown-enter-from,
.dropdown-leave-to {
	transform: translateY(-20px);
	opacity: 0;
}

.dropdown-enter-to,
.dropdown-leave-from {
	transform: translateY(0);
	opacity: 1;
}
</style>

<style>
.profile-loading {
	position: relative;
}

.profile-loading > * {
	opacity: 0;
}

/* Apply loading shimmer effect when parent is loading */
:where([class*='profile-loading']) {
	@apply animate-pulse;
}

.profile-loading {
	position: relative;
	background: #e5e7eb;
	overflow: hidden;
}

.profile-loading::after {
	position: absolute;
	top: 0;
	right: 0;
	bottom: 0;
	left: 0;
	transform: translateX(-100%);
	background-image: linear-gradient(
		90deg,
		rgba(var(--color-gold-neutral-200)) 0,
		rgba(var(--color-gold-neutral-300), 0.2) 20%,
		rgba(var(--color-gold-neutral-400), 0.5) 60%,
		rgba(var(--color-gold-neutral-400), 0)
	);
	animation: shimmer 2s infinite;
	content: '';
	z-index: 999;
}

@keyframes shimmer {
	100% {
		transform: translateX(100%);
	}
}
</style>
