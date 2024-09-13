<template>
	<div class="flex flex-col w-full gap-5">
		<div class="flex w-full gap-2 h-14 items-center">
			<h4
				v-for="title of HEADING_TITLES"
				:key="title + 'heading'"
				class="block"
				:class="getClassNameFromHeadingType(title)"
			>
				{{ title }}
			</h4>
		</div>

		<div ref="containerRef" class="w-full h-[100vh] relative overflow-y-scroll">
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
					<!-- TODO: use non-existent hash div and scroll within this parent only -->
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
							<div
								class="flex sticky top-0 mb-4 justify-between bg-neutral-200 p-2 rounded-sm [&>*]:text-lg border-none"
							>
								<h5>{{ agency }}</h5>
								<span class="pill">{{ locale }}</span>
							</div>

							<!-- Source within each agency -->
							<div
								v-for="source in results[locale].sourcesByAgency[agency]"
								:key="source.agency_name"
								class="flex gap-2 mb-4 p-2 h-auto lg:h-[91px] flex-wrap lg:flex-nowrap border-solid border-neutral-300 border-2 rounded-sm [&>*]:text-lg"
							>
								<!-- Source name and record type -->
								<div :class="getClassNameFromHeadingType(HEADING_TITLES[0])">
									<h6>
										{{ source.data_source_name }}
									</h6>
									<span class="text-med pill w-max">
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
									<RouterLink :to="`/data-source/${source.airtable_uid}`">
										<FontAwesomeIcon :icon="faInfo" />
									</RouterLink>
									<a :href="source.source_url" target="_blank" rel="noreferrer">
										<FontAwesomeIcon :icon="faLink" />
										source
									</a>
								</div>
							</div>
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
];

// For now we have a single array, but we may need to do some parsing, per https://github.com/Police-Data-Accessibility-Project/data-sources-app/issues/409
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

	return start ? `${startYear} - ${endYear}` : '—';
}

function getClassNameFromHeadingType(heading) {
	return heading.replaceAll(',', '').split(' ').join('-');
}

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
/* TODO: decouple heading styling from heading level in design-system (or at least provide classes that can perform these overrides more efficiently) */
h4 {
	@apply m-0 text-med;
}

h5,
h6 {
	@apply text-lg not-italic tracking-normal normal-case m-0;
}

.agency-name-record-type {
	@apply w-1/2 lg:w-[30%] flex flex-col gap-2;
}

.agency-name-record-type h6 {
	/* Tailwind is a pain, and its line clamp class doesn't work, so defining here instead */
	display: -webkit-box;
	-webkit-line-clamp: 1;
	-webkit-box-orient: vertical;
	overflow: hidden;
}

.time-range {
	@apply w-[20%] lg:w-[15%] mb-0;
}

.description {
	@apply hidden lg:block w-0 lg:w-[35%] leading-5;

	/* Tailwind is a pain, and its line clamp class doesn't work, so defining here instead */
	display: -webkit-box;
	-webkit-line-clamp: 3;
	-webkit-box-orient: vertical;
	overflow: hidden;
}

div.links {
	@apply flex gap-2 w-full lg:w-auto;
}

h4.formats {
	@apply w-[30%];
}

div.formats {
	@apply w-[25%] lg:w-[20%] overflow-hidden;
}

.links {
	@apply w-full lg:w-[10%];
}

div.agency-name-record-type {
	@apply flex flex-col justify-start;
}

.pill {
	@apply text-neutral-800 border-solid border-[1px] border-neutral-500 rounded-xl px-2 bg-neutral-200;
}

.format {
	@apply pill w-min max-w-full px-1 text-med inline-block;

	/* Tailwind is a pain, and its line clamp class doesn't work, so defining here instead */
	display: -webkit-box;
	-webkit-line-clamp: 1;
	-webkit-box-orient: vertical;
	overflow: hidden;
}
</style>
