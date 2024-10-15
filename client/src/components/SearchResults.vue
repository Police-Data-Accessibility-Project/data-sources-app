<template>
	<div class="flex flex-col w-full gap-5">
		<div class="heading-titles">
			<h4
				v-for="title of HEADING_TITLES"
				:key="title + 'heading'"
				:class="getClassNameFromHeadingType(title)"
			>
				{{ title }}
			</h4>
		</div>

		<div ref="containerRef" class="w-full h-[60vh] relative overflow-y-scroll">
			<Spinner
				v-if="isLoading"
				:show="isLoading"
				:size="64"
				text="Fetching search results..."
			/>
			<template v-else>
				<!-- eslint-disable vue/no-v-for-template-key -->
				<template
					v-for="locale in ALL_LOCATION_TYPES"
					:key="locale + 'results'"
				>
					<template v-if="'count' in results[locale]">
						<div
							:id="'scroll-to-' + locale"
							aria-hidden="true"
							class="w-full"
						/>
						<!-- Header by agency -->
						<template
							v-for="agency in Object.keys(results[locale].sourcesByAgency)"
							:key="agency + 'results'"
						>
							<div class="agency-heading-row">
								<h5>{{ agency }}</h5>
								<span class="pill">{{ locale }}</span>
							</div>

							<!-- Source within each agency -->
							<RouterLink
								v-for="source in results[locale].sourcesByAgency[agency]"
								:key="source.agency_name"
								:to="`/data-source/${source.id}`"
								class="agency-row group"
							>
								<!-- Source name and record type -->
								<div :class="getClassNameFromHeadingType(HEADING_TITLES[0])">
									<h6>
										{{ source.data_source_name }}
									</h6>
									<span class="pill flex items-center gap-2 w-max">
										<RecordTypeIcon :record-type="source.record_type" />
										{{ source.record_type }}
									</span>
								</div>

								<!-- Time range -->
								<p :class="getClassNameFromHeadingType(HEADING_TITLES[1])">
									{{ getYearRange(source.coverage_start, source.coverage_end) }}
								</p>

								<!-- Description -->
								<p :class="getClassNameFromHeadingType(HEADING_TITLES[2])">
									{{ source.description ?? '—' }}
								</p>

								<!-- Formats and links to data source view and data source url -->
								<div :class="getClassNameFromHeadingType(HEADING_TITLES[3])">
									<!-- TODO: when API returns array correctly - uncomment this -->
									<!-- <span
										v-for="format of source.record_format"
										:key="source.data_source_name + format"
										:class="getClassNameFromHeadingType(HEADING_TITLES[3])"
									>
										{{ format }}
									</span> -->
									<!-- And remove this (and the associated utility function) -->
									<span
										v-for="format of formatFormatsBecauseAPIReturnsStringsRatherThanArrays(
											source.record_format,
										)"
										:key="source.data_source_name + format"
										class="format"
									>
										{{ format }}
									</span>
								</div>
								<div class="links">
									<FontAwesomeIcon
										class="hidden lg:inline top-1 text-brand-gold-600 group-hover:text-brand-gold-300"
										:icon="faInfo"
									/>
									<a
										:href="source.source_url"
										target="_blank"
										rel="noreferrer"
										@keydown.stop.enter=""
										@click.stop=""
									>
										<FontAwesomeIcon :icon="faLink" />
										source
									</a>
								</div>
							</RouterLink>
						</template>
					</template>
				</template>
			</template>
		</div>
	</div>
</template>

<script setup>
import { ALL_LOCATION_TYPES } from '@/util/constants';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faInfo, faLink } from '@fortawesome/free-solid-svg-icons';
import { RecordTypeIcon, Spinner } from 'pdap-design-system';
import { useRoute } from 'vue-router';
import { ref, watchEffect } from 'vue';

const route = useRoute();

// constants
const HEADING_TITLES = [
	'agency, name, record type',
	'time range',
	'description',
	'formats',
	'details',
];

const { results, isLoading } = defineProps({
	results: Object,
	isLoading: Boolean,
});

const containerRef = ref();
// Handle scroll to on route hash change
function handleScrollTo() {
	if (route.hash) {
		const scrollToTop = document.getElementById(
			'scroll-to-' + route.hash.replace('#', ''),
		)?.offsetTop;

		containerRef.value?.scrollTo({ top: scrollToTop, behavior: 'smooth' });
	}
}
watchEffect(handleScrollTo);

