<template>
	<main data-test="search-results-page" class="flex flex-col p-8 h-auto">
		<div>
			<h1>Data Sources Search results</h1>
			<p data-test="search-results-section-header-p" class="text-2xl">
				Searching for <span class="font-semibold">"{{ searchTerm }}"</span> in
				<span class="font-semibold">"{{ location }}"</span>.
				<span
					v-if="searched && searchResult?.data?.length > 0"
					data-test="search-results-count"
					>Found {{ getResultsCopy() }}.</span
				>
			</p>

			<Button class="my-4" intent="secondary" @click="() => $router.push('/')">
				<i class="fa fa-plus" /> New search
			</Button>
		</div>
		<GridContainer
			:columns="3"
			template-rows="auto auto 1fr"
			component="section"
			data-test="search"
			class="p-0 w-full md:max-w-[unset] lg:max-w-[unset]"
		>
			<GridItem
				v-if="!searched"
				component="p"
				data-test="loading"
				:span-column="3"
			>
				Loading results...
			</GridItem>
			<GridItem
				v-else-if="searched && searchResult?.data?.length > 0"
				:span-column="3"
			>
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
			</GridItem>
			<GridItem
				v-else
				:span-column="3"
				component="p"
				data-test="no-search-results"
			>
				No results found.
			</GridItem>
			<SearchResultCard
				v-for="dataSource in searchResult?.data"
				:key="dataSource.uuid"
				data-test="search-results-cards"
				:data-source="dataSource"
			/>
		</GridContainer>
	</main>
</template>

<script>
import { Button, GridContainer, GridItem } from 'pdap-design-system';
import SearchResultCard from '../components/SearchResultCard.vue';
import axios from 'axios';
import pluralize from '../util/pluralize';

export default {
	name: 'SearchResultPage',
	components: {
		Button,
		SearchResultCard,
		GridContainer,
		GridItem,
	},
	data: () => ({
		searched: false,
		searchStatusCode: 200,
		searchResult: {},
		searchTerm: '',
		location: '',
	}),
	mounted: function () {
		this.searchTerm = this.$route.params.searchTerm;
		this.location = this.$route.params.location;
		this.search();
	},
	methods: {
		getResultsCopy() {
			const count = this.searchResult?.data?.length;
			return `${count} ${pluralize('result', count)}`;
		},
		async search() {
			const url = `${
				import.meta.env.VITE_VUE_API_BASE_URL
			}/search-tokens?endpoint=quick-search&arg1=${this.searchTerm}&arg2=${
				this.location
			}`;

			try {
				const res = await axios.get(url);
				this.searchStatusCode = res.status;
				this.searchResult = res.data;
			} catch (error) {
				this.searchStatusCode = error?.response?.status ?? 400;
				this.searchResult = error?.response?.data ?? {};
				console.error(error);
			} finally {
				this.searched = true;
			}
		},
	},
};
</script>
