<template>
	<main class="overflow-x-hidden max-w-[1080px] px-6 md:px-10 mx-auto">
		<h1>New request</h1>

		<FormV2
			id="new-request"
			ref="formRef"
			:error="formError"
			class="grid md:grid-cols-2 gap-x-4 [&>.pdap-form-error-message]:md:col-span-2"
			name="new-request"
			:schema="SCHEMA"
			@error="error"
			@submit="submit"
		>
			<InputText
				:id="'input-' + INPUT_NAMES.title"
				class="md:col-span-2"
				:name="INPUT_NAMES.title"
				placeholder="Briefly describe the general purpose or topic."
			>
				<template #label>
					<h4>Request title</h4>
				</template>
			</InputText>

			<label :for="INPUT_NAMES.area" class="py-1 md:col-span-2 mb-1">
				<h4>What area is covered by your request?</h4>
			</label>

			<TransitionGroup v-if="selectedLocations" name="list">
				<LocationSelected
					v-for="location in selectedLocations"
					:key="JSON.stringify(location)"
					class="md:col-span-2"
					:content="formatText(location)"
					:on-click="
						() => {
							const indexToRemove = selectedLocations.indexOf(location);
							if (indexToRemove > -1)
								selectedLocations.splice(indexToRemove, 1);
						}
					"
				/>
			</TransitionGroup>

			<Typeahead
				:id="INPUT_NAMES.area"
				ref="typeaheadRef"
				class="md:col-span-2 mb-2"
				:error="typeaheadError"
				:format-item-for-display="formatText"
				:items="items"
				:placeholder="
					selectedLocations.length ? 'Enter another place' : 'Enter a place'
				"
				@select-item="
					(item) => {
						if (item) {
							selectedLocations = [...selectedLocations, item];
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
					<span class="locale-type">
						{{ item.type }}
					</span>
					<span class="select">Select</span>
				</template>
			</Typeahead>

			<InputText
				:id="'input-' + INPUT_NAMES.range"
				class="md:col-span-2"
				:name="INPUT_NAMES.range"
				placeholder="What dates or years should the data cover?"
			>
				<template #label>
					<h4>Coverage range</h4>
				</template>
			</InputText>

			<InputSelect
				:id="'input-' + INPUT_NAMES.target"
				class="md:col-span-2"
				:name="INPUT_NAMES.target"
				:options="SELECT_OPTS"
				placeholder="When would you like to see this request filled?"
			>
				<template #label>
					<h4>Target date</h4>
				</template>
			</InputSelect>

			<InputTextArea
				:id="'input-' + INPUT_NAMES.notes"
				class="md:col-start-1 md:col-end-2"
				:name="INPUT_NAMES.notes"
				placeholder="What are you trying to learn? Is there anything you've already tried?"
				rows="4"
			>
				<template #label>
					<h4>Request notes</h4>
				</template>
			</InputTextArea>

			<InputTextArea
				:id="'input-' + INPUT_NAMES.requirements"
				class="md:col-start-2 md:col-end-3"
				:name="INPUT_NAMES.requirements"
				placeholder="Details the data must have, like 'case numbers' or 'incident location'."
				rows="4"
			>
				<template #label>
					<h4>Data requirements</h4>
				</template>
			</InputTextArea>

			<div
				class="flex gap-2 flex-col max-w-full md:flex-row md:col-start-1 md:col-end-2 mt-8"
			>
				<Button
					:disabled="requestPending"
					class="min-w-52"
					intent="primary"
					type="submit"
				>
					<Spinner :show="requestPending" />
					<template v-if="!requestPending" #default> Submit request </template>
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
import {
	Button,
	FormV2,
	InputText,
	InputSelect,
	InputTextArea,
	Spinner,
} from 'pdap-design-system';
import Typeahead from '../components/TypeaheadInput.vue';
import LocationSelected from '../components/TypeaheadLocationSelected.vue';
import { useRequestStore } from '@/stores/request';
import formatText from '@/util/formatLocationForDisplay';
import _debounce from 'lodash/debounce';
import _cloneDeep from 'lodash/cloneDeep';
import { nextTick, ref, watch } from 'vue';
import axios from 'axios';

const { createRequest } = useRequestStore();

const INPUT_NAMES = {
	// contact: 'contact',
	title: 'title',
	area: 'area',
	range: 'coverage_range',
	target: 'request_urgency',
	notes: 'submission_notes',
	requirements: 'data_requirements',
};
const SELECT_OPTS = [
	{ value: 'urgent', label: 'Urgent (Less than a week)' },
	{
		value: 'somewhat_urgent',
		label: 'Somewhat urgent (Less than a month)',
	},
	{
		value: 'not_urgent',
		label: 'Not urgent (A few months)',
	},
	{
		value: 'long_term',
		label: 'Long term (6 months or more)',
	},
	{ value: 'indefinite_unknown', label: 'Indefinite/Unknown' },
];
const SCHEMA = [
	// {
	// 	name: INPUT_NAMES.contact,
	// 	validators: {
	// 		required: {
	// 			value: true,
	// 			message: 'Please let us know how to get in touch about this request.',
	// 		},
	// 	},
	// },
	{
		name: INPUT_NAMES.title,
		validators: {
			required: {
				value: true,
				message: 'Please let us know what to call this request.',
			},
		},
	},
	{
		name: INPUT_NAMES.range,
		validators: {
			required: {
				value: true,
				message: 'Please let us know a range of years to look for this data.',
			},
		},
	},
	{
		name: INPUT_NAMES.target,
		validators: {
			required: {
				value: true,
				message:
					"Please let us know when you'd like this request to be filled.",
			},
		},
	},
	{
		name: INPUT_NAMES.notes,
		validators: {
			required: {
				value: true,
				message: 'Please let us know a little more about your request.',
			},
		},
	},
	{
		name: INPUT_NAMES.requirements,
		validators: {
			required: {
				value: true,
				message: 'Please let us know the requirements for this request.',
			},
		},
	},
];

const selectedLocations = ref([]);
const items = ref([]);
const formRef = ref();
const typeaheadRef = ref();
const typeaheadError = ref();
const formError = ref();
const requestPending = ref(false);

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

async function clear() {
	const newVal = Object.values(INPUT_NAMES)
		// Exclude typeahead
		.filter((n) => n !== INPUT_NAMES.area)
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
	selectedLocations.value = [];
}

function error(v$) {
	// Janky error handling for typeahead because it's not a controlled input - on form error, check for this error, too
	if (v$.value.$anyDirty && !selectedLocations.value.length) {
		typeaheadError.value = 'Please include a location with your request';
	}
}

async function submit(values) {
	if (!selectedLocations.value.length) {
		// Janky error handling for typeahead because it's not a controlled input - if form doesn't error, check for this error anyway.
		typeaheadError.value = 'Please include a location with your request';
		return;
	}
	requestPending.value = true;

	// Remove contact for now, as it's not present on the API endpoint yet TODO: remove this when API is updated
	delete values[INPUT_NAMES.contact];

	// Create new array. In case of error, we need the original array to remain unmodified
	const locations = _cloneDeep(selectedLocations.value);

	const requestBody = {
		request_info: values,
		location_infos: [
			...locations.map((loc) => {
				delete loc.display_name;
				return loc;
			}),
		],
	};

	try {
		await createRequest(requestBody);
	} catch (error) {
		if (error) {
			formError.value = 'Something went wrong, please try again.';
			formRef.value.setValues({ ...values });
			var isError = !!error;
		}
	} finally {
		if (!isError) {
			selectedLocations.value = [];
		}
		requestPending.value = false;
	}
}

watch(
	// More janky typeahead error handling
	() => selectedLocations.value,
	(selected) => {
		// clearing when error exists and value selected
		if (selected.length && typeaheadError.value) {
			typeaheadError.value = undefined;
		}

		// clearing and re-applying when dirty
		if (!selected.length && formRef.value.v$.$anyDirty) {
			typeaheadError.value = 'Please include a location with your request';
		}
	},
);
</script>

<style scoped>
h4 {
	margin: unset;
}

.select {
	@apply ml-auto;
}

.locale-type {
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

<route>
	{
		meta: {
			auth: true
		}
	}
</route>
