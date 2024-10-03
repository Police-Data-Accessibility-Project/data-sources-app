<template>
	<main :class="{ content: !isLoading && !error, loading: isLoading }">
		<Spinner
			v-if="isLoading"
			:show="isLoading"
			:size="64"
			text="Fetching data source results..."
		/>

		<template v-else-if="!isLoading && error">
			<h1>An error occurred loading the data source</h1>
			<p>Please refresh the page and try again.</p>
		</template>

		<!-- TODO: not found UI - do we want to send the user to search or something? -->
		<template v-else-if="!dataSource">
			<h1>Data source not found</h1>
			<p>We don't have a record of that source.</p>
		</template>

		<!-- For each section, render details -->
		<template v-else>
			<!-- NAV to prev/next data source -- TODO: only show if user navigates from search results -->
			<nav v-if="mostRecentSearchIds.length" class="self-start">
				<!-- TODO - prev/next logic -->
				<RouterLink
					:to="`/data-source/${mostRecentSearchIds[previousIdIndex]}`"
					:class="{ disabled: typeof previousIdIndex !== 'number' }"
				>
					PREV
				</RouterLink>
				/
				<RouterLink
					:to="`/data-source/${mostRecentSearchIds[nextIdIndex]}`"
					:class="{ disabled: typeof nextIdIndex !== 'number' }"
				>
					NEXT
				</RouterLink>
			</nav>

			<!-- Heading and related material -->
			<hgroup>
				<h1>{{ dataSource.name }}</h1>
				<div class="flex gap-2 items-center">
					<p v-if="dataSource.record_type_name" class="pill w-max">
						<RecordTypeIcon :record-type="dataSource.record_type_name" />
						{{ dataSource.record_type_name }}
					</p>
					<template v-if="Array.isArray(dataSource.tags)">
						<p v-for="tag in dataSource.tags" :key="tag" class="pill w-max">
							{{ tag }}
						</p>
					</template>
				</div>
			</hgroup>

			<!-- Agency data -->
			<div class="flex-[0_0_100%] flex flex-col gap-2 w-full">
				<!-- For each agency, TODO: does UI need to be updated? -->
				<div class="agency-row-container">
					<div class="agency-row">
						<div>
							<h4 class="m-0">Agency</h4>
							<p
								v-for="agency in dataSource.agencies"
								:key="agency.submitted_name"
							>
								{{ agency.submitted_name }}
							</p>
						</div>
						<div>
							<h4 class="m-0">County, State</h4>
							<p
								v-for="agency in dataSource.agencies"
								:key="agency.county_name"
							>
								{{
									// TODO: remove this once API is returning arrays
									formatStringIntoArraysBecauseAPIReturnsStringsRatherThanArrays(
										agency.county_name,
									)[0]
								}}, {{ agency.state_iso }}
							</p>
						</div>
						<div>
							<h4 class="m-0">Agency Type</h4>
							<p
								v-for="agency in dataSource.agencies"
								:key="agency.agency_type"
								class="capitalize"
							>
								{{ agency.agency_type }}
							</p>
						</div>
						<div>
							<h4 class="m-0">Jurisdiction Type</h4>
							<p
								v-for="agency in dataSource.agencies"
								:key="agency.jurisdiction_type"
								class="capitalize"
							>
								{{ agency.jurisdiction_type }}
							</p>
						</div>
					</div>
				</div>
				<a
					:href="dataSource.source_url"
					class="pdap-button-primary py-3 px-4 h-max mr-4"
					target="_blank"
					rel="noreferrer"
				>
					Visit Data Source
					<FontAwesomeIcon :icon="faLink" />
				</a>
			</div>

			<div v-if="dataSource.description" class="description-container">
				<p
					ref="descriptionRef"
					class="description"
					:class="{
						'truncate-2': !isDescriptionExpanded,
					}"
				>
					{{ dataSource.description }}
				</p>
				<Button
					v-if="showExpandDescriptionButton"
					intent="tertiary"
					@click="isDescriptionExpanded = !isDescriptionExpanded"
				>
					{{ isDescriptionExpanded ? 'See less' : 'See more' }}
				</Button>
			</div>

			<!-- Sections -->
			<div
				v-for="section in DATA_SOURCE_UI_SHAPE"
				:key="section.header"
				class="section"
			>
				<h2>{{ section.header }}</h2>
				<div
					v-for="record in section.records"
					:key="record.title"
					class="flex flex-col"
				>
					<!-- Only render if the key exists in the data source record -->
					<template v-if="dataSource[record.key]">
						<h4>{{ record.title }}</h4>

						<!-- If an array, render and nest inside of div -->
						<div v-if="Array.isArray(dataSource[record.key])">
							<component
								:is="record.component ?? 'p'"
								v-for="item in dataSource[record.key]"
								:key="item"
							>
								{{ formatResult(record, item) }}
							</component>
						</div>

						<!-- Otherwise, 1 component -->
						<component
							:is="record.component ?? 'p'"
							v-else
							:href="
								record.component === 'a' ? dataSource[record.key] : undefined
							"
							:class="record.classNames"
							target="record.attributes.target"
							rel="record.attributes.rel"
						>
							{{ formatResult(record, dataSource[record.key]) }}
						</component>
					</template>
				</div>
			</div>
		</template>
	</main>
