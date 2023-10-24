<template>
  <div class="search-result-card small" data-test="search-result-card">
    <div class="search-result-title" data-test="search-result-title">{{ dataSource.data_source_name }}</div>
    <div class="search-result-agency" data-test="search-result-agency">
      <p v-if="dataSource.agency_name" data-test="search-result-agency-known">{{ dataSource.agency_name }}</p>
      <p v-else data-test="search-result-agency-unknown">Agency Unknown</p>
    </div>
    <div class="search-result-place" data-test="search-result-place">
      <p v-if="dataSource.municipality && dataSource.state_iso" data-test="search-result-place-state-municipality">{{ dataSource.municipality }}, {{ dataSource.state_iso }}</p>
      <p v-else-if="dataSource.municipality" data-test="search-result-place-municipality">{{ dataSource.municipality }}</p>
      <p v-else-if="dataSource.state_iso" data-test="search-result-place-state">{{ dataSource.state_iso }}</p>
      <p v-else data-test="search-result-place-unknown">Location Unknown</p>
    </div>
    <p class="search-result-label" v-if="dataSource.record_type" data-test="search-result-record-label">Record type</p>
    <p class="search-result-data" data-test="search-result-record-type" v-if="dataSource.record_type">{{ dataSource.record_type }}</p>
    <p class="search-result-data" v-else data-test="search-result-record-type-unknown">Record Type Unknown</p>
    <p class="search-result-label" data-test="search-result-label-coverage" v-if="dataSource.coverage_start || dataSource.coverage_end">Coverage</p>
    <p class="search-result-data" v-if="dataSource.coverage_start && dataSource.coverage_end" data-test="search-result-coverage-start-end">{{ formatDate(dataSource.coverage_start) }}-{{ formatDate(dataSource.coverage_end) }}</p>
    <p class="search-result-data" v-else-if="dataSource.coverage_start && !dataSource.coverage_end" data-test="search-result-coverage-start">
      {{ formatDate(dataSource.coverage_start) }} - End Date Unknown
    </p>
    <p class="search-result-data" v-else-if="!dataSource.coverage_start && dataSource.coverage_end" data-test="search-result-coverage-end">
      Start Date Unknown - {{ formatDate(dataSource.coverage_end) }}
    </p>
    <p class="search-result-data" v-else data-test="search-result-coverage-unknown">
      Coverage Date Unknown
    </p>
    <p class="search-result-label" data-test="search-result-label-formats">Formats available</p>
    <div v-if="dataSource.record_format" data-test="search-result-formats">
      <p class="search-result-data" :key="recordFormat" v-for="recordFormat in dataSource.record_format" data-test="search-result-format">
        {{ recordFormat }}
      </p>
    </div>
    <p class="search-result-data" data-test="search-result-format-unknown" v-else>Data Formats Unknown</p>
    <button class="button" @click="openSource" :href="dataSource.source_url" data-test="search-result-source-button">Visit Source URL</button>
    <button class="source button" @click="showDetails" data-test="search-result-source-details-button">Source Details</button>
  </div>
</template>

<script>
  export default {
    name: 'SearchResultCard',
    props: {
      dataSource: Object
    },
    methods: {
      showDetails() {
        this.$router.push(`/data-sources/${this.dataSource.airtable_uid}`)
      },
      openSource() {
        window.open(this.dataSource.source_url, '_blank');
      },
      formatDate(date) {
        let newDate = date.split('-')
        let year = newDate.shift()
        newDate.push(year)
        let formattedDate = newDate.join('/')
        return formattedDate
      }
    }
  }
</script>

<style>
.search-result-card {
  border: 1px solid black;
  width: 25%;
  min-width: 200px;
  margin: 1rem;
  padding: 1rem
}

.search-result-title {
  font-weight: bold;
}

.search-result-agency p {
  font-weight: 500;
}

.search-result-agency p, .search-result-place p {
  font-size: 60%;
  font-style: italic;
  line-height: 1;
}

.search-result-label {
  line-height: 1;
  font-weight: 500;
}

.search-result-data {
  line-height: 1;
}

.source {
  background-color: #bfc0c0;
}

@media (prefers-color-scheme: dark) {
  .search-result-card {
    border: 1px solid white;
  }
}
</style>