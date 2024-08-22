<template>
	<main class="p-6 py-10">
		<h1>We help people use police data for public oversight</h1>
		<p>What types of data are you looking for?</p>

		<Form
			id="pdap-data-sources-search"
			class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 auto-rows-auto max-w-full"
			:schema="SCHEMA"
			@submit="submit"
		>
			<div
				class="col-span-1 md:col-span-2 lg:col-span-3 grid grid-cols-[1fr,1fr,auto]"
			>
				<!-- This label is hardcoded to support the PDAP /search functionality. We'll need to pass a prop if we need to use the typeahead element elsewhere -->
				<label class="col-span-2 mt-6 mb-4" :for="TYPEAHEAD_ID">
					<!-- TODO: add paths to these links after search results page built -->
					From where? Example,
					<router-link to="">Pittsburgh, Allegheny, PA</router-link>
					or <router-link to="">Pennsylvania</router-link></label
				>

				<TypeaheadInput
					:id="TYPEAHEAD_ID"
					class="col-span-2 h-full"
					:items="items"
					placeholder="Enter a place"
					@select-item="onSelectRecord"
					@on-input="fetchTypeaheadResults"
				/>

				<Button
					class="col-start-3 col-span-1 max-h-[calc(var(--typeahead-input-height)+2px)]"
					intent="primary"
					type="submit"
				>
					Search Data
				</Button>
			</div>
		</Form>
	</main>
</template>

<script setup>
import { Button, Form } from 'pdap-design-system';
import TypeaheadInput from '@/components/TypeaheadInput.vue';
import axios from 'axios';
import { ref } from 'vue';
import { debounce as _debounce } from 'lodash';

/* constants */
const TYPEAHEAD_ID = 'pdap-search-typeahead';
const SCHEMA = [
	{
		id: 'all-data-types',
		defaultChecked: false,
		name: 'all-data-types',
		label: 'All data types',
		type: 'checkbox',
		value: '',
	},
	{
		id: 'interactions',
		defaultChecked: false,
		name: 'police-and-public-interactions',
		label: 'Police & public interactions',
		type: 'checkbox',
		value: '',
	},
	{
		id: 'info-officers',
		defaultChecked: false,
		name: 'info-about-officers',
		label: 'Info about officers',
		type: 'checkbox',
		value: '',
	},
	{
		id: 'info-agencies',
		defaultChecked: false,
		name: 'info-about-agencies',
		label: 'Info about agencies',
		type: 'checkbox',
		value: '',
	},
	{
		id: 'agency-published-resources',
		defaultChecked: false,
		name: 'agency-published-resources',
		label: 'Agency-published resources',
		type: 'checkbox',
		value: '',
	},
	{
		id: 'jails-and-courts',
		defaultChecked: false,
		name: 'jails-and-courts',
		label: 'Jails and courts specific',
		type: 'checkbox',
		value: '',
	},
];

const items = ref([]);
const selectedRecord = ref();

function submit(values) {
	const params = new URLSearchParams(buildParams(values));

	const path = `/search?${params.toString()}`;

	// Logging for now, will router.push(path) once the search results page is built
	console.log('Path from search:\n', path);
}

function buildParams(values) {
	const obj = {};

	/* Handle record from typeahead input */
	const recordFilteredByParamsKeys = (({ state, county, locality }) => ({
		state,
		county,
		locality,
	}))(selectedRecord.value);

	Object.keys(recordFilteredByParamsKeys).forEach((key) => {
		if (recordFilteredByParamsKeys[key])
			obj[key] = recordFilteredByParamsKeys[key];
	});

	/* Handle form values from checkboxes */
	// Return obj without setting record_types if 'all-data-types' is true or no checkboxes checked
	if (
		values['all-data-types'] === 'true' ||
		Object.values(values).every((val) => !val || val === 'false')
	) {
		return obj;
	}
	// Otherwise set record_types array
	const inputIdsToRecordTypes = new Map(
		SCHEMA.map(({ name, label }) => [name, label]),
	);
	obj.record_categories = Object.entries(values)
		.map(([key, val]) => val === 'true' && inputIdsToRecordTypes.get(key))
		.filter(Boolean);

	return obj;
}

function onSelectRecord(item) {
	selectedRecord.value = item;
	items.value = [];
}

const fetchTypeaheadResults = _debounce(
	async (e) => {
		try {
			if (e.target.value.length > 1) {
				const {
					data: { suggestions },
				} = await axios.get(
					`${import.meta.env.VITE_VUE_API_BASE_URL}/search/typeahead-suggestions`,
					{
						headers: {
							Authorization: import.meta.env.VITE_ADMIN_API_KEY,
						},
						params: {
							query: e.target.value,
						},
					},
				);

				items.value = suggestions.length ? suggestions : undefined;
			} else {
				items.value = [];
			}
		} catch (err) {
			// TODO: handle error UI
			console.error(err);
		}
	},
	350,
	{ leading: true, trailing: true },
);
</script>
