<template>
  <div class="search-result-card ">
    <p>{{ dataSource.data_source_name }}</p>
    <p v-if="dataSource.agency_name">{{ dataSource.agency_name }}</p>
    <p v-else>Agency Unknown</p>
    <p v-if="dataSource.municipality && dataSource.state_iso">{{ dataSource.municipality }}, {{ dataSource.state_iso }}</p>
    <p v-else-if="dataSource.municipality">{{ dataSource.municipality }}</p>
    <p v-else-if="dataSource.state_iso">{{ dataSource.state_iso }}</p>
    <p v-else>Location Unknown</p>
    <p v-if="dataSource.record_type">Record type</p>
    <p v-if="dataSource.record_type">{{ dataSource.record_type }}</p>
    <p v-else>Record Type Unknown</p>
    <p v-if="dataSource.coverage_start || dataSource.coverage_end">Coverage</p>
    <p v-if="dataSource.coverage_start && dataSource.coverage_end">{{ dataSource.coverage_start }}-{{ dataSource.coverage_end }}</p>
    <p v-else-if="dataSource.coverage_start && !dataSource.coverage_end">
      {{ dataSource.coverage_start }} - End Date Unknown
    </p>
    <p v-else-if="!dataSource.coverage_start && dataSource.coverage_end">
      Start Date Unknown - {{ dataSource.coverage_end }}
    </p>
    <p v-else>
      Coverage Date Unknown
    </p>
    <div v-if="dataSource.record_formats">
      <p>Formats available</p>
      <p :key="recordFormat" v-for="recordFormat in dataSource.record_formats">
        {{ recordFormat }}
      </p>
    </div>
    <p v-else>Data Formats Unknown</p>
    <button @click="openSource" :href="dataSource.source_url">Visit Source URL</button>
    <button @click="showDetails">Source Details</button>
    <p v-if="expand && dataSource.description">
      {{ dataSource.description }}
    </p>
    <p v-else-if="expand && !dataSource.description">No Description Available</p>
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
      showDetails() {
        this.expand = !this.expand
      },
      openSource() {
        window.open(this.dataSource.source_url, '_blank');
      }
    }
  }
</script>

<style>

</style>