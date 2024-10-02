<template>
	<main
		class="grid grid-cols-1 xl:grid-cols-[1fr_340px] gap-4 xl:gap-x-8 max-w-[1800px] mx-auto"
	>
		<template v-if="!isLoading && error">
			<h1>Error loading search results</h1>
			<p>Please refresh the page to try again.</p>
		</template>

		<!-- Search results -->
		<section class="w-full h-full">
			<div class="flex flex-col sm:flex-row sm:justify-between mb-4">
				<div>
					<h1>
						Results {{ searchData && 'for ' + getLocationText(searchData) }}
					</h1>
					<nav
						class="flex gap-2 mb-4 [&>*]:text-[.72rem] [&>*]:xs:text-med [&>*]:sm:text-lg sm:gap-4"
					>
						<span class="text-neutral-500">Jump to:</span>
						<a
							v-for="locale in ALL_LOCATION_TYPES"
							:key="`${locale} anchor`"
							class="capitalize"
							:class="{
								'text-neutral-500 pointer-events-none cursor-auto':
									!searchData.results[locale].count,
							}"
							:href="`#${locale}`"
							@click="
								() =>
									// If route hash already includes locale, handle scroll manually
									route.hash.includes(locale) &&
									searchResultsRef.handleScrollTo()
							"
						>
							{{ getAnchorLinkText(locale) }}
							<span v-if="searchData.results[locale].count">
								({{ searchData.results[locale].count }})
							</span>
						</a>
					</nav>
				</div>
				<Button
					class="hidden sm:block max-h-12"
					intent="secondary"
					@click="() => console.log('Follow button pressed')"
				>
					Follow
				</Button>
			</div>
			<SearchResults
				v-if="!error"
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
				intent="secondary"
				@click="isSearchShown = !isSearchShown"
			>
				{{ isSearchShown ? 'Hide search' : 'Show search' }}
			</Button>

			<transition>
				<div v-if="isSearchShown" class="@container">
					<SearchForm
						:placeholder="
							searchData ? getLocationText(searchData) : 'Enter a place'
						"
						button-copy="Update search"
						@searched="onWindowWidthSetIsSearchShown"
					/>
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
import { onMounted, onUnmounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import _isEqual from 'lodash/_baseIsEqual';
import { ALL_LOCATION_TYPES } from '@/util/constants';
import {
	getMostNarrowSearchLocationWithResults,
	groupResultsByAgency,
	normalizeLocaleForHash,
	getLocationText,
	getAnchorLinkText,
	getAllIdsSearched,
} from '@/util/searchResults';

const { search, setMostRecentSearchIds } = useSearchStore();
const results = ref(null);
const params = ref(null);

export const useSearchData = defineBasicLoader(
	'/search/results',
	async (route) => {
		const searched = getMostNarrowSearchLocationWithResults(route.query);
		// If query matches cached query, return cached results
		if (_isEqual(params.value, route.query) && results.value) {
			const r = groupResultsByAgency(results.value);
			// setMostRecentSearchIds(getAllIdsSearched(r));

			return {
				results: r,
				searched,
				params: route.query,
			};
		}

		// Otherwise, fetch, cache, and return
		const res = await search(route.query);
		results.value = res;
		params.value = route.query;

		// On initial fetch - get hash
		const hash = normalizeLocaleForHash(searched, res);
		if (!route.hash) {
			return new NavigationResult({ ...route, hash: `#${hash}` });
		}

		const r = groupResultsByAgency(res);
		// setMostRecentSearchIds(getAllIdsSearched(r));

		return {
			results: r,
			searched,
			params: route.query,
		};
	},
);
</script>

<script setup>
import { Button } from 'pdap-design-system';
import SearchResults from '@/components/SearchResults.vue';
import SearchForm from '@/components/SearchForm.vue';

const { data: searchData, isLoading, error } = useSearchData();
const route = useRoute();
const searchResultsRef = ref();
const isSearchShown = ref(false);

// lifecycle methods
onMounted(() => {
	onWindowWidthSetIsSearchShown();
	setMostRecentSearchIds(getAllIdsSearched(searchData.value.results));
	window.addEventListener('resize', onWindowWidthSetIsSearchShown);
});

onUnmounted(() => {
	window.removeEventListener('resize', onWindowWidthSetIsSearchShown);
});

// Utilities and handlers
function onWindowWidthSetIsSearchShown() {
	if (window.innerWidth > 1280) isSearchShown.value = true;
	else isSearchShown.value = false;
}
</script>

<style scoped>
h1 {
	/* TODO: decouple heading styling from heading level in design-system (or at least provide classes that can perform these overrides more efficiently) */
	@apply text-brand-wine dark:text-neutral-500 font-semibold text-lg tracking-[.07em] uppercase;
}

.v-enter-active,
.v-leave-active {
	transition: opacity 0.5s ease;
}

.v-enter-from,
.v-leave-to {
	opacity: 0;
}
</style>

<route>
	{
		meta: {
			breadcrumbText: 'Results'
		}
	}
</route>
