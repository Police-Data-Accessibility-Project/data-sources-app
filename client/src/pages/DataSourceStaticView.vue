<template>
  <div>
    <div class="data-details-header">
      <h2>{{ dataSource.name }}</h2>
      <button class="button">Edit</button>
    </div>
    <div class="data-details-container">
      <div class="data-detail-section">
        <h2>Data type</h2>
        <p class="large">Record type</p>
        <p class="small">{{ dataSource.record_type || 'null' }}</p>
        <p class="large">Description</p>
        <p class="small">{{ dataSource.description || 'null' }}</p>
        <div v-if="dataSource.tags">
          <p class="large">Tags</p>
          <p v-for="tag in dataSource.tags" :key="tag" class="small">{{ tag }}</p>
        </div>
        <div v-else>
          <p class="large">Tags</p>
          <p class="small">null</p>
        </div>
      </div>

      <div class="data-detail-section">
        <h2>Agency</h2>
        <p class="large">Name</p>
        <p class="small">{{ dataSource.agency_name || 'null' }}</p>
        <p class="large">State</p>
        <p class="small">{{ dataSource.state_iso || 'null' }}</p>
        <div v-if="dataSource.county_name">
          <p class="large">County</p>
          <p class="small">{{ dataSource.county_name[0] }}</p>
        </div>
        <div v-else>
          <p class="large">County</p>
          <p class="small">null</p>
        </div>
        <p class="large">Municipality</p>
        <p class="small">{{ dataSource.municipality || 'null' }}</p>
        <p class="large">Agency Type</p>
        <p class="small">{{ dataSource.agency_type || 'null' }}</p>
        <p class="large">Jurisdiction Type</p>
        <p class="small">{{ dataSource.jurisdiction_type || 'null' }}</p>
      </div>

      <div class="data-detail-section">
        <h2>Access & format</h2>
        <p class="large">Source URL</p>
        <p class="small">{{ dataSource.source_url || 'null' }}</p>

        <p class="large">ReadMe URL</p>
        <p class="small">{{ dataSource.readme_url || 'null' }}</p>

        <div v-if="dataSource.access_type">
          <p class="large">Access Type:</p>
          <p v-for="access_type in dataSource.access_type" :key="access_type" class="small">{{ access_type }}</p>
        </div>
        <div v-else>
          <p class="large">Access Type</p>
          <p class="small">null</p>
        </div>

        <div v-if="dataSource.record_format">
          <p class="large">Record Formats:</p>
          <p v-for="record_format in dataSource.record_format" :key="record_format" class="small">{{ record_format }}</p>
        </div>
        <div v-else>
          <p class="large">Record Formats</p>
          <p class="small">null</p>
        </div>

        <div v-if="dataSource.detail_level">
          <p class="large">Detail Level:</p>
          <p v-for="detail_level in dataSource.detail_level" :key="detail_level" class="small">{{ detail_level }}</p>
        </div>
        <div v-else>
          <p class="large">Detail Level</p>
          <p class="small">null</p>
        </div>

        <p class="large">Download Options</p>
        <p class="small">{{ dataSource.record_download_option_provided || 'null' }}</p>

        <p class="large">Size</p>
        <p class="small">{{ dataSource.size || 'null' }}</p>

        <p class="large">Access Restrictions</p>
        <p class="small">{{ dataSource.access_restrictions || 'null' }}</p>

        <p class="large">Access Restriction Notes</p>
        <p class="small">{{ dataSource.access_restrictions_notes || 'null' }}</p>

        <p class="large">Records Not Online</p>
        <p class="small">{{ dataSource.records_not_online || 'null' }}</p>
      </div>

      <div class="data-detail-section">
        <h2>Provenance</h2>
        <p class="large">Agency Supplied</p>
        <p class="small">{{ dataSource.agency_supplied || 'null' }}</p>

        <p class="large">Supplying Entity</p>
        <p class="small">{{ dataSource.supplying_entity || 'null' }}</p>

        <p class="large">Agency Originated</p>
        <p class="small">{{ dataSource.agency_originated || 'null' }}</p>

        <p class="large">Originating Entity</p>
        <p class="small">{{ dataSource.originating_entity || 'null' }}</p>

        <p class="large">Community Data Source</p>
        <p class="small">{{ dataSource.community_data_source || 'null' }}</p>
      </div>

      <div class="data-detail-section">
        <h2>Coverage & retention</h2>
        <p class="large">Coverage Start Date</p>
        <p class="small">{{ dataSource.coverage_start || 'null' }}</p>

        <p class="large">Coverage End Date</p>
        <p class="small">{{ dataSource.coverage_end || 'null' }}</p>

        <p class="large">Source Last Updated</p>
        <p class="small">{{ dataSource.source_last_updated || 'null' }}</p>

        <p class="large">Update Frequency</p>
        <p class="small">{{ dataSource.update_frequency || 'null' }}</p>

        <p class="large">Update Method</p>
        <p class="small">{{ dataSource.update_method || 'null' }}</p>

        <p class="large">Sort Method</p>
        <p class="small">{{ dataSource.sort_method || 'null' }}</p>

        <p class="large">Retention Schedule</p>
        <p class="small">{{ dataSource.retention_schedule || 'null' }}</p>

        <p class="large">Number of Records Available</p>
        <p class="small">{{ dataSource.number_of_records_available || 'null' }}</p>
      </div>

      <div class="data-detail-section">
        <h2>Data Source Meta</h2>
        <p class="large">Scraper URL</p>
        <p class="small">{{ dataSource.scraper_url || 'null' }}</p>

        <p class="large">Created</p>
        <p class="small">{{ dataSource.data_source_created || 'null' }}</p>

        <p class="large">Agency ID</p>
        <p class="small">{{ dataSource.agency_described_linked_uid || 'null' }}</p>

        <p class="large">Data Source ID</p>
        <p class="small">{{ dataSource.airtable_uid || 'null' }}</p>
      </div>
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

<style scoped>
.data-details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0 1rem;
}

.data-details-header .button {
  height: 50%
}

.data-details-container {
  display: flex;
  flex-flow: row wrap;
  justify-content: center;
  align-items: stretch;
  gap: 2%;
  margin: 4rem 0;
}

.data-detail-section h2 {
  position: absolute;
  top: -1.75em;
  z-index: 1;
  padding: 0 .5em;
  background-color: #fffbfa;
}

.data-detail-section {
  border: #000 1px solid;
  width: 45%;
  padding: 1%;
  position: relative;
  margin: 1% 0;
}

@media (prefers-color-scheme: dark) {
  .data-detail-section {
    border: #fffbfa 1px solid;
  }

  .data-detail-section h2 {
    background-color: #000;
  }
}
</style>