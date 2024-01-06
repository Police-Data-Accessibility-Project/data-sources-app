<template>
	<main v-if="!noData" class="flex flex-col p-8">
		<h1 class="flex justify-start mt-2 w-full">
			{{ dataSource.name }}
		</h1>
		<a class="pdap-button-secondary bg-transparent" href="/"
			>Search for more Data Sources</a
		>
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
								record.isDate
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
import formatDateForSearchResults from "../util/formatDate";

export default {
	name: "DataSourceStaticView",
	data: () => ({
		dataSource: {},
		id: null,
		attributesByComponent: {
			a: {
				target: "_blank",
				rel: "noreferrer",
			},
		},
		dataToRender: [
			{
				header: "Data Type",
				records: [
					{
						title: "Record type",
						key: "record_type",
						classNames:
							"mt-1 py-[.125rem] px-3 rounded-full bg-brand-wine/10 dark:bg-brand-wine dark:text-white w-fit small",
						component: "button",
					},
					{ title: "Description", key: "description" },
					{ title: "Tags", key: "tags" },
				],
			},
			{
				header: "Access & format",
				records: [
					{ title: "Source URL", key: "source_url", component: "a" },
					{ title: "ReadMe URL", key: "readme_url" },
					{ title: "Access Type", key: "access_type" },
					{
						title: "Record Formats",
						key: "record_format",
						classNames:
							"mt-1 py-[.125rem] px-3 rounded-full bg-slate-200 dark:bg-slate-600 w-fit small",
					},
					{ title: "Detail Level", key: "detail_level" },
					{ title: "Size", key: "size" },
					{ title: "Access Notes", key: "access_notes" },
					// records_not_online to be hidden
					// { title: "Records Not Online", key: "records_not_online" },
				],
			},
			{
				header: "Agency",
				records: [
					{
						title: "Name",
						key: "agency_name",
						component: "button",
						classNames:
							"decoration-solid decoration-[6%] text-brand-gold  underline-offset-[5%] hover:brightness-85 small",
					},
					{ title: "State", key: "state_iso" },
					{ title: "County", key: "county_name" },
					{ title: "Municipality", key: "municipality" },
					{ title: "Agency Type", key: "agency_type" },
					{ title: "Jurisdiction Type", key: "jurisdiction_type" },
				],
			},
			{
				header: "Provenace",
				records: [
					{ title: "Agency Supplied", key: "agency_supplied" },
					{ title: "Supplying Entity", key: "supplying_entity" },
					{ title: "Agency Originated", key: "agency_originated" },
					{ title: "Originating Entity", key: "originating_entity" },
				],
			},
			{
				header: "Coverage & retention",
				records: [
					{ title: "Coverage Start Date", key: "coverage_start", isDate: true },
					{ title: "Coverage End Date", key: "coverage_end", isDate: true },
					{
						title: "Source Last Updated",
						key: "source_last_updated",
						isDate: true,
					},
					{ title: "Update Frequency", key: "update_frequency" },
					{ title: "Update Method", key: "update_method" },
					{ title: "Retention Schedule", key: "retention_schedule" },
					{
						title: "Number of Records Available",
						key: "number_of_records_available",
					},
				],
			},
			{
				header: "Data Source Meta",
				records: [
					{ title: "Scraper URL", key: "scraper_url" },
					{ title: "Created", key: "data_source_created", isDate: true },
					{ title: "Agency ID", key: "agency_id" },
					{ title: "Data Source ID", key: "data_source_id" },
				],
			},
		],
		noData: true,
		errorMessage: "",
	}),
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
				this.noData = false;
			} catch (error) {
				this.errorMessage = error.response.data;
			}
		},
		formatDate: formatDateForSearchResults,
	},
};
</script>
