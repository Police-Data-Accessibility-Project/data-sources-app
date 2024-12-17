<template>
	<main
		class="grid grid-cols-1 grid-rows-[auto_1fr] xl:grid-cols-[1fr_340px] gap-4 xl:gap-x-8 max-w-[1800px] mx-auto"
	>
		<!-- Search results -->
		<section class="w-full h-full">
			<div
				class="grid grid-cols-1 md:grid-cols-[1fr,auto] md:grid-rows-[repeat(3,35px)]"
			>
				<h1 class="like-h4 mb-4">
					Results
					{{ searchData && 'for ' + getFullLocationText(searchData.params) }}
				</h1>

				<!-- Follow -->
				<div
					v-if="!isFollowed"
					class="flex flex-col md:items-end md:row-start-1 md:row-span-2 md:col-start-2 md:col-span-1"
				>
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
						<RouterLink to="/sign-in"> Sign in </RouterLink>
						to follow this search
					</p>
				</div>
				<div v-else class="flex flex-col md:items-end md:max-w-80">
					<p
						v-if="isAuthenticated()"
						class="text-med text-neutral-500 max-w-full md:text-right"
					>
						You are following this search.<br />
						Review saved searches in
						<RouterLink to="/profile">your profile</RouterLink>
					</p>
				</div>

				<!-- Nav -->
				<nav
					v-if="!error"
					class="flex gap-2 mb-4 [&>*]:text-[.72rem] [&>*]:xs:text-med [&>*]:sm:text-lg sm:gap-4 md:col-start-1 md:col-span-1 md:row-start-2 md:row-span-2 justify-baseline mt-2"
				>
					<span class="text-neutral-500">Jump to:</span>
					<RouterLink
						v-for="locale in ALL_LOCATION_TYPES"
						:key="`${locale} anchor`"
						:class="{
							'text-neutral-500 pointer-events-none cursor-auto':
								!searchData?.results?.[locale]?.count,
						}"
						class="capitalize"
						:to="{ ...route, hash: `#${locale}` }"
						replace
						@click="
							() =>
								// If route hash already includes locale, handle scroll manually
								route.hash.includes(locale) && searchResultsRef.handleScrollTo()
						"
					>
						{{ getAnchorLinkText(locale) }}
						<span v-if="searchData?.results?.[locale]?.count">
							({{ searchData.results[locale].count }})
						</span>
					</RouterLink>
				</nav>
			</div>
			<SearchResults
				v-if="!error && searchData?.results"
				ref="searchResultsRef"
				:results="searchData.results"
				:is-loading="isLoading"
			/>

			<h2 class="like-h4">
				Data requests for {{ getFullLocationText(searchData.params) }}
			</h2>
			<Requests :requests="requestData" :error="!!requestsError" />
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
									? getFullLocationText(searchData.params)
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
import {
	getFullLocationText,
	getMostNarrowSearchLocationWithResults,
} from '@/util/locationFormatters';
import _isEqual from 'lodash/isEqual';
import { DataLoaderErrorPassThrough } from '@/util/errors';
const searchStore = useSearchStore();
import { search, getFollowedSearch, followSearch } from '@/api/search';
import { getLocationDataRequests } from '@/api/locations';

const query = ref();
const data = ref();
const previousRoute = ref();
const isPreviousRouteFollowed = ref(false);

// TODO: split loaders out into separate files
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
					: await search(route.query);

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
		try {
			const params = route.query;
			const isFollowed = await getFollowedSearch(params.location_id);
			previousRoute.value = route;
			isPreviousRouteFollowed.value = isFollowed;
			return isFollowed;
		} catch (error) {
			throw new DataLoaderErrorPassThrough(error);
		}
	},
);

export const useRequestsData = defineBasicLoader(
	'/search/results',
	async (route) => {
		try {
			const requests = await getLocationDataRequests(route.query.location_id);

			return requests.data.data;
		} catch (error) {
			throw new DataLoaderErrorPassThrough(error);
		}
	},
);

// function isOnlyHashChanged(currentRoute, previousRoute) {
// 	// If we don't have a previous route to compare against, return false
// 	if (!previousRoute) return false;

// 	// Check if queries are equal
// 	const areQueriesEqual = _isEqual(currentRoute.query, previousRoute.query);

// 	// Check if paths are equal
// 	const arePathsEqual = currentRoute.path === previousRoute.path;

// 	// Check if only the hash is different
// 	const hasHashChanged = currentRoute.hash !== previousRoute.hash;

// 	// Return true if everything is the same except the hash
// 	return areQueriesEqual && arePathsEqual && hasHashChanged;
// }
</script>

<script setup>
import { Button } from 'pdap-design-system';
import SearchForm from '@/components/SearchForm.vue';
import SearchResults from './_components/SearchResults.vue';
import Requests from './_components/Requests.vue';
import { toast } from 'vue3-toastify';
import { useAuthStore } from '@/stores/auth';
import { useRoute } from 'vue-router';
const { isAuthenticated } = useAuthStore();
const { data: searchData, isLoading, error } = useSearchData();
const { data: isFollowed, reload: reloadFollowed } = useFollowedData();
const { data: requestData, error: requestsError } = useRequestsData();
const route = useRoute();
const searchResultsRef = ref();
const isSearchShown = ref(false);
const dims = reactive({ width: window.innerWidth, height: window.innerHeight });
const hasDisplayedErrorByRouteParams = ref(new Map());

console.debug({ requestData });

// lifecycle methods
onMounted(() => {
	if (window.innerWidth > 1280) isSearchShown.value = true;

	if (searchData.value) {
		searchStore.setMostRecentSearchIds(
			getAllIdsSearched(searchData.value.results),
		);
	}

	if (requestData.value) {
		searchStore.setMostRecentRequestIds(requestData.value.map((req) => req.id));
	}

	window.addEventListener('resize', onWindowWidthSetIsSearchShown);
});

onUpdated(async () => {
	if (error.value) {
		toast.error(
			`Error fetching search results for ${getFullLocationText(route.query)}. Please try again!`,
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
		searchStore.setMostRecentSearchIds(
			getAllIdsSearched(searchData.value.results),
		);

	if (requestData.value) {
		searchStore.setMostRecentRequestIds(requestData.value.map((req) => req.id));
	}
});

onUnmounted(() => {
	hasDisplayedErrorByRouteParams.value.clear();
	window.removeEventListener('resize', onWindowWidthSetIsSearchShown);
});

// Utilities and handlers
async function follow() {
	try {
		await followSearch(route.query.location_id);
		toast.success(`Search followed for ${getFullLocationText(route.query)}.`);
		await reloadFollowed();
	} catch (error) {
		toast.error(`Error following search. Please try again.`);
	}
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
