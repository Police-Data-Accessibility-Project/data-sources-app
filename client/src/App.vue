<template>
  <img src="@/assets/logo.svg" class="logo"/>
  <h2 class="quick-search-description">Our mission is to help people locate, understand, and share public records about every U.S. police system. Try giving our database a search to see if we can help you find public records.</h2>
  <QuickSearchForm :searchTerm="searchTerm" :county="county" @handleChange="handleChange" @handleSubmit="handleSubmit"/>
  <button @click="console.log('Clicked advanced search')">Advanced search</button>
  <div v-if="searchResult">
    <p>{{ searchResult }}</p>
  </div>
  <footer>
    <a href="https://airtable.com/shrbFfWk6fjzGnNsk" target="_blank" rel="noopener noreferrer">Request data</a>
    <a href="https://pdap.io/index.html" target="_blank" rel="noopener noreferrer">Ask a question</a>
    <a href="https://airtable.com/shrJafakrcmTxHU2i" target="_blank" rel="noopener noreferrer">Submit a Data Source</a>
    <a href="https://pdap.io/index.html" target="_blank" rel="noopener noreferrer">Report issue</a>
    <a href="https://docs.pdap.io/" target="_blank" rel="noopener noreferrer">Docs</a>
  </footer>
</template>

<script>
import QuickSearchForm from './components/QuickSearchForm.vue';
import {BASE_URL} from '../globals'
import axios from 'axios'

export default {
  name: 'App',
  components: {
    QuickSearchForm
  },
  data: () => ({
    searchTerm: '',
    county: '',
    searchResult: ''
  }),
  methods: {
    handleChange(name, value) {
      this[name] = value
    },
    async handleSubmit() {
      const res = await axios.get(`${BASE_URL}/quick-search/${this.searchTerm}/${this.county}`)
      this.searchResult = res.data
      this.searchTerm = ''
      this.county = ''
    }
  }
}
</script>

<style>
#app {
  font-family: 'Inter', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  margin: 0;
  padding: 1rem;
}

.logo {
  width: 50px;
  margin: 1rem
}

.quick-search-description {
  text-align: center;
}

</style>
