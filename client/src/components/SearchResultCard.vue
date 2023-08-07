<template>
  <div class="search-result-card small">
    <div class="search-result-title">{{ dataSource.data_source_name }}</div>
    <div class="search-result-agency">
      <p v-if="dataSource.agency_name">{{ dataSource.agency_name }}</p>
      <p v-else>Agency Unknown</p>
    </div>
    <div class="search-result-place">
      <p v-if="dataSource.municipality && dataSource.state_iso">{{ dataSource.municipality }}, {{ dataSource.state_iso }}</p>
      <p v-else-if="dataSource.municipality">{{ dataSource.municipality }}</p>
      <p v-else-if="dataSource.state_iso">{{ dataSource.state_iso }}</p>
      <p v-else>Location Unknown</p>
    </div>
    <p class="search-result-label" v-if="dataSource.record_type">Record type</p>
    <p class="search-result-data" v-if="dataSource.record_type">{{ dataSource.record_type }}</p>
    <p class="search-result-data" v-else>Record Type Unknown</p>
    <p class="search-result-label" v-if="dataSource.coverage_start || dataSource.coverage_end">Coverage</p>
    <p class="search-result-data" v-if="dataSource.coverage_start && dataSource.coverage_end">{{ dataSource.coverage_start }}-{{ dataSource.coverage_end }}</p>
    <p class="search-result-data" v-else-if="dataSource.coverage_start && !dataSource.coverage_end">
      {{ formatDate(dataSource.coverage_start) }} - End Date Unknown
    </p>
    <p class="search-result-data" v-else-if="!dataSource.coverage_start && dataSource.coverage_end">
      Start Date Unknown - {{ dataSource.coverage_end }}
    </p>
    <p class="search-result-data" v-else>
      Coverage Date Unknown
    </p>
    <p class="search-result-label">Formats available</p>
    <div v-if="dataSource.record_formats">
      <p class="search-result-data" :key="recordFormat" v-for="recordFormat in dataSource.record_formats">
        {{ recordFormat }}
      </p>
    </div>
    <p class="search-result-data" v-else>Data Formats Unknown</p>
    <button class="button" @click="openSource" :href="dataSource.source_url">Visit Source URL</button>
    <button class="source button" @click="showDetails">Source Details</button>
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