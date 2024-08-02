<template>
	<main
		v-if="!noData"
		class="flex flex-col p-8 w-full"
		data-test="data-source-static-view"
	>
		<h1 class="flex justify-start mt-2 w-full">
			{{ dataSource.name }}
		</h1>
		<Button
			data-test="new-search-button"
			class="new-search"
			intent="secondary"
			@click="() => $router.push('/')"
		>
			<i class="fa fa-plus" /> New search
		</Button>
		<div
			alignment="center"
			class="grid grid-cols-1 w-full auto-rows-auto gap-4 mx-auto items-start md:grid-cols-2 lg:grid-cols-3"
		>
			<!-- Each card -->
			<div
				v-for="(section, index) in dataToRender"
				:key="index"
				class="flex self-stretch flex-col text-lg"
			>
				<div class="border border-neutral-400 h-full leading-snug p-3 mt-8">
					<h2 class="text-xl font-semibold line-clamp-2">
						{{ section.header }}
					</h2>

					<!-- Within each card, the items listed -->
					<div
						v-for="(record, recordIndex) in section.records"
						:key="recordIndex"
					>
						<!-- Title -->
						<p
							v:if="record.title"
							class="large text-brand-wine dark:text-white font-semibold text-sm uppercase tracking-wider mb-0 mt-4"
						>
							{{ record.title }}
						</p>

						<!-- If no data for this key, em-dash -->
						<div
							v-if="!dataSource[record.key] && !dataSource[record.renderIf]"
							class="text-neutral-500"
						>
							&mdash;
						</div>

						<!-- If data is an array and returned from API, loop over it and render each -->
						<div v-if="Array.isArray(dataSource[record.key])">
							<component
								:is="
									dataSource[record.key] && record.component
										? record.component
										: 'p'
								"
								v-for="item in dataSource[record.key]"
								:key="item"
								:class="record?.classNames"
								:data-test="record['data-test'] ?? 'data-source-item'"
								:href="dataSource[record.key]"
								:intent="record?.attributes?.intent"
								:target="record?.attributes?.target"
								:rel="record?.attributes?.target"
								@click="onClick(record.key, dataSource[record.key])"
							>
								{{
									record.isDate && dataSource[record.key]
										? formatDate(item)
										: item
								}}
							</component>
						</div>

						<!-- Otherwise, if single item returned from API, render that item  -->
						<!-- TODO: Abstract this duplicate logic into a render function (https://vuejs.org/guide/extras/render-function) to decrease repetition  -->
						<component
							:is="
								dataSource[record.key] && record.component
									? record.component
									: 'p'
							"
							v-else-if="dataSource[record.key]"
							:class="record?.classNames"
							:data-test="record['data-test'] ?? 'data-source-item'"
							:href="dataSource[record.key]"
							:intent="record?.attributes?.intent"
							:target="record?.attributes?.target"
							:rel="record?.attributes?.target"
							@click="onClick(record.key, dataSource[record.key])"
						>
							{{
								record.isDate && dataSource[record.key]
									? formatDate(dataSource[record.key])
									: dataSource[record.key]
							}}
						</component>

						<!-- Otherwise, this isn't returned from API, we need to do it ourselves -->
						<component
							:is="record.component ? record.component : 'p'"
							v-else-if="dataSource[record.renderIf]"
							:class="record?.classNames"
							:data-test="record['data-test'] ?? 'data-source-item'"
							:href="record?.href"
							:intent="record?.attributes?.intent"
							:target="record?.attributes?.target"
							:rel="record?.attributes?.target"
							@click="onClick(record.key, dataSource[record.key])"
						>
							{{ record.isDate ? formatDate(record.text) : record.text }}
							<i v-if="record.icon" :class="'fa' + ' ' + record.icon" />
						</component>
					</div>
				</div>
			</div>
		</div>
	</main>
	<main v-else>
		<h2>{{ errorMessage }}</h2>
	</main>
</template>

<script>
import axios from 'axios';
import { Button } from 'pdap-design-system';
import formatDateForSearchResults from '@/util/formatDate';
import { STATIC_VIEW_UI_SHAPE } from '@/util/pageData.js';

export default {
	name: 'DataSourceStaticView',
	components: {
		Button,
	},
	data: function () {
		return {
			dataSource: {},
			id: null,
			dataToRender: STATIC_VIEW_UI_SHAPE,
			noData: true,
			errorMessage: '',
		};
	},
	mounted: function () {
		this.id = this.$route.params.id;
		this.getDataSourceDetails();
	},
	methods: {
		searchAgain(searchTerm, location) {
			this.$router.push(`/search/${searchTerm}/${location}`);
		},
		navigateTo(to) {
			window.open(to, '_blank');
		},
		onClick(key, value) {
			switch (key) {
				case 'record_type':
					return this.searchAgain(value, 'all');
				case 'agency_name':
					return this.searchAgain('all', value);
				case 'source_url_cache':
					return this.navigateTo(
						`https://web.archive.org/web/*/${this.dataSource.source_url}`,
					);
				default:
					return undefined;
			}
		},
		async getDataSourceDetails() {
			try {
				const res = await axios.get(
					`${
						import.meta.env.VITE_VUE_API_BASE_URL
					}/search-tokens?endpoint=data-sources-by-id&arg1=${this.id}`,
				);
				this.dataSource = res.data;
				this.noData = false;
			} catch (error) {
				this.errorMessage = error?.message;
			}
		},
		formatDate: formatDateForSearchResults,
	},
};
</script>

<style scoped>
/* Reset secondary button horizontal margin. TODO: update this in design-system */
.pdap-button-secondary {
	@apply mx-0;
}
.pdap-button-secondary:not(.new-search) {
	@apply my-2;
}
</style>
./pageData
