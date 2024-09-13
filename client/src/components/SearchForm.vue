<template>
	<Form
		id="pdap-data-sources-search"
		ref="formRef"
		class="grid grid-cols-1 auto-rows-auto max-w-full gap:0 md:gap-4"
		:class="{
			'md:grid-cols-2 lg:grid-cols-3 gap-0': !isSingleColumn,
		}"
		:schema="SCHEMA"
		@change="onChange"
		@submit="submit"
	>
		<div
			class="col-span-1 flex flex-col gap-6"
			:class="{
				'md:col-span-2 lg:col-span-3 md:flex-row md:gap-0': !isSingleColumn,
			}"
		>
			<TypeaheadInput
				:id="TYPEAHEAD_ID"
				class=""
				:items="items"
				placeholder="Enter a place"
				@select-item="onSelectRecord"
				@on-input="fetchTypeaheadResults"
			>
				<!-- Pass label as slot to typeahead -->
				<template #label>
					<label class="col-span-2 mt-6 mb-4" :for="TYPEAHEAD_ID">
						From where? Example,
						<router-link
							:to="{
								path: '/search/results',
								query: {
									state: 'Pennsylvania',
									county: 'Allegheny',
									locality: 'Pittsburgh',
								},
							}"
						>
							Pittsburgh, Allegheny, PA
						</router-link>
						or
						<router-link
							:to="{
								path: '/search/results',
								query: {
									state: 'Pennsylvania',
								},
							}"
						>
							Pennsylvania
						</router-link>
					</label>
				</template>
			</TypeaheadInput>

			<Button
				class="max-h-[calc(var(--typeahead-input-height)+10px)] self-end"
				:disabled="!selectedRecord"
				intent="primary"
				type="submit"
			>
				Search Data
			</Button>
		</div>
	</Form>
</template>

<script setup>
import { Button, Form } from 'pdap-design-system';
import TypeaheadInput from '@/components/TypeaheadInput.vue';
import axios from 'axios';
import { ref } from 'vue';
import { debounce as _debounce } from 'lodash';
import { useRouter } from 'vue-router';

const router = useRouter();

const { isSingleColumn } = defineProps({
	isSingleColumn: Boolean,
});

/* constants */
const TYPEAHEAD_ID = 'pdap-search-typeahead';
const SCHEMA = [
	{
		id: 'all-data-types',
		defaultChecked: true,
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
const formRef = ref();

function submit(values) {
	const params = new URLSearchParams(buildParams(values));
	const path = `/search/results?${params.toString()}`;
	router.push(path);
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

function onChange(values, event) {
	if (event.target.name === 'all-data-types') {
		if (event.target.checked) {
			const update = {};
			Object.entries(values).forEach(([key, val]) => {
				if (key !== 'all-data-types' && val === 'true') {
					update[key] = 'false';
				}
			});
			formRef.value.setValues({ ...values, ...update });
		}
	} else {
		if (values['all-data-types'] === 'true' && event.target.checked) {
			formRef.value.setValues({ ...values, ['all-data-types']: 'false' });
		}
	}
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
					`${import.meta.env.VITE_VUE_API_BASE_URL}/typeahead/locations`,
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
			console.error(err);
		}
	},
	350,
	{ leading: true, trailing: true },
);
</script>
