<route>
	{
		meta: {
			auth: true
		}
	}
</route>

<template>
	<main class="overflow-x-hidden max-w-[1080px] px-6 md:px-10 mx-auto">
		<!-- TODO: this component is massive. Let's break it up into components and move the constants and utils to separate files.
			------ Also: the additional properties section is probably meaty enough that we want an async import.
			------ Maybe even a separate sub-route? At `.data-source/create/additional` ? 
			------ Think about it. -->
		<h1>New data source</h1>

		<FormV2
			id="new-data-source"
			ref="formRef"
			:error="formError"
			class="flex flex-col gap-2"
			name="new-request"
			:schema="SCHEMA"
			@submit="submit"
		>
			<InputText
				:id="'input-' + INPUT_NAMES.url"
				class="md:col-span-2"
				:name="INPUT_NAMES.url"
				placeholder="A link where these records can be found or are referenced."
				@input="checkDuplicates"
			>
				<template #label>
					<h4>Source URL<sup>*</sup></h4>
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

				<template #not-found>
					<span>
						<Button
							class="text-left p-0"
							intent="tertiary"
							type="button"
							@click="
								() => {
									agencyNotAvailable = typeaheadRef.value;
									items = [];
									typeaheadRef.clearInput();
								}
							"
						>
							<strong>No results found.</strong> Would you like to suggest
							{{ typeaheadRef.value }}
							be added to our agencies database?
						</Button>
					</span>
				</template>
			</Typeahead>

			<div v-if="!selectedAgencies.length && agencyNotAvailable">
				<h4>Agency not found</h4>
				<p>
					We will attempt to find this agency and add it to our database as a
					part of this request
				</p>
				<TransitionGroup v-if="agencyNotAvailable" name="list">
					<AgencySelected
						class="md:col-span-2"
						:content="agencyNotAvailable"
						@click="agencyNotAvailable = ''"
					/>
				</TransitionGroup>
			</div>

			<InputText
				:id="'input-' + INPUT_NAMES.name"
				class="md:col-start-1 md:col-end-2"
				:name="INPUT_NAMES.name"
				placeholder="For example, “Arrest records for Portsmouth PD”"
				rows="4"
			>
				<template #label>
					<h4>Source name <sup>*</sup></h4>
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
					<h4>Description <sup>*</sup></h4>
				</template>
			</InputTextArea>

			<InputText
				:id="'input-' + INPUT_NAMES.contact"
				class="md:col-start-1 md:col-end-2"
				:name="INPUT_NAMES.contact"
				placeholder="Please provide an email address so we can give credit or follow up with questions."
			>
				<template #label>
					<h4>Contact info</h4>
				</template>
			</InputText>

			<p class="mt-4"><sup>*</sup> These fields are required</p>

			<transition>
				<div
					v-if="advancedPropertiesExpanded"
					class="max-h-[6000px] overflow-hidden pb-20"
				>
					<div>
						<RadioGroup class="mt-4" :name="INPUT_NAMES.detail">
							<h4>Level of detail available at this source</h4>
							<InputRadio
								v-for="detail of DETAIL_LEVEL"
								:id="detail"
								:key="detail"
								:name="INPUT_NAMES.detail"
								:value="detail"
								:label="detail"
							/>
						</RadioGroup>

						<RadioGroup class="record-type-group" :name="INPUT_NAMES.type">
							<h4 class="col-span-2">Record type</h4>

							<div
								v-for="[categoryTitle, recordTypes] of Object.entries(
									RECORD_TYPES_BY_CATEGORY,
								)"
								:key="categoryTitle"
								v-bind="{
									[RECORD_TYPE_GRID_POSITIONS_BY_CATEGORY[categoryTitle]]: true,
								}"
							>
								<h6 class="text-sm col-span-2">{{ categoryTitle }}</h6>

								<InputRadio
									v-for="detail of recordTypes"
									:id="detail"
									:key="detail"
									:name="INPUT_NAMES.type"
									:value="detail"
									:label="detail"
								/>
							</div>
						</RadioGroup>

						<div class="mt-2">
							<h4>Agency supplied</h4>
							<p class="text-sm max-w-full lg:w-3/4">
								Is the relevant agency also the entity supplying the data? This
								may be "no" if the agency or local government contracted with a
								third party to publish this data, or if a third party was the
								original record-keeper.
							</p>
							<InputCheckbox
								:id="'input-' + INPUT_NAMES.agencySupplied"
								class="md:col-start-1 md:col-end-2"
								:name="INPUT_NAMES.agencySupplied"
								:default-checked="true"
								label="Agency supplied data?"
								@change="(e) => (agencySuppliedChecked = e.target.checked)"
							/>

							<InputTextArea
								v-if="!agencySuppliedChecked"
								:id="'input-' + INPUT_NAMES.supplyingEntity"
								class="md:col-start-1 md:col-end-2"
								:name="INPUT_NAMES.supplyingEntity"
								placeholder="Who made this information available? Please provide a link to their website and contact information."
								rows="4"
							>
								<template #label>
									<h4>Supplying entity</h4>
								</template>
							</InputTextArea>
						</div>

						<div class="mt-2">
							<h4>Agency originated</h4>
							<p class="text-sm max-w-full lg:w-3/4">
								Is the relevant agency also the original record keeper? This is
								usually "yes", unless a third party collected data about a
								police agency.
							</p>
							<InputCheckbox
								:id="'input-' + INPUT_NAMES.agencyOriginated"
								class="md:col-start-1 md:col-end-2"
								:name="INPUT_NAMES.agencyOriginated"
								:default-checked="true"
								label="Agency originated data?"
								@change="(e) => (agencyOriginatedChecked = e.target.checked)"
							/>

							<InputTextArea
								v-if="!agencyOriginatedChecked"
								:id="'input-' + INPUT_NAMES.originatingEntity"
								class="md:col-start-1 md:col-end-2"
								:name="INPUT_NAMES.originatingEntity"
								placeholder="Who originally collected these records? Please provide a link to their website."
								rows="4"
							>
								<template #label>
									<h4>Originating entity</h4>
								</template>
							</InputTextArea>
						</div>

						<div class="mt-2">
							<h4>Access type</h4>
							<p class="text-sm max-w-full">How can the data be acquired?</p>
							<InputCheckbox
								v-for="accessType of ACCESS_TYPE"
								:id="accessType.id"
								:key="accessType.name"
								:name="accessType.name"
								:label="accessType.label"
								class="md:col-start-1 md:col-end-2"
							/>
						</div>

						<div class="mt-2 grid md:grid-cols-2 lg:grid-cols-3">
							<h4 class="md:col-span-2 lg:col-span-3">Formats available</h4>
							<p class="text-sm max-w-full md:col-span-2 lg:col-span-3">
								This applies to the records themselves.
							</p>
							<InputCheckbox
								v-for="format of FORMATS"
								:id="format.id"
								:key="format.name"
								:name="format.name"
								:label="format.label"
								class="w-[max-content]"
							/>
						</div>

						<RadioGroup class="mt-4" :name="INPUT_NAMES.method">
							<h4>Update method</h4>
							<p class="text-sm">
								How are new records added to this data source?
							</p>
							<InputRadio
								v-for="method of UPDATE_METHOD"
								:id="method"
								:key="method"
								:name="INPUT_NAMES.method"
								:value="method"
								:label="method"
							/>
						</RadioGroup>

						<InputDatePicker
							:id="INPUT_NAMES.start"
							:name="INPUT_NAMES.start"
							position="left"
						>
							<template #label>
								<h4>Coverage start</h4>
							</template>
						</InputDatePicker>
						<InputDatePicker
							:id="INPUT_NAMES.end"
							:name="INPUT_NAMES.end"
							position="left"
						>
							<template #label>
								<h4>Coverage end</h4>
							</template>
						</InputDatePicker>

						<RadioGroup
							class="mt-2 grid md:grid-cols-2 lg:grid-cols-3"
							:name="INPUT_NAMES.schedule"
						>
							<h4 class="md:col-span-2 lg:col-span-3">Retention schedule</h4>
							<p class="text-sm max-w-full md:col-span-2 lg:col-span-3">
								How long are records kept? There may be guidelines regarding how
								long important information must remain accessible for future
								use.
							</p>
							<InputRadio
								v-for="schedule of RETENTION_SCHEDULE"
								:id="schedule"
								:key="schedule"
								:name="INPUT_NAMES.schedule"
								:value="schedule"
								:label="schedule"
							/>
						</RadioGroup>

						<InputSelect
							:id="INPUT_NAMES.portalType"
							:name="INPUT_NAMES.portalType"
							:options="DATA_PORTAL_TYPE"
							combobox
							placeholder="Select the data portal type."
							@change="
								({ value }) => {
									isOtherPortalTypeSelected = value === 'Other';
								}
							"
						>
							<template #label>
								<h4>Data portal type</h4>
								<p class="text-sm max-w-full lg:w-3/4">
									Some data is published via a standard third-party portal,
									typically named somewhere on the page. Select "Other" if the
									site uses a data portal we don't have listed.
								</p>
							</template>
						</InputSelect>
						<InputText
							v-if="isOtherPortalTypeSelected"
							:id="'input-' + INPUT_NAMES.portalTypeOther"
							class="md:col-start-1 md:col-end-2"
							:name="INPUT_NAMES.portalTypeOther"
							placeholder="Provide a name for the Data Portal, since 'Other' was selected."
						>
							<template #label>
								<h4>Data portal type—other</h4>
							</template>
						</InputText>

						<InputTextArea
							:id="'input-' + INPUT_NAMES.accessNotes"
							class="md:col-start-1 md:col-end-2"
							:name="INPUT_NAMES.accessNotes"
							placeholder="Anything else we should know about how to get this data?"
							rows="4"
						>
							<template #label>
								<h4>Access notes</h4>
							</template>
						</InputTextArea>

						<InputTextArea
							:id="'input-' + INPUT_NAMES.notes"
							class="md:col-start-1 md:col-end-2"
							:name="INPUT_NAMES.notes"
							placeholder="Did you encounter an issue using this form? Were you unable to select an option you needed or give us information we did not ask for? Is there something special about this Data Source?"
							rows="4"
						>
							<template #label> <h4>Submission notes</h4> </template>
						</InputTextArea>
					</div>
				</div>
			</transition>

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
				<Button
					:disabled="requestPending"
					intent="secondary"
					type="button"
					@click="advancedPropertiesExpanded = !advancedPropertiesExpanded"
				>
					{{ advancedPropertiesExpanded ? 'Hide' : 'Show' }} advanced properties
				</Button>
			</div>
		</FormV2>
	</main>
