<template>
	<div v-if="!noData">
		<FlexContainer component="header" alignment="center" class="data-details-header">
			<h2>{{ dataSource.name }}</h2>
			<Button>Edit</Button>
		</FlexContainer>
		<FlexContainer alignment="center" class="data-details-container">
			<div v-for="(section, index) in dataToRender" :key="index" class="data-detail-section">
				<h2>{{ section.header }}</h2>
				<div v-for="(record, recordIndex) in section.records" :key="recordIndex">
					<p class="large">{{ record.title }}</p>
					<div v-if="Array.isArray(dataSource[record.key])">
						<p v-for="item in dataSource[record.key]" :key="item" class="small">{{ item }}</p>
					</div>
					<p class="small" v-else>
						{{ dataSource[record.key] || 'null' }}
					</p>
				</div>
			</div>
		</FlexContainer>
	</div>
	<div v-else>
		<h2>{{ errorMessage }}</h2>
	</div>
</template>

<script>
import { Button, FlexContainer } from 'pdap-design-system';
import axios from 'axios';

export default {
	name: 'DataSourceStaticView',
	components: {
		Button,
		FlexContainer,
	},
	data: () => ({
		dataSource: {},
		id: null,
		dataToRender: [
			{
				header: 'Data Type',
				records: [
					{ title: 'Record type', key: 'record_type' },
					{ title: 'Description', key: 'description' },
					{ title: 'Tags', key: 'tags' },
				],
			},
			{
				header: 'Agency',
				records: [
					{ title: 'Name', key: 'agency_name' },
					{ title: 'State', key: 'state_iso' },
					{ title: 'County', key: 'county_name' },
					{ title: 'Municipality', key: 'municipality' },
					{ title: 'Agency Type', key: 'agency_type' },
					{ title: 'Jurisdiction Type', key: 'jurisdiction_type' },
				],
			},
			{
				header: 'Access & format',
				records: [
					{ title: 'Source URL', key: 'source_url' },
					{ title: 'ReadMe URL', key: 'readme_url' },
					{ title: 'Access Type', key: 'access_type' },
					{ title: 'Record Formats', key: 'record_format' },
					{ title: 'Detail Level', key: 'detail_level' },
					{ title: 'Size', key: 'size' },
					{ title: 'Access Notes', key: 'access_notes' },
					{ title: 'Records Not Online', key: 'records_not_online' },
				],
			},
			{
				header: 'Provenace',
				records: [
					{ title: 'Agency Supplied', key: 'agency_supplied' },
					{ title: 'Supplying Entity', key: 'supplying_entity' },
					{ title: 'Agency Originated', key: 'agency_originated' },
					{ title: 'Originating Entity', key: 'originating_entity' },
				],
			},
			{
				header: 'Coverage & retention',
				records: [
					{ title: 'Coverage Start Date', key: 'coverage_start' },
					{ title: 'Coverage End Date', key: 'coverage_end' },
					{ title: 'Source Last Updated', key: 'source_last_updated' },
					{ title: 'Update Frequency', key: 'update_frequency' },
					{ title: 'Update Method', key: 'update_method' },
					{ title: 'Retention Schedule', key: 'retention_schedule' },
					{ title: 'Number of Records Available', key: 'number_of_records_available' },
				],
			},
			{
				header: 'Data Source Meta',
				records: [
					{ title: 'Scraper URL', key: 'scraper_url' },
					{ title: 'Created', key: 'data_source_created' },
					{ title: 'Agency ID', key: 'agency_id' },
					{ title: 'Data Source ID', key: 'data_source_id' },
				],
			},
		],
		noData: true,
		errorMessage: '',
	}),
	mounted: function () {
		this.id = this.$route.params.id;
		this.getDataSourceDetails();
	},
	methods: {
		async getDataSourceDetails() {
			const headers = { Authorization: `Bearer ${process.env.VUE_APP_PDAP_TOKEN}` };
			try {
				const res = await axios.get(
					`${process.env.VUE_APP_BASE_URL}/search-tokens?endpoint=data-sources-by-id&arg1=${this.id}`,
					{ headers }
				);
				this.dataSource = res.data;
				this.noData = false;
			} catch (error) {
				this.errorMessage = error.response.data;
			}
		},
	},
};
</script>

<style scoped>
.data-details-header {
	justify-content: space-between;
	margin: 0 1rem;
}

.data-details-header .pdap-button {
	height: 50%;
}

.data-details-container {
	flex-flow: row wrap;
	align-items: stretch;
	gap: 2%;
	margin: 4rem 0;
}

.data-detail-section h2 {
	position: absolute;
	top: -1.75em;
	z-index: 1;
	padding: 0 0.5em;
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
