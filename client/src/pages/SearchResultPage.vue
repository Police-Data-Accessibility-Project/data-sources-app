<template>
	<GridContainer
		:columns="3"
		templateRows="auto auto 1fr"
		component="section"
		data-test="search-results-page"
	>
	<GridItem :span-column="3">
		<h1>Search results</h1>
	</GridItem>
		<GridItem 
			v-if="!searched" 
			component="p"
			:span-column="3"
		>
			Loading results...
		</GridItem>
		<GridItem 
			v-else 
			:span-column="3"
		>
			<p data-test="search-results-section-header-p" class="text-xl">
				Searching for <span class="font-semibold">"{{ searchTerm }}"</span> 
				in <span class="font-semibold">"{{ location }}"</span>.
				Found {{ typeof searchResult.count !== 'undefined' ? (searchResult.count === 0 ? '0 results' : (searchResult.count === 1 ? '1 result' : searchResult.count + ' results')) : '0 results' }}.
			</p>
			<p class="text-xl">
				If you don't see what you need, 
				<a href="https://airtable.com/shrbFfWk6fjzGnNsk">
					make a request <i class="fa fa-external-link"></i>
				</a>
			</p>
		</GridItem>
		<GridItem
			v-if="searchStatusCode >= 500 && searchStatusCode < 599"
			component="p"
			:span-column="3"
		>
			{{ searchResult.data.message }}
		</GridItem>
		<SearchResultCard
			v-for="dataSource in searchResult?.data"
			v-else-if="searchResult.count > 0"
			:key="dataSource.uuid"
			data-test="search-results-cards"
			:data-source="dataSource"
		/>
		<GridItem
			v-else
			:span-column="3"
			data-test="no-search-results"
			><p>No results found.</p></GridItem
		>
	</GridContainer>
</template>

<script>
import {
	Button,
	FlexContainer,
	GridContainer,
	GridItem,
} from "pdap-design-system";
import SearchResultCard from "../components/SearchResultCard.vue";
import axios from "axios";

export default {
	name: "SearchResultPage",
	components: {
		SearchResultCard,
		Button,
		GridContainer,
		GridItem,
		FlexContainer,
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
			try {
				const res = await axios.get(
					// eslint-disable-next-line no-undef
					`${process.env.VUE_APP_BASE_URL}/search-tokens?endpoint=quick-search&arg1=${this.searchTerm}&arg2=${this.location}`,
				);

				this.searchStatusCode = res.status;
				this.searchResult = res.data;
				this.searched = true;
			} catch (error) {
				this.searchStatusCode = error?.response?.status ?? 400;
				this.searchResult = error?.response?.data ?? {};
				this.searched = true;
				console.log(this.searchResult);
			}
		},
	},
};
</script>