</template>

<script setup>
import {
	Button,
	FormV2,
	InputCheckbox,
	InputDatePicker,
	InputRadio,
	InputSelect,
	InputText,
	InputTextArea,
	RadioGroup,
} from 'pdap-design-system';
import Typeahead from '@/components/TypeaheadInput.vue';
import AgencySelected from '@/components/TypeaheadSelected.vue';
import { toast } from 'vue3-toastify';
import { formatText } from './_util';
import pluralize from '@/util/pluralize';
import unpluralize from '@/util/unpluralize';
import _debounce from 'lodash/debounce';
import _cloneDeep from 'lodash/cloneDeep';
import _isEqual from 'lodash/isEqual';
import _startCase from 'lodash/startCase';
import { nextTick, ref } from 'vue';
import axios from 'axios';
import { useDataSourceStore } from '@/stores/data-source';
import { useSearchStore } from '@/stores/search';

const { createDataSource } = useDataSourceStore();
const { findDuplicateURL } = useSearchStore();

const INPUT_NAMES = {
	// Base properties
	url: 'source_url',
	readMeUrl: 'readme_url',
	agencies: 'agencies',
	name: 'submitted_name',
	description: 'description',
	contact: 'submitter_contact_info',

	// Advanced properties
	detail: 'detail_level',
	type: 'record_type_name',
	agencySupplied: 'agency_supplied',
	agencyOriginated: 'agency_originated',
	supplyingEntity: 'supplying_entity',
	originatingEntity: 'originating_entity',
	accessType: 'access_types',
	format: 'record_formats',
	frequency: 'update_frequency',
	method: 'update_method',
	start: 'coverage_start',
	end: 'coverage_end',
	schedule: 'retention_schedule',
	portalType: 'data_portal_type',
	portalTypeOther: 'data_portal_type_other',
	accessNotes: 'access_notes',
	notes: 'submission_notes',
};
const RECORD_TYPES_BY_CATEGORY = {
	'Police & Public Interactions': [
		'Accident Reports',
		'Arrest Records',
		'Calls for Service',
		'Car GPS',
		'Citations',
		'Dispatch Logs',
		'Dispatch Recordings',
		'Field Contacts',
		'Incident Reports',
		'Misc Police Activity',
		'Officer Involved Shootings',
		'Stops',
		'Surveys',
		'Use of Force Reports',
		'Vehicle Pursuits',
	],
	'Info about officers': [
		'Complaints & Misconduct',
		'Daily Activity Logs',
		'Training & Hiring Info',
		'Personnel Records',
	],
	'Info about agencies': [
		'Annual & Monthly Reports',
		'Budgets & Finances',
		'Contact Info & Agency Meta',
		'Geographic',
		'List of Data Sources',
		'Policies & Contracts',
	],
	'Agency-published Resources': [
		'Crime Maps & Reports',
		'Crime Statistics',
		'Media Bulletins',
		'Records Request Info',
		'Resources',
		'Sex Offender Registry',
		'Wanted Persons',
	],
	'Jails & courts': ['Booking Reports', 'Court Cases', 'Incarceration Records'],
};
const RECORD_TYPE_GRID_POSITIONS_BY_CATEGORY = {
	'Police & Public Interactions': 'tallest',
	'Info about officers': 'short',
	'Info about agencies': 'tall',
	'Agency-published Resources': 'taller',
	'Jails & courts': 'short',
};

