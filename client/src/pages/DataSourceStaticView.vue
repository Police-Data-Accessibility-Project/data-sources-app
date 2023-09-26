<template>
  <div>
    <h2>{{ dataSource.name }}</h2>
    <div class="data-type">
      <h2>Data type</h2>
      <p>Record type: {{ dataSource.record_type || 'null' }}</p>
      <p>Description: {{ dataSource.description || 'null' }}</p>
      <div v-if="dataSource.tags">
        <p>Tags:</p>
        <p v-for="tag in dataSource.tags" :key="tag">{{ tag }}</p>
      </div>
      <div v-else>
        <p>Tags: null</p>
      </div>
    </div>

    <div class="agency">
      <h2>Agency</h2>
      <p>Name: {{ dataSource.agency_name || 'null'}}</p>
      <p>State: {{ dataSource.state_iso || 'null'}}</p>
      <p v-if="dataSource.county_name">County: {{ dataSource.county_name[0] }}</p>
      <p v-else>County: null</p>
      <p>Municipality: {{ dataSource.municipality || 'null' }}</p>
      <p>Agency Type: {{ dataSource.agency_type || 'null' }}</p>
      <p>Jurisdition Type: {{ dataSource.jurisdiction_type || 'null' }}</p>
    </div>

    <div class="access-format">
      <h2>Access & format</h2>
      <p>Source URL: {{ dataSource.source_url || 'null' }}</p>
      <p>ReadMe URL: {{ dataSource.readme_url || 'null' }}</p>
      <div v-if="dataSource.access_type">
        <p>Access Type:</p>
        <p v-for="access_type in dataSource.access_type" :key="access_type">{{ access_type }}</p>
      </div>
      <div v-else>
        <p>Access Type: null</p>
      </div>
      <div v-if="dataSource.record_format">
        <p>Record Formats:</p>
        <p v-for="record_format in dataSource.record_format" :key="record_format">{{ record_format }}</p>
      </div>
      <div v-else>
        <p>Record Formats: null</p>
      </div>
      <div v-if="dataSource.detail_level">
        <p>Detail Level:</p>
        <p v-for="detail_level in dataSource.detail_level" :key="detail_level">{{ detail_level }}</p>
      </div>
      <div v-else>
        <p>Detail Level: null</p>
      </div>
      <p>Download Options: {{ dataSource.record_download_option_provided || 'null' }}</p>
      <p>Size: {{ dataSource.size || 'null' }}</p>
      <p>Access Restrictions: {{ dataSource.access_restrictions || 'null' }}</p>
      <p>Access Restriction Notes: {{ dataSource.access_restrictions_notes || 'null' }}</p>
      <p>Records Not Online: {{ dataSource.records_not_online || 'null' }}</p>
    </div>

    <div class="provenance">
      <h2>Provenance</h2>
      <p>Agency Supplied: {{ dataSource.agency_supplied || 'null' }}</p>
      <p>Supplying Entity: {{ dataSource.supplying_entity || 'null' }}</p>
      <p>Agency Originated: {{ dataSource.agency_originated || 'null' }}</p>
      <p>Originating Entity: {{ dataSource.originating_entity || 'null' }}</p>
      <p>Community Data Source: {{ dataSource.community_data_source || 'null' }}</p>
    </div>

    <div class="coverage-retention">
      <h2>Coverage & retention</h2>
      <p>Coverage Start Date: {{ dataSource.coverage_start || 'null' }}</p>
      <p>Coverage End Date: {{ dataSource.coverage_end || 'null' }}</p>
      <p>Source Last Updated: {{ dataSource.source_last_updated || 'null' }}</p>
      <p>Update Frequency: {{ dataSource.update_frequency || 'null' }}</p>
      <p>Update Method: {{ dataSource.update_method || 'null' }}</p>
      <p>Sort Method: {{ dataSource.sort_method || 'null' }}</p>
      <p>Retention Schedule: {{ dataSource.retention_schedule || 'null' }}</p>
      <p>Number of Records Available: {{ dataSource.number_of_records_available || 'null' }}</p>
    </div>

    <div class="data-source-meta">
      <h2>Data Source Meta</h2>
      <p>{{ dataSource.scraper_url }}</p>
      <p>Created: {{ dataSource.data_source_created }}</p>
      <p>{{ dataSource.agency_described_linked_uid }}</p>
      <p>{{ dataSource.airtable_uid }}</p>
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