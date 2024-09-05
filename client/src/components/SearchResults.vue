<template>
	<div class="flex flex-col w-full gap-5">
		<details
			v-for="location in ALL_LOCATION_TYPES"
			:key="location"
			:open="location === mostSpecificLocationSearched"
		>
			<summary>
				{{ getSummaryText(location) }}
				{{
					`(${results[location].count} ${pluralize('result', results[location].count)})`
				}}
				<FontAwesomeIcon :icon="faAngleUp" />
			</summary>
			<p
				v-if="!results[location].count"
				class="border-solid border-neutral-300 border-2 p-4 max-w-full"
			>
				{{ `No ${location}-level results found` }}
			</p>
			<div
				v-else
				class="border-solid border-neutral-300 border-2 px-4 pb-4 pt-0 flex flex-col gap-2 lg:gap-4 max-h-[400px] md:max-h-[600px] overflow-scroll relative"
			>
				<div class="results-row">
					<h4
						v-for="title of HEADING_TITLES"
						:key="title"
						:class="title.split(' ').join('-').toLowerCase()"
					>
						{{ title }}
					</h4>
				</div>
				<div
					v-for="record of results[location].results"
					:key="record.agency_name + record.record_type"
					class="results-row"
				>
					<p class="agency">{{ record.agency_name }}</p>
					<a
						:href="record.source_url"
						target="_blank"
						rel="noreferrer"
						class="record-type"
					>
						{{ record.record_type }}
					</a>
					<p class="location">
						{{ record.municipality }}, {{ record.state_iso }}
					</p>
					<p class="time-frame">
						{{
							record.coverage_start
								? getYearRange(record.coverage_start, record.coverage_end)
								: 'Unknown'
						}}
					</p>
				</div>
			</div>
		</details>
	</div>
</template>

<script setup>
import pluralize from '@/util/pluralize';

import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faAngleUp } from '@fortawesome/free-solid-svg-icons';

// constants
const ALL_LOCATION_TYPES = ['locality', 'county', 'state', 'federal'];
const HEADING_TITLES = [
	'Agency',
	'Record Type',
	'Location',
	// 'Access Type',
	'Time Frame',
];

// For now we have a single array, but we may need to do some parsing, per https://github.com/Police-Data-Accessibility-Project/data-sources-app/issues/409
const { results, mostSpecificLocationSearched } = defineProps({
	results: Object,
	mostSpecificLocationSearched: String,
});

/**
 * @param start {string} date string
 * @param end {string | undefined} date string
 * @returns string formatted YYYY - YYYY or YYYY - (if the `end` param is not passed)
 */
function getYearRange(start, end) {
	const startYear = new Date(start).getFullYear();
	const endYear = new Date(end).getFullYear();
	const endYearNormalizedForCurrentYear =
		!end || endYear === new Date().getFullYear() ? '' : endYear;

	return `${startYear} - ${endYearNormalizedForCurrentYear}`;
}

function getSummaryText(text) {
	if (text === 'locality') return 'local';
	else return text;
}
</script>

<style scoped>
details summary {
	@apply capitalize flex gap-4 items-center;
}

details[open] summary {
	@apply mb-3 font-medium;
}

details summary svg {
	@apply transition-transform duration-150;
}

details[open] summary svg {
	@apply rotate-180;
}

summary {
	@apply cursor-pointer list-none;
}

.results-row {
	@apply flex items-center gap-2 md:gap-4;
}

.results-row:first-of-type {
	@apply sticky top-0 bg-neutral-50 pt-4;
}

.agency,
.record-type,
.location,
.time-frame {
	@apply basis-[calc(25%-8px)];
}

.agency,
.record-type {
	@apply md:basis-[calc(30%-16px)];
}

.location,
.time-frame {
	@apply md:basis-[calc(20%-16px)];
}

.results-row h4 {
	@apply text-[12px] sm:text-sm md:text-lg;
}

.results-row p,
.results-row a {
	@apply text-[10px] sm:text-xs md:text-sm;
}
</style>
