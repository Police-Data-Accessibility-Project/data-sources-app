<template>
	<main data-test="search-results-page" class="flex flex-col p-8 h-auto">
		<div>
			<h1>Data Sources Search results</h1>
			<p data-test="search-results-section-header-p" class="text-2xl">
				Searching for <span class="font-semibold">"{{ searchTerm }}"</span> in
				<span class="font-semibold">"{{ location }}"</span>.
				<span v-if="searched && count > 0" data-test="search-results-count"
					>Found {{ getResultsCopy() }}.</span
				>
			</p>

			<Button class="my-4" intent="secondary" @click="() => $router.push('/')">
				<i class="fa fa-plus" /> New search
			</Button>
		</div>

		<p v-if="!searched" component="p" data-test="loading" :span-column="3">
			Loading results...
		</p>

		<p v-else-if="searched && count === 0" data-test="no-search-results">
			No results found.
		</p>

		<div v-else>
			<p class="text-xl max-w-full">
				If you don't see what you need,
				<a
					href="https://airtable.com/shrbFfWk6fjzGnNsk"
					data-test="search-results-request-link"
				>
					make a request&nbsp;<i class="fa fa-external-link" />
				</a>
			</p>
			<p class="text-xl max-w-full">
				To see these results in a table,
				<a href="https://airtable.com/shrUAtA8qYasEaepI">
					view the full database&nbsp;<i class="fa fa-external-link" />
				</a>
			</p>
		</div>

		<div data-test="search-results">
			<section
				v-for="section in uiShape"
				:key="section.header"
				data-test="search"
				class="mt-8 p-0 w-full"
			>
				<h2 class="section-subheading w-full">
					{{ section.header }}
				</h2>

				<div class="grid pdap-grid-container-column-3 gap-4">
					<ErrorBoundary
						v-for="result in [...getAllRecordsFromSection(section)]"
						:key="result.type"
					>
						<SearchResultCard
							data-test="search-results-cards"
							:data-source="result"
						/>
					</ErrorBoundary>
				</div>
			</section>
		</div>
	</main>
</template>

<script>
import { Button } from 'pdap-design-system';
import SearchResultCard from '../components/SearchResultCard.vue';
import ErrorBoundary from '../components/ErrorBoundary.vue';
import axios from 'axios';
import pluralize from '../util/pluralize';
import { SEARCH_RESULTS_UI_SHAPE } from '../util/pageData';

export default {
	name: 'SearchResultPage',
	components: {
		Button,
		ErrorBoundary,
		SearchResultCard,
	},
	data: () => ({
		count: 0,
		searched: false,
		searchResult: {},
		searchTerm: '',
		location: '',
		uiShape: {},
	}),
	mounted: function () {
		this.searchTerm = this.$route.params.searchTerm;
		this.location = this.$route.params.location;
		this.search();
	},
	methods: {
		getAllRecordsFromSection(section) {
			return section.records.reduce((acc, cur) => {
				return [...acc, ...this.searchResult[cur.type]];
			}, []);
		},
		getResultsCopy() {
			return `${this.count} ${pluralize('result', this.count)}`;
		},
		async search() {
			const url = `${
				import.meta.env.VITE_VUE_API_BASE_URL
			}/search-tokens?endpoint=quick-search&arg1=${this.searchTerm}&arg2=${
				this.location
			}`;

			try {
				const res = await axios.get(url);

				// Format results into object keyed by record_type
				const resultFormatted = res.data.data.reduce((acc, cur) => {
					return {
						...acc,
						[cur.record_type]: Array.isArray(acc[cur.record_type])
							? [...acc[cur.record_type], cur]
							: [cur],
					};
				}, {});

				// Modify ui shape object to exclude any sections / data sources that do not have records returned by API
				this.uiShape = SEARCH_RESULTS_UI_SHAPE.reduce((acc, cur) => {
					const recordsFiltered = cur.records.filter(
						(record) => resultFormatted[record.type],
					);
					return recordsFiltered.length > 0
						? [...acc, { header: cur.header, records: recordsFiltered }]
						: acc;
				}, []);

				// Set data and away we go
				this.searchResult = resultFormatted;
				this.count = res.data.count;
			} catch (error) {
				console.error(error);
			} finally {
				this.searched = true;
			}
		},
	},
};
</script>
