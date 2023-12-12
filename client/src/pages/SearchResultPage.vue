<template>
	<GridContainer
		alignment="center"
		:columns="3"
		component="main"
		data-test="search-results-page"
	>
		<GridItem v-if="!searched" component="p">Loading results...</GridItem>

		<GridItem v-else :span-column="3" class="small">
			<FlexContainer alignment="center">
				<h2>Search results</h2>
				<p data-test="search-results-section-header-p">
					You searched "{{ searchTerm }}" in {{ location }} and you got
					{{ searchResult.count }} results
				</p>
				<Button
					data-test="search-results-section-header-button"
					@click="openForm"
				>
					Missing something? Request data here
				</Button>
			</FlexContainer>
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
			component="p"
			:span-column="3"
			data-test="no-search-results"
			>No results found.</GridItem
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
		openForm() {
			window.open("https://airtable.com/shrbFfWk6fjzGnNsk", "_blank");
		},
	},
};
</script>