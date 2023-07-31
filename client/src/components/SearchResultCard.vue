<template>
  <div>
    <h3>{{ dataSource.data_source_name }}</h3>
    <h4>{{ dataSource.agency_name }}</h4>
    <h4>{{ dataSource.municipality }}, {{ dataSource.state_iso }}</h4>
    <p>Record type</p>
    <p>{{ dataSource.record_type }}</p>
    <p>Coverage</p>
    <p>{{ dataSource.coverage_start }}-{{ dataSource.coverage_end }}</p>
    <p>Formats available</p>
    <p :key="recordFormat" v-for="recordFormat in dataSource.record_formats">
      {{ recordFormat }}
    </p>
    <button href="dataSource.source_url">Visit Source URL</button>
    <button @click="handleClick">Source details</button>
    <p v-if="expand">
      {{ dataSource.description }}
    </p>
  </div>
</template>

<script>
  export default {
    name: 'SearchResultCard',
    props: {
      dataSource: Object
    },
    data: () => ({
      expand: false
    }),
    methods: {
      handleClick() {
        this.expand = !this.expand
      }
    }
  }
</script>