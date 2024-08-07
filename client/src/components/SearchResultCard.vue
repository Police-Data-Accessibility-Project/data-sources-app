<template>
	<div
		class="col-span-1 row-span-1 flex flex-col border border-neutral-400 p-3 text-lg leading-snug"
		data-test="search-result-card"
	>
		<h3
			class="text-xl font-semibold line-clamp-2 normal-case tracking-normal min-h-[50px]"
			data-test="search-result-title"
		>
			{{ dataSource.data_source_name }}
		</h3>

		<Button
			:class="['text-lg font-medium px-4 py-1 mt-4 mb-2 lg:mx-0 max-w-full']"
			:disabled="
				!dataSource.source_url ||
				dataSource.url_status === 'broken' ||
				dataSource.url_status === 'not found'
			"
			data-test="search-result-visit-source-button"
			@click="
				dataSource.source_url &&
				dataSource.url_status !== 'broken' &&
				dataSource.url_status !== 'not found'
					? openSource()
					: null
			"
		>
			Visit data source <i class="fa fa-external-link" />
		</Button>

		<p
			class="text-brand-wine dark:text-white font-semibold text-sm uppercase tracking-wider mb-0 mt-4"
			data-test="search-result-record-label"
		>
			Record type
		</p>
		<div
			v-if="dataSource.record_type"
			data-test="search-result-record-type"
			class="mt-1 py-[.125rem] px-3 rounded-full bg-brand-wine/10 dark:bg-brand-wine dark:text-white w-fit"
		>
			{{ dataSource.record_type }}
		</div>
		<p v-else data-test="search-result-record-type-unknown">Unknown</p>
		<div class="search-result-agency" data-test="search-result-agency">
			<p
				class="text-brand-wine dark:text-white font-semibold text-sm uppercase tracking-wider mb-0 mt-4"
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
			class="text-brand-wine dark:text-white font-semibold text-sm uppercase tracking-wider mb-0 mt-4"
			data-test="search-result-label-coverage"
		>
			Time range
		</p>
		<p
			v-if="dataSource.coverage_start && dataSource.coverage_end"
			data-test="search-result-coverage-start-end"
		>
			{{ formatDate(dataSource.coverage_start) }}&ndash;{{
				formatDate(dataSource.coverage_end)
			}}
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
		<p v-else data-test="search-result-coverage-unknown">Unknown</p>
		<p
			class="text-brand-wine dark:text-white font-semibold text-sm uppercase tracking-wider mb-0 mt-4"
			data-test="search-result-label-formats"
		>
			Formats available
		</p>
		<ul
			v-if="dataSource.record_format"
			data-test="search-result-formats"
			class="mb-4"
		>
			<li
				v-for="recordFormat in dataSource.record_format"
				:key="recordFormat"
				data-test="search-result-format"
				class="mt-1 py-[.125rem] px-3 rounded-full bg-slate-200 dark:bg-slate-600 w-fit"
			>
				{{ recordFormat }}
			</li>
		</ul>
		<p v-else data-test="search-result-format-unknown">Unknown</p>
		<Button
			intent="secondary"
			class="text-lg font-medium px-4 py-1 lg:mx-0 max-w-full mt-auto"
			data-test="search-result-source-details-button"
			@click="showDetails"
		>
			More details
		</Button>
	</div>
</template>

<script>
import { Button } from 'pdap-design-system';
import formatDateForSearchResults from '../util/formatDate';

export default {
	name: 'SearchResultCard',
	components: {
		Button,
	},
	props: {
		dataSource: Object,
	},
	methods: {
		showDetails() {
			this.$router.push(`/data-sources/${this.dataSource.airtable_uid}`);
		},
		openSource() {
			let url = this.dataSource.source_url;
			// ensure URL is treated as an absolute path
			url = this.prepend_protocol_if_none(url);
			window.open(url, '_blank');
		},
		prepend_protocol_if_none(url) {
			// add 'https://' if the URL does not have a protocol
			if (!/^https?:\/\//i.test(url)) {
				return (url = 'https://' + url);
			}
			return url;
		},
		formatDate: formatDateForSearchResults,
	},
};
</script>
