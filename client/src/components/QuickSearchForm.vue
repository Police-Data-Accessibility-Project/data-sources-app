<template>
  <div>
    <form class="quick-search-form" @submit="handleSubmit">
      <div class="quick-search-input-label">
        <label for="searchTerm">What are you looking for?</label>
        <input @input="handleChange" placeholder="Complaints" :value="searchTerm" name="searchTerm" />
      </div>
      <div class="quick-search-input-label">
        <label for="county">From where?</label>
        <input @input="handleChange" placeholder="Allegheny County" :value="county" name="county" />
      </div>
      <button>Search</button>
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
.quick-search-form {
  display: flex;
  justify-content: center;
}

.quick-search-input-label {
  display: flex;
  flex-flow: column-reverse wrap;
  padding: 1rem;
}
</style>