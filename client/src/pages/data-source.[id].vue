<template>
	<main :class="{ content: !isLoading && !error, loading: isLoading }">
		<section class="w-full">
			<Spinner
				:show="isLoading"
				:size="64"
				text="Fetching data source results..."
			/>

			<template v-if="!isLoading && error">
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
				<hgroup>
					<h1>{{ dataSource.name }}</h1>
					<span class="status">
						{{ dataSource.approval_status }}
					</span>
				</hgroup>

				<details
					v-for="section in DATA_SOURCE_UI_SHAPE"
					:key="section.header"
					class="w-full"
				>
					<summary>{{ section.header }}</summary>
					<div
						v-for="record in section.records"
						:key="record.title"
						class="flex items-center justify-between"
					>
						<!-- Only render if the key exists in the data source record -->
						<template v-if="dataSource[record.key]">
							<h6>{{ record.title }}</h6>

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
				</details>
			</template>
		</section>

		<!-- TODO: aside stuff -->
		<aside>
			<h5>Related sources</h5>
			<p>TODO: API not ready yet</p>
			<h5>All requests</h5>
			<p>TODO: API not ready yet</p>
		</aside>
	</main>
</template>

<script>
// Data loader
import { defineBasicLoader } from 'unplugin-vue-router/data-loaders/basic';
import { useSearchStore } from '@/stores/search';

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
import { DATA_SOURCE_UI_SHAPE } from '@/util/pageData';
import formatDateForSearchResults from '@/util/formatDate';

import { Spinner } from 'pdap-design-system';

const { data: dataSource, isLoading, error } = useDataSourceData();

function formatResult(record, item) {
	if (record.isDate) return formatDateForSearchResults(item);
	return item;
}
</script>

<style scoped>
.loading {
	@apply flex items-center justify-center;
}

.content {
	@apply flex justify-between flex-col gap-12 md:flex-row;
}

.content a {
	@apply max-w-[400px];
}

.status {
	@apply mt-1 py-[.125rem] px-3 rounded-full bg-slate-200 dark:bg-slate-600 w-fit capitalize;
}
</style>