const DETAIL_LEVEL = [
	'Individual record',
	'Aggregated records',
	'Summarized totals',
];
const ACCESS_TYPE = ['web-page', 'download', 'api'].map(formatAccessType);
function formatAccessType(accessType) {
	return {
		id: 'input-' + accessType,
		name: INPUT_NAMES.accessType + '-' + accessType,
		label: formatAccessTypeLabel(accessType),
	};
}
function formatAccessTypeLabel(accessType) {
	return accessType
		.replaceAll(/-/g, ' ')
		.split(' ')
		.map((s) => {
			if (s === 'api') return s.toUpperCase();
			if (s === 'page') return s;
			return _startCase(s.toLocaleLowerCase());
		})
		.join(' ');
}
const UPPERCASE_FORMATS = new Set([
	'csv',
	'doc',
	'gis',
	'html',
	'json',
	'pdf',
	'pdf:',
	'rdf',
	'rss',
	'txt',
	'xls',
	'xml',
]);
const LOWERCASE_FORMATS = new Set(['table', 'text']);

const FORMATS = [
	'audio',
	'csv',
	'dashboard_visualization',
	'doc_txt',
	'gis_shapefile',
	'google-sheets',
	'html-table',
	'html-text',
	'json',
	'other',
	'pdf',
	'pdf:-machine-created',
	'pdf:-scanned',
	'physical',
	'rdf',
	'rss',
	'video_image',
	'xls',
	'xml',
].map(formatFormats);
function formatFormats(format) {
	return {
		id: INPUT_NAMES.format + '-' + format,
		name: INPUT_NAMES.format + '-' + format,
		label: formatFormatsLabel(format),
	};
}
function formatFormatsLabel(format) {
	return format
		.replaceAll(/-/g, ' ')
		.replaceAll(/_/g, ' / ')
		.replaceAll(/__/g, ': ')
		.split(' ')
		.map((s) => {
			if (UPPERCASE_FORMATS.has(s)) return s.toUpperCase();
			if (LOWERCASE_FORMATS.has(s)) return s;
			return _startCase(s.toLocaleLowerCase());
		})
		.join(' ');
}

