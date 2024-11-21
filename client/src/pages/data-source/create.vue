<route>
	{
		meta: {
			auth: true
		}
	}
</route>

<template>
	<main class="overflow-x-hidden max-w-[1080px] px-6 md:px-10 mx-auto">
		<h1>New data source</h1>

		<FormV2
			id="new-data-source"
			ref="formRef"
			:error="formError"
			class="flex flex-col gap-2"
			name="new-request"
			:schema="SCHEMA"
			@error="error"
			@submit="submit"
		>
			<InputText
				:id="'input-' + INPUT_NAMES.url"
				class="md:col-span-2"
				:name="INPUT_NAMES.url"
				placeholder="A link where these records can be found or are referenced."
			>
				<template #label>
					<h4>Source URL</h4>
				</template>
			</InputText>

			<InputText
				:id="'input-' + INPUT_NAMES.readMeUrl"
				class="md:col-span-2"
				:name="INPUT_NAMES.readMeUrl"
				placeholder="A link to any contextual info, like a data dictionary or explanation of the data."
			>
				<template #label>
					<h4>README URL</h4>
				</template>
			</InputText>

			<label :for="INPUT_NAMES.agencies" class="py-1 md:col-span-2">
				<h4>What agency is covered by this source?</h4>
			</label>

			<TransitionGroup v-if="selectedAgencies" name="list">
				<AgencySelected
					v-for="agency in selectedAgencies"
					:key="JSON.stringify(agency)"
					class="md:col-span-2"
					:content="formatText(agency)"
					:on-click="
						() => {
							const indexToRemove = selectedAgencies.indexOf(agency);
							if (indexToRemove > -1) selectedAgencies.splice(indexToRemove, 1);
						}
					"
				/>
			</TransitionGroup>

			<Typeahead
				:id="INPUT_NAMES.agencies"
				ref="typeaheadRef"
				class="md:col-span-2"
				:error="typeaheadError"
				:format-item-for-display="formatText"
				:items="items"
				:placeholder="
					selectedAgencies.length ? 'Enter another agency' : 'Enter an agency'
				"
				@select-item="
					(item) => {
						if (item) {
							selectedAgencies = [...selectedAgencies, item];
							items = [];
							typeaheadRef.clearInput();
							typeaheadRef.focusInput();
						}
					}
				"
				@on-input="fetchTypeaheadResults"
			>
				<!-- Item to render passed as scoped slot -->
				<template #item="item">
					<!-- eslint-disable-next-line vue/no-v-html This data is coming from our API, so we can trust it-->
					<span v-html="typeaheadRef?.boldMatchText(formatText(item))" />
					<span class="select">Select</span>
				</template>
			</Typeahead>

			<InputText
				:id="'input-' + INPUT_NAMES.name"
				class="md:col-start-1 md:col-end-2"
				:name="INPUT_NAMES.name"
				placeholder="For example, “Arrest records for Portsmouth PD”"
				rows="4"
			>
				<template #label>
					<h4>Source name</h4>
				</template>
			</InputText>

			<InputTextArea
				:id="'input-' + INPUT_NAMES.description"
				class="md:col-start-2 md:col-end-3"
				:name="INPUT_NAMES.description"
				placeholder="If the source is difficult to understand or categorize, please share more information about how it was processed or can be used."
				rows="4"
			>
				<template #label>
					<h4>Description</h4>
				</template>
			</InputTextArea>

			<InputText
				:id="'input-' + INPUT_NAMES.contact"
				class="md:col-start-1 md:col-end-2"
				:name="INPUT_NAMES.contact"
				placeholder="Please provide an email address so we can give credit or follow up with questions."
				rows="4"
			>
				<template #label>
					<h4>Contact info</h4>
				</template>
			</InputText>

			<div
				class="flex gap-2 flex-col max-w-full md:flex-row md:col-start-1 md:col-end-2 mt-8"
			>
				<Button
					:disabled="requestPending"
					:is-loading="requestPending"
					class="min-w-52"
					intent="primary"
					type="submit"
				>
					Submit data source
				</Button>
				<Button
					:disabled="requestPending"
					intent="secondary"
					type="button"
					@click="clear"
				>
					Clear
				</Button>
			</div>
		</FormV2>
	</main>
</template>

