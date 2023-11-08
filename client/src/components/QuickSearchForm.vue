<template>
  <div class="quick-search-component">
    <form class="quick-search-form" @submit="handleSubmit">
      <div class="quick-search-input-label">
        <label for="searchTerm">What are you looking for?</label>
        <input @input="handleChange" placeholder="Enter a keyword or type of public records, or 'all'" :value="searchTerm" name="searchTerm" />
      </div>
      <div class="quick-search-input-label">
        <label for="location">From where?</label>
        <input @input="handleChange" placeholder="Enter a state abbreviation, county, muncipipality, or 'all'" :value="location" name="location" />
      </div>
      <button class="quick-search-button">Search Data Sources</button>
    </form>
  </div>
</template>

<script>
export default {
  name: 'QuickSearchForm',
  props: {
    searchTerm: String,
    location: String
  },
  methods: {
    handleChange(e) {
      this.$emit('handleChange', e.target.name, e.target.value)
    },
    handleSubmit(e) {
      e.preventDefault()
      this.$emit('handleSubmit')
    }
  }
}
</script>

<style>
.quick-search-component {
  display: flex;
  justify-content: center; 
  width: 100%;
}

.quick-search-form {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  width: 50%;
  min-width: 450px;
}

.quick-search-input-label {
  display: flex;
  flex-flow: column-reverse wrap;
  padding: 1rem 0;
  width: 45%;
}

.quick-search-input-label input {
  padding: .5rem .25rem;
  width: 100%;
  line-height: 1.5;
  font-weight: normal;
}

.quick-search-input-label label {
  margin: .5rem 0;
}

.quick-search-button {
  width: 100%;
  padding: .5rem 1rem;
}

@media (max-width: 1400px) {
  .quick-search-input-label label {
    font-size: 1rem;
  }
}

@media (max-width: 500px) {
  .quick-search-input-label {
    width: 100%;
  }
  .quick-search-form {
    width: 80%;
    min-width: 50px;
  }
}
</style>