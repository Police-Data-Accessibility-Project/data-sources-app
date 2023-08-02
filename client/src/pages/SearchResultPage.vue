<template>
  <div class="search-results-page">
    <h2>Search results</h2>
    <div class="loading-section" v-if="!searched">
      <p>Loading results...</p>
    </div>
    <div class="search-results-section" v-else>
      <div class="search-results-section-header small">
        <p>You searched "{{ searchTerm }}" in {{county}} County and you got {{ searchResult.count }} results</p>
        <button class="button" @click="openForm">Missing something? Request data here</button>
      </div>
      <div class="search-results-content" v-if="searchResult.count > 0">
        <SearchResultCard :key="dataSource.uuid" v-for="dataSource in searchResult?.data" :dataSource="dataSource"/>
      </div>
      <div v-else>
        <p>No results found.</p>
      </div>
    </div>
  </div>
</template>

<script>
import SearchResultCard from '../components/SearchResultCard.vue';
import {BASE_URL} from '../../globals'
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
    county: ''
  }),
  mounted: function() {
    this.searchTerm = this.$route.params.searchTerm
    this.county = this.$route.params.county
    this.search()
  },
  methods: {
    async search() {
      const res = await axios.get(`${BASE_URL}/quick-search/${this.searchTerm}/${this.county}`)
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