<template>
	<main
		class="grid grid-cols-1 grid-rows-[auto_1fr] xl:grid-cols-[1fr_340px] gap-4 xl:gap-x-8 max-w-[1800px] mx-auto"
	>
		<!-- Search results -->
		<section class="w-full h-full">
			<div class="flex flex-col md:flex-row md:justify-between mb-4">
				<div>
					<h1 class="like-h4 mb-4">
						Results
						{{ searchData && 'for ' + getLocationText(searchData.params) }}
					</h1>
					<nav
						v-if="!error"
						class="flex gap-2 mb-4 [&>*]:text-[.72rem] [&>*]:xs:text-med [&>*]:sm:text-lg sm:gap-4"
					>
						<span class="text-neutral-500">Jump to:</span>
						<RouterLink
							v-for="locale in ALL_LOCATION_TYPES"
							:key="`${locale} anchor`"
							class="capitalize"
							:class="{
								'text-neutral-500 pointer-events-none cursor-auto':
									!searchData?.results?.[locale]?.count,
							}"
							:to="{ ...route, hash: `#${locale}` }"
							replace
							@click="
								() =>
									// If route hash already includes locale, handle scroll manually
									route.hash.includes(locale) &&
									searchResultsRef.handleScrollTo()
							"
						>
							{{ getAnchorLinkText(locale) }}
							<span v-if="searchData?.results?.[locale]?.count">
								({{ searchData.results[locale].count }})
							</span>
						</RouterLink>
					</nav>
				</div>
				<div v-if="!isFollowed" class="flex flex-col md:items-end">
					<Button
						:disabled="!isAuthenticated()"
						class="sm:block max-h-12"
						intent="primary"
						@click="
							async () => {
								await follow();
							}
						"
					>
						Follow
					</Button>
					<p v-if="!isAuthenticated()" class="text-med text-neutral-500">
						<RouterLink to="/sign-in" @mouseenter="onSignInMouseEnter">
							Sign in
						</RouterLink>
						to follow this search
					</p>
				</div>
				<div v-else class="flex flex-col md:items-end md:max-w-60">
					<p
						v-if="isAuthenticated()"
						class="text-med text-neutral-500 max-w-full"
					>
						You are following this search. Go to
						<RouterLink to="/profile">your profile</RouterLink> to review saved
						searches or un-follow below.
					</p>

					<Button
						:disabled="!isAuthenticated()"
						class="sm:block max-h-12"
						intent="primary"
						@click="
							async () => {
								await unFollow();
							}
						"
					>
						Un-follow
					</Button>
				</div>
			</div>
			<SearchResults
				v-if="!error && searchData?.results"
				ref="searchResultsRef"
				:results="searchData.results"
				:is-loading="isLoading"
			/>
		</section>

		<!-- Aside for handling filtering and saved searches -->
		<aside
			class="w-full row-start-1 row-end-2 xl:col-start-2 xl:col-end-3 relative z-20"
		>
			<Button
				class="mb-2 w-full xl:hidden"
				intent="primary"
				@click="isSearchShown = !isSearchShown"
			>
				{{ isSearchShown ? 'Hide search' : 'Show search' }}
			</Button>

			<transition>
				<div v-if="isSearchShown" class="max-h-[900px] overflow-hidden mb-8">
					<div class="@container">
						<SearchForm
							:placeholder="
								searchData
									? getLocationText(searchData.params)
									: 'Enter a place'
							"
							button-copy="Update search"
							@searched="onSearchSetIsSearchShown"
						/>
					</div>
				</div>
			</transition>
		</aside>
	</main>
</template>

<script>
// Data loader
import { defineBasicLoader } from 'unplugin-vue-router/data-loaders/basic';
import { useSearchStore } from '@/stores/search';
import { NavigationResult } from 'unplugin-vue-router/runtime';
import { onMounted, onUnmounted, onUpdated, reactive, ref } from 'vue';
import { ALL_LOCATION_TYPES } from '@/util/constants';
import {
	groupResultsByAgency,
	normalizeLocaleForHash,
	getAnchorLinkText,
	getAllIdsSearched,
} from './_util';
import { getMostNarrowSearchLocationWithResults } from '@/util/getLocationText';
import getLocationText from '@/util/getLocationText';
import _isEqual from 'lodash/isEqual';
import { DataLoaderErrorPassThrough } from '@/util/errors';
const search = useSearchStore();

const query = ref();
const data = ref();
const previousRoute = ref();
const isPreviousRouteFollowed = ref(false);

