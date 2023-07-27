<template>
  <div class="quick-search-component">
    <form class="quick-search-form" @submit="handleSubmit">
      <div class="quick-search-input-label">
        <label for="searchTerm">What are you looking for?</label>
        <input @input="handleChange" placeholder="Complaints" :value="searchTerm" name="searchTerm" />
      </div>
      <div class="quick-search-input-label">
        <label for="county">From where?</label>
        <input @input="handleChange" placeholder="Allegheny County" :value="county" name="county" />
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
    county: String
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
  width: 100%
}

.quick-search-input-label label {
  margin: .5rem 0;
}

.quick-search-button {
  width: 100%;
  padding: .5rem 1rem;
}
</style>