<template>
  <h2>Search results</h2>
  <div v-if="!searched">
    <p>Loading results...</p>
  </div>
  <div v-else>
    <p>You searched "{{ searchTerm }}" for {{county}} County and you got {{ searchResult.count }} results</p>
    <button @click="openForm">Missing something? Request data here</button>
    <div v-if="searchResult.count > 0">
      <SearchResultCard :key="dataSource.uuid" v-for="dataSource in searchResult?.data" :dataSource="dataSource"/>
    </div>
    <div v-else>
      <p>No results found.</p>
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