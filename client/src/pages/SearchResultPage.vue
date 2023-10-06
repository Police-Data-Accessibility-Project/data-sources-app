<template>
  <div class="search-results-page" data-test="search-results-page">
    <h2>Search results</h2>
    <div class="loading-section" data-test="loading-section" v-if="!searched">
      <p>Loading results...</p>
    </div>
    <div class="search-results-section" data-test="search-results-section" v-else>
      <div class="search-results-section-header small" >
        <p data-test="search-results-section-header-p">You searched "{{ searchTerm }}" in {{location}} and you got {{ searchResult.count }} results</p>
        <button class="button" data-test="search-results-section-header-button" @click="openForm">Missing something? Request data here</button>
      </div>
      <div class="search-results-content" data-test="search-results-content" v-if="searchResult.count > 0">
        <SearchResultCard data-test="search-results-cards" :key="dataSource.uuid" v-for="dataSource in searchResult?.data" :dataSource="dataSource"/>
      </div>
      <div data-test="no-search-results" v-else>
        <p>No results found.</p>
      </div>
    </div>
  </div>
</template>

<script>
import SearchResultCard from '../components/SearchResultCard.vue';
import axios from 'axios'

export default {
  name: 'SearchResultPage',
  components: {
    SearchResultCard
  },
  data: () => ({
    searched: false,
    searchResult: {},
    searchTerm: '',
    location: ''
  }),
  mounted: function() {
    this.searchTerm = this.$route.params.searchTerm
    this.location = this.$route.params.location
    this.search()
  },
  methods: {
    async search() {
      const headers = {"Authorization": `Bearer ${process.env.VUE_APP_PDAP_TOKEN}`}
      const res = await axios.get(`${process.env.VUE_APP_BASE_URL}/quick-search/${this.searchTerm}/${this.location}`, {headers})
      this.searchResult = res.data
      this.searched = true
    },
    openForm() {
      window.open('https://airtable.com/shrbFfWk6fjzGnNsk', '_blank');
    }
  }
}
</script>

<style>
.loading-section {
  min-height: 75vh;
  text-align: center;
  margin: 2rem 0
}

.search-results-page {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-flow: column wrap;
  min-height: 75vh;
}

.search-results-page h2 {
  width: 75%;
  min-width: 450px;
}

.search-results-section {
  display: flex;
  justify-content: center;
  flex-flow: column wrap;
  width: 75%;
  min-width: 450px;
}

.search-results-section-header {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
}

.search-results-section-header p {
  margin-right: 2rem;
}

.search-results-content {
  display: flex;
  /* justify-content: space-between; */
  flex-wrap: wrap;
}

</style>