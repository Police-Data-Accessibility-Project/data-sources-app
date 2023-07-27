<template>
  <img src="@/assets/logo.svg" />
  <h2>Our mission is to help people locate, understand, and share public records about every U.S. police system. Try giving our database a search to see if we can help you find public records.</h2>
  <QuickSearchForm :searchTerm="searchTerm" :county="county" @handleChange="handleChange" @handleSubmit="handleSubmit"/>
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
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
