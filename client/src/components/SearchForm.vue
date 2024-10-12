<template>
	<div
		class="col-span-1 flex flex-col gap-6 mt-8 @md:col-span-2 @lg:col-span-3 @md:flex-row @md:gap-0"
	>
		<TypeaheadInput
			:id="TYPEAHEAD_ID"
			:items="items"
			:placeholder="placeholder ?? 'Enter a place'"
			@select-item="onSelectRecord"
			@on-input="fetchTypeaheadResults"
		>
			<!-- Pass label as slot to typeahead -->
			<template #label>
				<label class="col-span-2" :for="TYPEAHEAD_ID">
					<h4 class="uppercase">Search location</h4>
				</label>
			</template>
		</TypeaheadInput>
	</div>

	<h4 class="w-full mt-8">Types of data</h4>
	<FormV2
		id="pdap-data-sources-search"
		ref="formRef"
		class="grid grid-cols-1 auto-rows-auto max-w-full gap:0 @md:gap-4 @md:grid-cols-2 @lg:grid-cols-3 gap-0"
		@change="onChange"
		@submit="submit"
	>
		<InputCheckbox
			v-for="{ id, defaultChecked, name, label } in CHECKBOXES"
			:id="id"
			:key="name"
			:default-checked="defaultChecked"
			:name="name"
		>
			<template #label>
				{{ label }} <RecordTypeIcon :record-type="label" />
			</template>
		</InputCheckbox>

		<Button :disabled="!selectedRecord" intent="primary" type="submit">
			{{ buttonCopy ?? 'Search' }}
		</Button>
	</FormV2>
</template>

<script setup>
import {
	Button,
	FormV2,
	InputCheckbox,
	RecordTypeIcon,
} from 'pdap-design-system';
import TypeaheadInput from '@/components/TypeaheadInput.vue';
import axios from 'axios';
import { ref } from 'vue';
import { debounce as _debounce } from 'lodash';
import { useRouter } from 'vue-router';

const router = useRouter();

const { buttonCopy } = defineProps({
	buttonCopy: String,
	placeholder: String,
});

const emit = defineEmits(['searched']);

/* constants */
const TYPEAHEAD_ID = 'pdap-search-typeahead';
const CHECKBOXES = [
	{
		id: 'all-data-types',
		defaultChecked: true,
		name: 'all-data-types',
		label: 'All data types',
	},
	{
		id: 'interactions',
		defaultChecked: false,
		name: 'police-and-public-interactions',
		label: 'Police & public interactions',
	},
	{
		id: 'info-officers',
		defaultChecked: false,
		name: 'info-about-officers',
		label: 'Info about officers',
	},
	{
		id: 'info-agencies',
		defaultChecked: false,
		name: 'info-about-agencies',
		label: 'Info about agencies',
	},
	{
		id: 'agency-published-resources',
		defaultChecked: false,
		name: 'agency-published-resources',
		label: 'Agency-published resources',
	},
	{
		id: 'jails-and-courts',
		defaultChecked: false,
		name: 'jails-and-courts',
		label: 'Jails and courts specific',
	},
];

const items = ref([]);
const selectedRecord = ref();
const formRef = ref();

function submit(values) {
	const params = new URLSearchParams(buildParams(values));
	const path = `/search/results?${params.toString()}`;
	router.push(path);
	emit('searched');
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
		values['all-data-types'] ||
		Object.values(values).every((val) => !val || !val)
	) {
		return obj;
	}
	// Otherwise set record_types array
	const inputIdsToRecordTypes = new Map(
		CHECKBOXES.map(({ name, label }) => [name, label]),
	);
	obj.record_categories = Object.entries(values)
		.map(([key, val]) => val && inputIdsToRecordTypes.get(key))
		.filter(Boolean);

	return obj;
}

function onChange(values, event) {
	if (event.target.name === 'all-data-types') {
		if (event.target.checked) {
			const update = {};
			Object.entries(values).forEach(([key, val]) => {
				if (key !== 'all-data-types' && val) {
					update[key] = false;
					const checkbox = document.querySelector(`input[name=${key}]`);
					checkbox.checked = false;
				}
			});
			formRef.value.setValues({ ...values, ...update });
		}
	} else {
		const allTypesCheckbox = document.querySelector(
			'input[name="all-data-types"]',
		);
		if (allTypesCheckbox.checked && event.target.checked) {
			formRef.value.setValues({ ...values, ['all-data-types']: false });
			allTypesCheckbox.checked = false;
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