export const useSearchData = defineBasicLoader(
	'/search/results',
	async (route) => {
		try {
			const params = route.query;
			const searched = getMostNarrowSearchLocationWithResults(params);

			const response =
				// Local caching to skip even the pinia method in case of only the hash changing while on the route.
				_isEqual(params, query.value) && data.value
					? data.value
					: await search.search(route.query);

			// On initial fetch - get hash
			const hash = normalizeLocaleForHash(searched, response.data);
			if (!route.hash && hash) {
				return new NavigationResult({ ...route, hash: `#${hash}` });
			}

			data.value = response;
			query.value = params;

			const ret = {
				results: groupResultsByAgency(response.data),
				searched,
				params,
			};
			return ret;
		} catch (error) {
			throw new DataLoaderErrorPassThrough(error);
		}
	},
);

export const useFollowedData = defineBasicLoader(
	'/search/results',
	async (route) => {
		if (isOnlyHashChanged(route, previousRoute.value)) {
			previousRoute.value = route;
			return isPreviousRouteFollowed.value;
		}

		try {
			const params = route.query;
			const isFollowed = await search.getFollowedSearch(params);
			previousRoute.value = route;
			isPreviousRouteFollowed.value = isFollowed;
			return isFollowed;
		} catch (error) {
			throw new DataLoaderErrorPassThrough(error);
		}
	},
);

function isOnlyHashChanged(currentRoute, previousRoute) {
	// If we don't have a previous route to compare against, return false
	if (!previousRoute) return false;

	// Check if queries are equal
	const areQueriesEqual = _isEqual(currentRoute.query, previousRoute.query);

	// Check if paths are equal
	const arePathsEqual = currentRoute.path === previousRoute.path;

	// Check if only the hash is different
	const hasHashChanged = currentRoute.hash !== previousRoute.hash;

	// Return true if everything is the same except the hash
	return areQueriesEqual && arePathsEqual && hasHashChanged;
}
</script>

<script setup>
import { Button } from 'pdap-design-system';
import SearchResults from './_components/SearchResults.vue';
import SearchForm from '@/components/SearchForm.vue';
import { toast } from 'vue3-toastify';
import { useAuthStore } from '@/stores/auth';
import { useRoute } from 'vue-router';

const { isAuthenticated, setRedirectTo } = useAuthStore();
const { data: searchData, isLoading, error } = useSearchData();
const { data: isFollowed, reload: reloadFollowed } = useFollowedData();
const route = useRoute();
const searchResultsRef = ref();
const isSearchShown = ref(false);
const dims = reactive({ width: window.innerWidth, height: window.innerHeight });
const hasDisplayedErrorByRouteParams = ref(new Map());

// lifecycle methods
onMounted(() => {
	if (window.innerWidth > 1280) isSearchShown.value = true;

	if (searchData.value) {
		search.setMostRecentSearchIds(getAllIdsSearched(searchData.value.results));
	}

	window.addEventListener('resize', onWindowWidthSetIsSearchShown);
});

onUpdated(async () => {
	if (error.value) {
		toast.error(
			`Error fetching search results for ${getLocationText(route.query)}. Please try again!`,
			{
				autoClose: false,
				onClose() {
					isSearchShown.value = true;
				},
			},
		);
		hasDisplayedErrorByRouteParams.value.set(JSON.stringify(route.query), true);
	}

	if (searchData.value)
		search.setMostRecentSearchIds(getAllIdsSearched(searchData.value.results));
});

onUnmounted(() => {
	hasDisplayedErrorByRouteParams.value.clear();
	window.removeEventListener('resize', onWindowWidthSetIsSearchShown);
});

// Utilities and handlers
async function follow() {
	try {
		await search.followSearch(route.query);
		toast.success(`Search followed for ${getLocationText(route.query)}.`);
		await reloadFollowed();
	} catch (error) {
		toast.error(`Error following search. Please try again.`);
	}
}
async function unFollow() {
	try {
		await search.deleteFollowedSearch(route.query);
		toast.success(`Search un-followed for ${getLocationText(route.query)}.`);
		await reloadFollowed();
	} catch (error) {
		toast.error(`Error un-following search. Please try again.`);
	}
}

function onSignInMouseEnter() {
	setRedirectTo({ ...route.value });
}

function onWindowWidthSetIsSearchShown() {
	if (window.innerWidth === dims.width) {
		return;
	}

	if (window.innerWidth > 1280) isSearchShown.value = true;
	else isSearchShown.value = false;

	dims.value = { width: window.innerWidth, height: window.innerHeight };
}

function onSearchSetIsSearchShown() {
	if (window.innerWidth < 1280) isSearchShown.value = false;
}
</script>

<style scoped>
.v-enter-active,
.v-leave-active {
	transition:
		opacity 0.5s ease,
		max-height 0.5s ease-in;
}

.v-enter-from,
.v-leave-to {
	opacity: 0;
	max-height: 0;
}
</style>
