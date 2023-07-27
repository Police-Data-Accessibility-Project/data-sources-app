<template>
  <div>
    <form @submit="handleSubmit">
      <label for="searchTerm">What are you looking for?</label>
      <input @input="handleChange" placeholder="Complaints" :value="searchTerm" name="searchTerm" />
      <label for="county">From where?</label>
      <input @input="handleChange" placeholder="Allegheny County" :value="county" name="county" />
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