</template>

<script>
// Data loader
import { defineBasicLoader } from 'unplugin-vue-router/data-loaders/basic';
import { useSearchStore } from '@/stores/search';
import { useRoute } from 'vue-router';

const { getDataSource } = useSearchStore();

export const useDataSourceData = defineBasicLoader(
	'/data-source/:id',
	async (route) => {
		const results = await getDataSource(route.params.id);
		return results?.data?.data;
	},
);
</script>

<script setup>
import { Button, RecordTypeIcon } from 'pdap-design-system';
import { Spinner } from 'pdap-design-system';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faLink } from '@fortawesome/free-solid-svg-icons';

import { DATA_SOURCE_UI_SHAPE } from '@/util/constants';
import formatDateForSearchResults from '@/util/formatDate';
import { computed, onMounted, onUnmounted, ref } from 'vue';

const route = useRoute();
const { mostRecentSearchIds } = useSearchStore();
const { data: dataSource, isLoading, error } = useDataSourceData();

const currentIdIndex = computed(() =>
	mostRecentSearchIds.indexOf(route.params.id),
);
const nextIdIndex = computed(() =>
	currentIdIndex.value < mostRecentSearchIds.length - 1
		? currentIdIndex.value + 1
		: null,
);
const previousIdIndex = computed(() =>
	currentIdIndex.value > 0 ? currentIdIndex.value - 1 : null,
);
const isDescriptionExpanded = ref(false);
const showExpandDescriptionButton = ref(false);
const descriptionRef = ref();

onMounted(() => {
	handleShowMoreButton();
	window.addEventListener('resize', handleShowMoreButton);
});

onUnmounted(() => {
	window.removeEventListener('resize', handleShowMoreButton);
});

function handleShowMoreButton() {
	if (descriptionRef.value?.offsetHeight < descriptionRef.value?.scrollHeight) {
		showExpandDescriptionButton.value = true;
	} else {
		showExpandDescriptionButton.value = false;
	}
}

function formatResult(record, item) {
	if (record.isDate) return formatDateForSearchResults(item);
	return item;
}

/**
 * TODO: remove this function when API returns arrays rather than strings
 */
function formatStringIntoArraysBecauseAPIReturnsStringsRatherThanArrays(str) {
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
.loading {
	@apply flex items-center justify-center h-full w-full;
}

.content {
	@apply flex flex-col sm:flex-row sm:flex-wrap items-center sm:items-stretch sm:justify-between gap-4;
}

.section {
	@apply w-full flex flex-col gap-2 max-w-full md:max-w-[50%] border-solid border-2 border-neutral-300 p-4;
	flex: 1 1 40%;
}

.content hgroup {
	flex: 0 0 100%;
}

.description-container {
	@apply relative w-full mt-4;
}

.description {
	@apply block max-w-full leading-6 max-h-full overflow-hidden;
	transition: max-height 0.3s ease;
}

.description.truncate-2 {
	@apply line-clamp-2 max-h-[calc(2*1.5rem+5px)] md:text-xl;
}

.pdap-button-tertiary {
	@apply text-brand-gold-600 p-1;
}

.agency-row {
	@apply inline-flex gap-8 [&>div]:w-max;
}

.agency-row-container {
	@apply w-full overflow-x-scroll self-start justify-self-start my-4;
}

.disabled {
	@apply pointer-events-none opacity-50;
}
</style>
