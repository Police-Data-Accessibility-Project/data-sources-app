<template>
	<main v-if="!noData" class="flex flex-col p-8">
		<h1 class="flex justify-start mt-2 w-full">
			{{ dataSource.name }}
		</h1>
		<PButton intent="secondary" @click="() => $router.push('/')">
			<i class="fa fa-plus" /> New search
		</PButton>
		<div
			alignment="center"
			class="grid grid-cols-[auto] auto-rows-auto gap-4 mx-auto w-full items-start md:grid-cols-2 lg:grid-cols-3"
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
							class="large text-brand-wine dark:text-white font-semibold text-sm uppercase tracking-wider mb-0 mt-4"
						>
							{{ record.title }}
						</p>

						<!-- If no data for this key, em-dash -->
						<div v-if="!dataSource[record.key]" class="text-neutral-500">
							&mdash;
						</div>

						<!-- If data is an array, loop over it and render each -->
						<div v-if="Array.isArray(dataSource[record.key])">
							<component
								:is="record.component ?? 'p'"
								v-for="item in dataSource[record.key]"
								:key="item"
								:class="item?.classNames || small"
								:href="dataSource[record.key]"
								:target="attributesByComponent[record.component]?.target"
								:rel="attributesByComponent[record.component]?.target"
								@click="onClick(record.key, dataSource[record.key])"
							>
								{{ record.isDate ? formatDate(item) : item }}
							</component>
						</div>

						<!-- Otherwise, render single item -->
						<component
							:is="record.component ?? 'p'"
							v-else
							:class="(dataSource[record.key] && record.classNames) || small"
							:href="dataSource[record.key]"
							:target="attributesByComponent[record.component]?.target"
							:rel="attributesByComponent[record.component]?.target"
							@click="onClick(record.key, dataSource[record.key])"
						>
							{{
								record.isDate && dataSource[record.key]
									? formatDate(dataSource[record.key])
									: dataSource[record.key]
							}}
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
import axios from "axios";
/* Updating local button name because it's conflicting with native `<button>` when registered.
 * TODO: add `intent="tertiary"` to design-system, in order to allow unstyled button usage */
import { Button as PButton } from "pdap-design-system";
import formatDateForSearchResults from "../util/formatDate";
import { STATIC_VIEW_UI_SHAPE } from "./util";

export default {
	name: "DataSourceStaticView",
	components: {
		PButton,
	},
	data: function () {
		return {
			dataSource: {},
			id: null,
			attributesByComponent: {
				a: {
					target: "_blank",
					rel: "noreferrer",
				},
			},
			dataToRender: STATIC_VIEW_UI_SHAPE,
			noData: true,
			errorMessage: "",
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
		onClick(key, value) {
			switch (key) {
				case "record_type":
					return this.searchAgain(value, "all");
				case "agency_name":
					return this.searchAgain("all", value);
				default:
					return () => undefined;
			}
		},
		async getDataSourceDetails() {
			const headers = {
				Authorization: `Bearer ${import.meta.env.VUE_APP_PDAP_TOKEN}`,
			};
			try {
				const res = await axios.get(
					`${
						import.meta.env.VITE_VUE_APP_BASE_URL
					}/search-tokens?endpoint=data-sources-by-id&arg1=${this.id}`,
					{ headers },
				);
				this.dataSource = res.data;
				console.log({ data: res.data });
				this.noData = false;
			} catch (error) {
				this.errorMessage = error.response.data;
			}
		},
		formatDate: formatDateForSearchResults,
	},
};
</script>