const UPDATE_METHOD = ['Overwrite', 'Insert', 'No updates'];
const RETENTION_SCHEDULE = [
	'Future only',
	'< 1 day',
	'1 day',
	'< 1 week',
	'1 week',
	'< 1 month',
	'1 month',
	'< 1 year',
	'1 year',
	'1-10 years',
	'> 10 years',
];
const DATA_PORTAL_TYPE = [
	'ArcGIS',
	'Benchmark / Pioneer Technology Group',
	'Broadcastify',
	'Carto',
	'City',
	'CityProtect',
	'CKAN',
	'County',
	'CourtView Justice Solutions / equivant',
	'CrimeGraphics',
	'CrimeMapping',
	'CTrack',
	'DataWorks',
	'Department',
	'DKAN',
	'DocumentCloud',
	'DomainWeb',
	'Doxpop',
	'eCourt Kokua',
	'eMagnus Multicourt',
	'ESRI',
	'Granicus',
	'Judici',
	'KellPro',
	'LexisNexis',
	'Microsoft Power BI',
	'MuckRock',
	'Open Data Soft',
	'Open Knowledge Foundation',
	'Opendata',
	'Other',
	'pandA',
	'PROWARE',
	'ShowCase / equivant',
	'Socrata',
	'SpotCrime',
	'Tableau',
	'Tyler Technologies',
	'Xerox Government Systems',
	'PowerDMS',
	'SWIFTREPOSITORY',
].map((portalType) => {
	return {
		label: portalType,
		value: portalType.toLowerCase().replaceAll(' ', '_'),
	};
});
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

