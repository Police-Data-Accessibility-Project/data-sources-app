<template>
  <img src="@/assets/logo.svg" class="logo"/>
  <div class="quick-search-card">
    <div class="quick-search-description-div">
      <h3 class="quick-search-description">Our mission is to help people locate, understand, and share public records about every U.S. police system. Try giving our database a search to see if we can help you find public records.</h3>
    </div>
    <QuickSearchForm :searchTerm="searchTerm" :county="county" @handleChange="handleChange" @handleSubmit="handleSubmit"/>
    <div class="advanced-search-button-div">
      <button @click="console.log('Clicked advanced search')" class="advanced-search-button">Advanced Search</button>
    </div>
    <div v-if="searchResult">
      <p>{{ searchResult }}</p>
    </div>
  </div>
  <footer>
    <div class="footer-links">
      <a href="https://airtable.com/shrbFfWk6fjzGnNsk" target="_blank" rel="noopener noreferrer">Request data</a>
      <p>|</p>
      <a href="https://airtable.com/shrJafakrcmTxHU2i" target="_blank" rel="noopener noreferrer">Submit a Data Source</a>
      <p>|</p>
      <a href="https://docs.pdap.io/" target="_blank" rel="noopener noreferrer">Docs</a>
    </div>
    <p class="footer-email">To report an issue or ask a question, email<a href="mailto:contact@pdap.io">contact@pdap.io</a></p>
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

.quick-search-card {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-flow: column wrap;
  height: 75vh;
}

.quick-search-description-div {
  display: flex;
  justify-content: center;
}

.quick-search-description {
  text-align: center;
  width: 50%;
  min-width: 450px;
}

.advanced-search-button-div {
  display: flex;
  justify-content: center;
}

.advanced-search-button {
  width: 50%;
  padding: .5rem 1rem;
  margin: .5rem 0;
  min-width: 450px;
}

footer {
  position: relative;
  bottom: 0;
  width: 100%;
  padding: 1rem 0;
  text-align: center;
}

.footer-links {
  display: flex;
  justify-content: center;
}

footer a, footer p {
  margin: 0 .5rem;
  text-decoration: none;
}

footer p {
  font-weight: bold
}

.footer-email {
  font-weight: normal;
  padding: 1rem 0
}

@media (max-width: 450px) {
  .quick-search-description {
    width: 80%;
    min-width: 50px;
  }

  .advanced-search-button {
    width: 80%;
    min-width: 50px;
  }

  .advanced-search-button-div {
    width: 100%;
  }

  footer a, footer p {
    margin: 0 .25rem;
    font-size: smaller;
  }
}
</style>
