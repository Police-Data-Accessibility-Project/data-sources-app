<template>
	<GridItem
		class="border border-neutral-400 p-3 text-lg leading-snug"
		alignment="center"
		data-test="search-result-card"
	>
		<h2 class="text-xl font-semibold line-clamp-2" data-test="search-result-title">
			{{ dataSource.data_source_name }}
		</h2>
		<p
			class="text-brand-wine font-semibold text-sm uppercase tracking-wider mb-0 mt-4"
			data-test="search-result-record-label"
		>
			Record type
		</p>
		<div
			data-test="search-result-record-type"
			v-if="dataSource.record_type"
			class="mt-1 py-[.125rem] px-3 rounded-full bg-brand-wine/10 w-fit"
		>
			{{ dataSource.record_type }}
		</div>
		<p 
			v-else 
			data-test="search-result-record-type-unknown"
		>
			Unknown
		</p>
		<div class="search-result-agency" data-test="search-result-agency">
			<p
			class="text-brand-wine font-semibold text-sm uppercase tracking-wider mb-0 mt-4"
			data-test="search-result-record-label"
			>
			Agency
		</p>
			<p v-if="dataSource.agency_name" data-test="search-result-agency-known">
				{{ dataSource.agency_name }}
			</p>
			<p v-else data-test="search-result-agency-unknown">Unknown</p>
		</div>
<!-- hiding place for now
		<div data-test="search-result-place">
			<p
				v-if="dataSource.municipality && dataSource.state_iso"
				data-test="search-result-place-state-municipality"
			>
				{{ dataSource.municipality }}, {{ dataSource.state_iso }}
			</p>
			<p v-else-if="dataSource.municipality" data-test="search-result-place-municipality">
				{{ dataSource.municipality }}
			</p>
			<p v-else-if="dataSource.state_iso" data-test="search-result-place-state">
				{{ dataSource.state_iso }}
			</p>
			<p v-else data-test="search-result-place-unknown">Location Unknown</p>
		</div>
-->
		<p
			class="text-brand-wine font-semibold text-sm uppercase tracking-wider mb-0 mt-4"
			data-test="search-result-label-coverage"
		>
			Time range
		</p>
		<p
			v-if="dataSource.coverage_start && dataSource.coverage_end"
			data-test="search-result-coverage-start-end"
		>
			{{ formatDate(dataSource.coverage_start) }}&ndash;{{ formatDate(dataSource.coverage_end) }}
		</p>
		<p
			v-else-if="dataSource.coverage_start && !dataSource.coverage_end"
			data-test="search-result-coverage-start"
		>
			{{ formatDate(dataSource.coverage_start) }}&ndash;Unknown end
		</p>
		<p
			v-else-if="!dataSource.coverage_start && dataSource.coverage_end"
			data-test="search-result-coverage-end"
		>
			Unknown start&ndash;{{ formatDate(dataSource.coverage_end) }}
		</p>
		<p v-else data-test="search-result-coverage-unknown">
			Unknown
		</p>
		<p class="text-brand-wine font-semibold text-sm uppercase tracking-wider mb-0 mt-4" data-test="search-result-label-formats">Formats available</p>
		<ul
			v-if="dataSource.record_format" 
			data-test="search-result-formats"
			class="mb-4"
		>
			<li
				:key="recordFormat"
				v-for="recordFormat in dataSource.record_format"
				data-test="search-result-format"
				class="mt-1 py-[.125rem] px-3 rounded-full bg-slate-200 w-fit"
			>
				{{ recordFormat }}
			</li>
		</ul>
		<p data-test="search-result-format-unknown" v-else>
			Unknown
		</p>
		<Button
			@click="openSource"
			:href="dataSource.source_url"
			class="text-lg px-4 py-1 mb-2 lg:mx-0 w-full"
			data-test="search-result-source-button"
		>
			Visit data source <i class="fa fa-external-link"></i>
		</Button>
		<Button
			@click="showDetails"
			class="text-lg w-full px-4 py-1 lg:mx-0"
			data-test="search-result-source-details-button"
		>
			More details
		</Button>
	</GridItem>
</template>

<script>
import { Button, FlexContainer, GridItem } from 'pdap-design-system';

export default {
	name: 'SearchResultCard',
	components: {
		Button,
		FlexContainer,
		GridItem,
	},
	props: {
		dataSource: Object,
	},
	methods: {
		showDetails() {
			this.$router.push(`/data-sources/${this.dataSource.airtable_uid}`);
		},
		openSource() {
			window.open(this.dataSource.source_url, '_blank');
		},
		formatDate(date) {
			let newDate = date.split('-');
			let year = newDate.shift();
			newDate.push(year);
			let formattedDate = newDate.join('/');
			return formattedDate;
		},
	},
};
</script>