<template>
  <div class="quick-search-card">
    <div class="quick-search-description-div">
      <p class="quick-search-description">Our mission is to help people locate, understand, and share public records about every U.S. police system. Try giving our database a search to see if we can help you find public records.</p>
    </div>
    <QuickSearchForm :searchTerm="searchTerm" :county="county" @handleChange="handleChange" @handleSubmit="handleSubmit"/>
    <!-- <div class="advanced-search-button-div">
      <button @click="console.log('Clicked advanced search')" class="advanced-search-button">Advanced Search</button>
    </div> -->
  </div>
</template>

<script>
import QuickSearchForm from '../components/QuickSearchForm.vue';

export default {
  name: 'QuickSearchPage',
  components: {
    QuickSearchForm
  },
  data: () => ({
    searchTerm: '',
    county: ''
  }),
  methods: {
    handleChange(name, value) {
      this[name] = value
    },
    async handleSubmit() {
      let searchTerm = this.searchTerm
      let county = this.county
      this.searchTerm = ''
      this.county = ''
      this.$router.push(`/search/${searchTerm}/${county}`)
    }
  }
}
</script>

<style>
.quick-search-card {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-flow: column wrap;
  min-height: 75vh;
}

.quick-search-description-div {
  display: flex;
  justify-content: center;
  width: 100%;
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

@media (max-width: 500px) {
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
}
</style>