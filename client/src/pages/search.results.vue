<template>
	<main v-if="isLoading" class="loading">
		<Spinner :show="isLoading" :size="64" text="Fetching search results..." />
	</main>
	<main v-else-if="!isLoading && error">
		<h1>Error loading search results</h1>
		<p>Please refresh the page to try again.</p>
	</main>
	<main v-else class="content">
		<!-- Search results -->
		<section class="results">
			<div class="flex flex-col sm:flex-row sm:justify-between mb-4">
				<h1>{{ searchData.results.count }} Search Results</h1>
				<Button
					class="max-h-12"
					intent="secondary"
					@click="() => console.log('New source button pressed')"
				>
					Submit a Source
				</Button>
			</div>
			<SearchResults
				:results="searchData.results.data"
				:most-specific-location-searched="searchData.searched"
			/>
		</section>

		<!-- Open requests -->
		<section class="requests">
			<div class="flex flex-col mb-4 sm:flex-row sm:justify-between">
				<h2>Open Requests</h2>
				<Button
					class="max-h-12"
					intent="secondary"
					@click="() => console.log('New request button pressed')"
				>
					New Request
				</Button>
			</div>
			<div
				class="w-full h-[200px] border-solid border-neutral-300 border-2 p-4"
			>
				TBD
			</div>
		</section>

		<!-- Aside for handling filtering and saved searches -->
		<aside class="sidebar w-full @container">
			<h5 class="w-full not-italic">
				Get notified about updates to sources and requests:
			</h5>
			<Button
				intent="secondary"
				@click="() => console.log('Get notified button pressed')"
			>
				Follow {{ getFollowText(searchData) }}
			</Button>

			<h5 class="w-full not-italic mt-12">Search again:</h5>
			<SearchForm :is-single-column="true" />
		</aside>
	</main>
</template>

<script>
// Data loader
import { defineBasicLoader } from 'unplugin-vue-router/data-loaders/basic';
import { useSearchStore } from '@/stores/search';
import statesToAbbreviations from '@/util/statesToAbbreviations';

const { search } = useSearchStore();

export const useSearchData = defineBasicLoader(
	'/search/results',
	async (route) => {
		const results = await search(route.query);
		const searched = getMostNarrowSearchLocation(route.query);
		return {
			results,
			searched,
			params: route.query,
		};
	},
);

function getMostNarrowSearchLocation(params) {
	if ('locality' in params) return 'locality';
	if ('county' in params) return 'county';
	if ('state' in params) return 'state';
	if ('federal' in params) return 'federal';
}
</script>

<script setup>
import { Button, Spinner } from 'pdap-design-system';
import SearchResults from '@/components/SearchResults.vue';
import SearchForm from '@/components/SearchForm.vue';

const { data: searchData, isLoading, error } = useSearchData();

console.debug({ searchData });

function getFollowText({ searched, params }) {
	switch (searched) {
		case 'locality':
			return `${params.locality}, ${statesToAbbreviations.get(params.state)}`;
		case 'county':
			return `${params.county} ${statesToAbbreviations.get(params.state) === 'LA' ? 'Parish' : 'County'}, ${params.state}`;
		case 'state':
			return params.state;
		default:
			return 'Federal';
	}
}
</script>

<style scoped>
.loading {
	@apply flex items-center justify-center;
}

.content {
	@apply grid gap-4 md:gap-x-8;
	grid-template-areas: 'results' 'requests' 'sidebar';
}

.results {
	grid-area: results;
}

.requests {
	grid-area: requests;
}

.sidebar {
	grid-area: sidebar;
}

@media (min-width: 1024px) {
	.content {
		grid-template-areas:
			'results sidebar'
			'requests sidebar';
		grid-template-columns: 1fr minmax(25%, 30%);
	}
}
</style>

<route>
	{
		meta: {
			breadcrumbText: 'Results'
		}
	}
</route>