// TODO: try to handle this with IntersectionObserver instead (i.e. set hash when div intersects, so hash remains up-to-date)
defineExpose({
	handleScrollTo,
});

/**
 * @param start {string} date string
 * @param end {string | undefined} date string
 * @returns string formatted YYYY - YYYY
 */
function getYearRange(start, end) {
	const startYear = new Date(start).getFullYear();
	const endYear = (end ? new Date(end) : new Date()).getFullYear();

	return start ? `${startYear} to ${endYear}` : '—';
}

function getClassNameFromHeadingType(heading) {
	if (heading === 'details') return 'links';
	return heading.replaceAll(',', '').split(' ').join('-');
}

/**
 * TODO: remove this function when API returns arrays
 */
function formatFormatsBecauseAPIReturnsStringsRatherThanArrays(str) {
	if (!str) return [];
	return str
		.replaceAll('[', '')
		.replaceAll(']', '')
		.replaceAll('"', '')
		.split(',')
		.map((s) => s.trim());
}
</script>

<style scoped>
@import url('../main.css');
@tailwind utilities;

/* TODO: decouple heading styling from heading level in design-system (or at least provide classes that can perform these overrides more efficiently) */
h4 {
	@apply m-0 block text-[.65rem] sm:text-med;
}

h5,
h6 {
	@apply text-lg not-italic tracking-normal normal-case m-0;
}

.heading-titles,
.agency-row {
	/* Tailwind is a pain for complex grids, so using standard CSS */
	grid-template-columns: 6fr 2fr 1fr;
	grid-template-areas: 'name name name' 'range formats formats';
	grid-template-rows: repeat(2, auto);
}

.heading-titles {
	@apply w-full items-center grid gap-1 gap-y-3 [&>*]:text-[.7rem] [&>*]:md:text-med [&>*]:lg:text-lg p-2 border-solid border-neutral-300 border-2 lg:border-none;
}

h4.formats {
	@apply break-all overflow-hidden;
}

.agency-heading-row {
	@apply flex items-center sticky top-0 mb-4 justify-between gap-4 bg-neutral-100 p-2 rounded-sm [&>*]:text-xs [&>*]:md:text-med [&>*]:lg:text-lg border-solid border-neutral-300 border-2 z-10;
}

.agency-row {
	@apply grid gap-4 mb-4 p-2 h-auto lg:h-[91px] border-solid border-neutral-300 border-2 rounded-sm [&>*]:text-sm [&>*]:md:text-med [&>*]:lg:text-lg text-neutral-950 hover:bg-neutral-100;
}

.agency-row * {
	@apply [&>*]:text-sm [&>*]:md:text-med [&>*]:lg:text-lg;
}

@media (width >= 768px) {
	.heading-titles,
	.agency-row {
		/* Tailwind is a pain for complex grids, so using standard CSS */
		grid-template-columns: 5fr 2fr 3fr;
		grid-template-areas: 'name name name' 'range formats links';
	}
}

@media (width >= 1024px) {
	.heading-titles,
	.agency-row {
		@apply gap-4;

		grid-template-columns: 320px 125px 1fr 128px 115px;
		grid-template-rows: repeat(1, auto);
		grid-template-areas: 'name range description formats links';
	}
}

.agency-name-record-type {
	grid-area: name;
}

div.agency-name-record-type {
	@apply flex flex-col justify-start gap-2;
}

.agency-name-record-type h6 {
	@apply line-clamp-1;
}

.time-range {
	grid-area: range;
	@apply mb-0 sm:min-w-24;
}

.description {
	@apply hidden m-0;
}

@media (width >= 1024px) {
	.description {
		display: inline-block;
	}

	p.description {
		@apply line-clamp-3 leading-5 max-h-[3.75rem];
	}
}

h4.links {
	@apply hidden md:block;
}

div.links {
	@apply hidden md:flex h-auto gap-2;

	grid-area: links;
}

.formats {
	@apply flex flex-wrap gap-2 justify-start max-w-32 h-max;
	grid-area: formats;
}

div.formats {
	@apply overflow-hidden h-full;
}

.format {
	@apply pill p-0 px-1 text-med inline-block w-min max-w-[8ch] h-min whitespace-nowrap text-ellipsis line-clamp-1;
}
</style>
