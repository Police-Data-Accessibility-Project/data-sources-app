<template>
	<main ref="mainRef" class="min-h-[75%] relative">
		<!-- NAV to prev/next data request -->
		<PrevNextNav
			:request-ids="searchStore.mostRecentRequestIds"
			:previous-index="previousIdIndex"
			:next-index="nextIdIndex"
			:set-nav-is="(val) => (navIs = val)"
		/>

		<transition mode="out-in" :name="navIs">
			<div
				v-if="isLoading"
				class="flex items-center justify-center h-[80vh] w-full flex-col relative"
			>
				<Spinner
					:show="isLoading"
					:size="64"
					text="Fetching data source results..."
				/>
			</div>

			<div
				v-else
				class="flex flex-col sm:flex-row sm:flex-wrap mt-6 sm:items-stretch sm:justify-between gap-4 h-full w-full relative [&>*]:w-full"
			>
				<template v-if="!isLoading && error">
					<h1>An error occurred loading the data request</h1>
					<p>Please refresh the page and try again.</p>
				</template>

				<!-- TODO: not found UI - do we want to send the user to search or something? -->
				<template v-else-if="!error && !dataRequest">
					<h1>Data source not found</h1>
					<p>We don't have a record of that source.</p>
				</template>
				<!-- For each section, render details -->
				<template v-else>
					<!-- Heading and related material -->
					<hgroup>
						<h1>{{ dataRequest.title }}</h1>
						<div class="flex gap-2 items-center">
							<div v-if="dataRequest.record_types_required">
								<p
									v-for="type of dataRequest.record_types_required"
									:key="type.record_types_required"
									class="pill w-max"
								>
									<RecordTypeIcon :record-type="type" />
									{{ type }}
								</p>
							</div>
						</div>
					</hgroup>

					<!-- Location data -->
					<h4>Locations covered by request</h4>
					<p v-for="location of dataRequest.locations" :key="location">
						{{ formatLocationText(location) }}
					</p>

					<h4>Coverage Range</h4>
					<p>{{ dataRequest.coverage_range }}</p>

					<h4>Target date</h4>
					<p>{{ REQUEST_URGENCY[dataRequest.request_urgency] }}</p>

					<h4>Request notes</h4>
					<p class="break-words">{{ dataRequest.submission_notes }}</p>

					<h4>Data requirements</h4>
					<p class="break-words">{{ dataRequest.data_requirements }}</p>

					<a
						v-if="dataRequest.github_issue_url"
						:href="dataRequest.github_issue_url"
						class="pdap-button-primary mt-2 mb-4"
						_target="blank"
						rel="noreferrer"
					>
						Help out with this issue on Github
						<FontAwesomeIcon :icon="faLink" />
					</a>
				</template>
			</div>
		</transition>
	</main>
</template>

<script>
// Data loader
import { defineBasicLoader } from 'unplugin-vue-router/data-loaders/basic';
import { useRoute, useRouter } from 'vue-router';
import { useSwipe } from '@vueuse/core';
import { ref } from 'vue';
import { useDataRequestsStore } from '@/stores/data-requests';
import { DataLoaderErrorPassThrough } from '@/util/errors';
import { getDataRequest } from '@/api/data-requests';

const dataRequestsStore = useDataRequestsStore();

export const useDataRequestData = defineBasicLoader(
	'/request/:id',
	async (route) => {
		const dataSourceId = route.params.id;

		try {
			const results = await getDataRequest(dataSourceId);
			// Then set current route to prev before returning data
			dataRequestsStore.setPreviousDataRequestRoute(route);
			return results.data.data;
		} catch (error) {
			throw new DataLoaderErrorPassThrough(error);
		}
	},
);
</script>

<script setup>
import { RecordTypeIcon, Spinner } from 'pdap-design-system';
import PrevNextNav from './_components/Nav.vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faLink } from '@fortawesome/free-solid-svg-icons';
import { useSearchStore } from '@/stores/search';
import { formatLocationText } from './_util';
import { REQUEST_URGENCY } from './_constants';
import { computed, onMounted, onUnmounted, watch } from 'vue';

const route = useRoute();
const router = useRouter();
const searchStore = useSearchStore();
const { data: dataRequest, isLoading, error } = useDataRequestData();

const currentIdIndex = computed(() =>
	// Route params are strings, but the ids are stored as numbers, so cast first
	searchStore.mostRecentRequestIds.indexOf(Number(route.params.id)),
);
const nextIdIndex = computed(() =>
	currentIdIndex.value < searchStore.mostRecentRequestIds.length - 1
		? currentIdIndex.value + 1
		: null,
);
const previousIdIndex = computed(() =>
	currentIdIndex.value > 0 ? currentIdIndex.value - 1 : null,
);

const showExpandDescriptionButton = ref(false);
const descriptionRef = ref();
const mainRef = ref();
const navIs = ref('');

// Handle swipe
const { isSwiping, direction } = useSwipe(mainRef);
watch(
	() => isSwiping.value,
	(isNowSwiping) => {
		if (isNowSwiping) {
			switch (direction.value) {
				case 'left':
					navIs.value = 'increment';
					router.replace(
						`/data-source/${searchStore.mostRecentRequestIds[nextIdIndex.value]}`,
					);
					break;
				case 'right':
					navIs.value = 'decrement';
					router.replace(
						`/data-source/${searchStore.mostRecentRequestIds[previousIdIndex.value]}`,
					);
					break;
				default:
					return;
			}
		}
	},
);

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

// function formatResult(record, item) {
// 	if (record.isDate) return formatDateForSearchResults(item);
// 	return item;
// }
</script>

<style scoped>
.increment-enter-active,
.increment-leave-active,
.decrement-enter-active,
.decrement-leave-active {
	transition:
		opacity 150ms ease-in,
		transform 150ms ease-in;
}

.increment-enter-from,
.increment-leave-to,
.decrement-enter-from,
.decrement-leave-to {
	opacity: 0;
}

.increment-enter-from,
.decrement-leave-to {
	transform: translateX(15%);
}

.decrement-enter-from,
.increment-leave-to {
	transform: translateX(-15%);
}
</style>
