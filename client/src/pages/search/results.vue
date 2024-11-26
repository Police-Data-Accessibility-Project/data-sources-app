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
				<div v-if="!searchData?.isFollowed" class="flex flex-col md:items-end">
					<Button
						:disabled="!isAuthenticated()"
						class="sm:block max-h-12"
						intent="primary"
						@click="
							async () => {
								await follow();
								reload();
							}
						"
					>
						Follow
					</Button>
					<p v-if="!isAuthenticated()" class="text-med text-neutral-500">
						<RouterLink to="/sign-in">Sign in</RouterLink>
						to follow this search
					</p>
				</div>
				<div v-else class="flex flex-col md:items-end max-w-60">
					<p v-if="isAuthenticated()" class="text-med text-neutral-500">
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
								reload();
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
				:results="searchData"
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
import { onBeforeUpdate, onMounted, onUnmounted, reactive, ref } from 'vue';
import { useRoute } from 'vue-router';
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
import { toast } from 'vue3-toastify';
import { IgnoredError } from '@/util/errors';
const search = useSearchStore();

const query = ref();
const data = ref();

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

			const isFollowed = !!(await search.getFollowedSearch(params));

			return {
				results: groupResultsByAgency(response.data),
				searched,
				params,
				isFollowed,
			};
		} catch (error) {
			throw new IgnoredError(error);
		}
	},
	{
		errors: true,
		lazy: true,
	},
);
</script>

<script setup>
import { Button } from 'pdap-design-system';
import SearchResults from './_components/SearchResults.vue';
import SearchForm from '@/components/SearchForm.vue';
import { useAuthStore } from '@/stores/auth';

const { isAuthenticated } = useAuthStore();
const { data: searchData, isLoading, error, reload } = useSearchData();
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

onBeforeUpdate(() => {
	if (
		error.value &&
		!hasDisplayedErrorByRouteParams.value.get(JSON.stringify(route.query))
	) {
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
	window.removeEventListener('resize', onWindowWidthSetIsSearchShown);
});

// Utilities and handlers
async function follow() {
	try {
		await search.followSearch(route.query);
		toast.success(`Search followed for ${getLocationText(route.query)}!`);
	} catch (error) {
		toast.error(`Error saving search. Please try again!`);
	}
}
async function unFollow() {
	try {
		await search.deleteFollowedSearch(route.query);
		toast.success(`Search un-followed for ${getLocationText(route.query)}!`);
	} catch (error) {
		toast.error(`Error un-following search. Please try again!`);
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
