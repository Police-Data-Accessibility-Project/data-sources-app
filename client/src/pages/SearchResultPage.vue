<template>
	<FlexContainer
		component="main"
		data-test="search-results-page"
		class="h-auto md:px-0"
	>
		<div>
			<h1>Search results</h1>
			<p data-test="search-results-section-header-p" class="text-2xl">
					Searching for <span class="font-semibold">"{{ searchTerm }}"</span> 
					in <span class="font-semibold">"{{ location }}"</span>.
			</p>
		</div>      
		<GridContainer
			:columns="3"
			templateRows="auto auto 1fr"
			component="section"
			data-test="search"
			class="p-0 gap-6"
		>
			<GridItem v-if="!searched" component="p" :span-column="3">
				Loading results...
			</GridItem>
			<GridItem
				v-else-if="searched && searchResult?.data?.length > 0"
				:span-column="3"
			>
				<p class="text-xl max-w-full">
					<span data-test="search-results-count">Found {{ typeof searchResult.count !== 'undefined' ? (searchResult.count === 0 ? '0 results' : (searchResult.count === 1 ? '1 result' : searchResult.count + ' results')) : '0 results' }}.</span>
					If you don't see what you need, 
					<a href="https://airtable.com/shrbFfWk6fjzGnNsk">
						make a request&nbsp;<i class="fa fa-external-link"></i>
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
	</FlexContainer>

</template>

<script>
import { Button, GridContainer, GridItem } from "pdap-design-system";
import SearchResultCard from "../components/SearchResultCard.vue";
import axios from "axios";

export default {
	name: "SearchResultPage",
	components: {
		SearchResultCard,
		Button,
		GridContainer,
		GridItem,
	},
	data: () => ({
		searched: false,
		searchStatusCode: 200,
		searchResult: {},
		searchTerm: "",
		location: "",
	}),
	mounted: function () {
		this.searchTerm = this.$route.params.searchTerm;
		this.location = this.$route.params.location;
		this.search();
	},
	methods: {
		async search() {
			const url = `${
				import.meta.env.VITE_VUE_APP_BASE_URL
			}/search-tokens?endpoint=quick-search&arg1=${this.searchTerm}&arg2=${
				this.location
			}`;

			try {
				const res = await axios.get(url);
				this.searchStatusCode = res.status;
				this.searchResult = res.data;
				this.searched = true;
			} catch (error) {
				this.searchStatusCode = error?.response?.status ?? 400;
				this.searchResult = error?.response?.data ?? {};
				this.searched = true;
				console.error(error);
			}
		},
	},
};

</script>