<script setup>
import { Button, FormV2, InputText, InputTextArea } from 'pdap-design-system';
import Typeahead from '@/components/TypeaheadInput.vue';
import AgencySelected from '@/components/TypeaheadSelected.vue';
import { toast } from 'vue3-toastify';
import { formatText } from './_util';
import _debounce from 'lodash/debounce';
import _cloneDeep from 'lodash/cloneDeep';
import _isEqual from 'lodash/isEqual';
import { nextTick, ref } from 'vue';
import axios from 'axios';
import { useDataSourceStore } from '@/stores/data-source';

const { createDataSource } = useDataSourceStore();

const INPUT_NAMES = {
	// contact: 'contact',
	url: 'source_url',
	readMeUrl: 'readme_url',
	agencies: 'agencies',
	name: 'submitted_name',
	description: 'description',
	contact: 'submitter_contact_info',
};
const SCHEMA = [
	{
		name: INPUT_NAMES.url,
		validators: {
			required: {
				value: true,
				message:
					'Please submit a url where data is accessible for this source.',
			},
			url: {
				value: true,
				message:
					'Please submit a valid url, including the scheme (http/https).',
			},
		},
	},
	{
		name: INPUT_NAMES.readMeUrl,
		validators: {
			url: {
				value: true,
				message:
					'Please submit a valid url, including the scheme (http/https).',
			},
		},
	},
	{
		name: INPUT_NAMES.name,
		validators: {
			required: {
				value: true,
				message: 'Please let us know what to call this request.',
			},
		},
	},
	{
		name: INPUT_NAMES.description,
		validators: {
			required: {
				value: true,
				message: 'Please describe this request.',
			},
		},
	},
	{
		name: INPUT_NAMES.contact,
		validators: {
			email: {
				value: true,
				message: 'Please provide a valid email address.',
			},
		},
	},
];

const selectedAgencies = ref([]);
const items = ref([]);
const formRef = ref();
const typeaheadRef = ref();
const typeaheadError = ref();
const formError = ref();
const requestPending = ref(false);

// TODO: This functionality is duplicated everywhere we're using typeahead.
const fetchTypeaheadResults = _debounce(
	async (e) => {
		try {
			if (e.target.value.length > 1) {
				const response = await axios.get(
					`${import.meta.env.VITE_VUE_API_BASE_URL}/typeahead/agencies`,
					{
						headers: {
							Authorization: import.meta.env.VITE_ADMIN_API_KEY,
						},
						params: {
							query: e.target.value,
						},
					},
				);
				const suggestions = response?.data?.suggestions;
				const filteredBySelected = suggestions.filter((sugg) => {
					return !selectedAgencies.value.find((agency) =>
						_isEqual(sugg, agency),
					);
				});

				items.value = filteredBySelected.length
					? filteredBySelected
					: undefined;
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

async function clear() {
	const newVal = Object.values(INPUT_NAMES)
		// Exclude typeahead
		.filter((n) => n !== INPUT_NAMES.agencies)
		.reduce(
			(acc, cur) => ({
				...acc,
				[cur]: '',
			}),
			{},
		);

	formRef.value.setValues(newVal);
	await nextTick();
	items.value = [];
	selectedAgencies.value = [];
}

async function submit(values) {
	requestPending.value = true;

	// Create new array. In case of error, we need the original array to remain unmodified
	const agencies = _cloneDeep(selectedAgencies.value);

	const requestBody = {
		entry_data: values,
		linked_agency_ids: agencies?.map(({ id }) => id),
	};

	try {
		await createDataSource(requestBody);

		const message = `${values[INPUT_NAMES.name]} has been submitted successfully!\nIt will be available in our data sources database after approval.`;
		window.scrollTo(0, 0);
		toast.success(message, { autoClose: false });
	} catch (error) {
		if (error) {
			console.error(error);
			formError.value = 'Something went wrong, please try again.';
			formRef.value.setValues({ ...values });
			var isError = !!error;
		}
	} finally {
		if (!isError) {
			selectedAgencies.value = [];
		}
		requestPending.value = false;
	}
}
</script>

<style scoped>
h4 {
	margin: unset;
}

.select {
	@apply ml-auto;
}

.agency-type {
	@apply border-solid border-2 border-neutral-700 dark:border-neutral-400 rounded-full text-neutral-700 dark:text-neutral-400 text-xs @md:text-sm px-2 py-1;
}

.list-move,
.list-enter-active,
.list-leave-active {
	transition:
		opacity 500ms ease,
		transform 500ms ease;
}

.list-enter-from {
	opacity: 0;
	transform: translateX(-50%);
}

.list-leave-to {
	opacity: 0;
	transform: translateX(50%);
}
</style>
