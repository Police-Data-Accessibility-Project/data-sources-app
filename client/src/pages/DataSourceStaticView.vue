<template>
  <div>
    <h2>{{ dataSource.name }}</h2>
    <div class="data-type">
      <h2>Data type</h2>
      <p>{{ dataSource.record_type }}</p>
      <p>{{ dataSource.description }}</p>
    </div>

    <div class="agency">
      <h2>Agency</h2>
      <p>{{ dataSource.agency_name }}</p>
      <p>{{ dataSource.agency_county_name }}</p>
      <p>{{ dataSource.agency_municipality }}</p>
      <p>{{ dataSource.agency_state_iso }}</p>
    </div>

    <div class="access-format">
      <h2>Access & format</h2>
      <p>{{ dataSource.access_type }}</p>
    </div>

    <div class="provenance">
      <h2>Provenance</h2>
    </div>

    <div class="coverage-retention">
      <h2>Coverage & retention</h2>
    </div>

    <div class="data-source-meta">
      <h2>Data Source Meta</h2>
      <!-- Display general data source meta information here -->
      <p>Created: {{ dataSource.data_source_created }}</p>
      <p>Last Modified: {{ dataSource.airtable_source_last_modified }}</p>
    </div>

  </div>
</template>

<script>
import axios from 'axios';
import { BASE_URL } from '../../globals';

export default {
  name: 'DataSourceStaticView',
  data: () => ({
    dataSource: {},
    id: null
  }),
  mounted: function() {
    this.id = this.$route.params.id
    this.getDataSourceDetails()
  }, 
  methods: {
    async getDataSourceDetails() {
      const headers = {"Authorization": `Bearer ${process.env.VUE_APP_PDAP_TOKEN}`}
      const res = await axios.get(`${BASE_URL}/data-sources/${this.id}`, {headers})
      this.dataSource = res.data
    }
  }
}
</script>