const advancedPropertiesExpanded = ref(false);
const agencySuppliedChecked = ref(true);
const agencyOriginatedChecked = ref(true);
const isOtherPortalTypeSelected = ref(false);
const selectedAgencies = ref([]);
const agencyNotAvailable = ref('');
const alreadyExistsToastId = ref();
const items = ref([]);
const formRef = ref();
const typeaheadRef = ref();
const typeaheadError = ref();
const formError = ref();
const requestPending = ref(false);

function formatDate(date) {
	const offset = date.getTimezoneOffset();
	date = new Date(date.getTime() - offset * 60 * 1000);
	return date.toISOString().split('T')[0];
}

function formatData(values) {
	if (values[INPUT_NAMES.start]) {
		values[INPUT_NAMES.start] = formatDate(new Date(values[INPUT_NAMES.start]));
	}
	if (values[INPUT_NAMES.end]) {
		values[INPUT_NAMES.end] = formatDate(new Date(values[INPUT_NAMES.end]));
	}

	if (agencyNotAvailable.value) {
		values.agency_described_not_in_database = agencyNotAvailable.value;
	}

	Object.assign(values, {
		[INPUT_NAMES.format]: [],
	});
	Object.assign(values, {
		[INPUT_NAMES.accessType]: [],
	});
	Object.entries(values).forEach(([key, value]) => {
		const isAccess =
			key.includes(INPUT_NAMES.accessType) &&
			key.length > INPUT_NAMES.accessType.length &&
			value;
		const isFormat =
			key.includes(INPUT_NAMES.format) &&
			key.length > INPUT_NAMES.format.length &&
			value;

		if (isAccess) {
			values[INPUT_NAMES.accessType].push(
				formatAccessTypeLabel(key.replace(`${INPUT_NAMES.accessType}-`, ''))
					.split(' ')
					.join(''),
			);
		} else if (isFormat) {
			values[INPUT_NAMES.format].push(
				formatFormatsLabel(key.replace(`${INPUT_NAMES.format}-`, '')),
			);
		}
		if (isAccess || isFormat) delete values[key];
	});
	return values;
}

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

const checkDuplicates = _debounce(
	async (e) => {
		try {
			const dupes = await findDuplicateURL(e.target.value);
			if (dupes.data.duplicates.length && !alreadyExistsToastId.value) {
				alreadyExistsToastId.value = toast.info(
					`${dupes.data.duplicates.length} ${pluralize('data source', dupes.data.duplicates.length)} already ${unpluralize('exists', dupes.data.duplicates.length)} with the url ${e.target.value}.\n${dupes.data.duplicates.length === 1 ? 'Its status is' : 'Their statuses are'} ${dupes.data.duplicates.map(({ approval_status }) => approval_status).join(', ')}`,
					{ autoClose: false },
				);
			}
		} catch (err) {
			return;
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
		entry_data: formatData(values),
		linked_agency_ids: agencies?.map(({ id }) => id),
	};

	formRef.value.setValues({ ...values });

	try {
		if (formError.value) {
			formError.value = '';
		}
		await createDataSource(requestBody);

		window.scrollTo(0, 0);
		advancedPropertiesExpanded.value = false;
		const message = `${values[INPUT_NAMES.name]} has been submitted successfully!\nIt will be available in our data sources database after approval.`;
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

<style>
@tailwind utilities;
</style>

<style scoped>
h4 {
	margin: unset;
}

.record-type-group {
	@apply mt-2;
}

@media (width > 1024px) {
	.record-type-group {
		display: grid;
		grid-auto-rows: auto repeat(4, 175px);
		grid-gap: 10px;
		grid-template-columns: repeat(2, minmax(30%, 1fr));
	}

	[short] {
		grid-row: span 1;
	}

	[tall] {
		grid-row: span 2;
	}

	[taller] {
		grid-row: span 3;
	}

	[tallest] {
		grid-row: span 4;
	}
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

<style scoped>
.v-enter-active,
.v-leave-active {
	transition:
		opacity 0.5s ease,
		max-height 0.5s ease-in;
}

.v-enter-from,
.v-leave-to {
	opacity: 0;
	max-height: 0;
}
</style>
