import SearchResultPage from '../pages/SearchResultPage.vue';
import { flushPromises, shallowMount } from '@vue/test-utils';
import { describe, expect, vi, test } from 'vitest';
import axios from 'axios';

vi.mock('axios');

const $routeMock = {
	params: {
		searchTerm: 'calls',
		county: 'Cook',
	},
};

describe('SearchResultPage successfully renders components', () => {
	axios.get.mockResolvedValue({
		data: {
			count: 3,
			data: [
				{
					agency_name: 'Cicero Police Department - IN',
					agency_supplied: false,
					airtable_uid: 'rec7edsmcuVQwMMXG',
					coverage_end: null,
					coverage_start: '2017-01-01',
					data_source_name:
						'Calls for Service for Cicero Police Department - IN',
					description: null,
					municipality: 'Bridgeview',
					name: 'Cicero Police Department - IN',
					record_format: '[]',
					record_type: 'Calls for Service',
					source_url:
						'https://cityprotect.com/agency/cc0d9a3d-50b2-4424-ae25-5699ba6eaff9',
					state_iso: 'IN',
				},
				{
					agency_name: 'Chicago Police Department - IL',
					agency_supplied: true,
					airtable_uid: 'recv9fMNEQTbVarj2',
					coverage_end: null,
					coverage_start: '2019-01-01',
					data_source_name:
						'Calls for Service for Chicago Police Department - IL',
					description: null,
					municipality: 'Chicago',
					name: 'Chicago Police Department - IL',
					record_format: '[]',
					record_type: 'Calls for Service',
					source_url:
						'https://informationportal.igchicago.org/911-calls-for-cpd-service/',
					state_iso: 'IL',
				},
				{
					agency_name: 'Chicago Police Department - IL',
					agency_supplied: false,
					airtable_uid: 'recv9fMNEQTbVarj2',
					coverage_end: null,
					coverage_start: '2018-12-18',
					data_source_name: '311 Calls for City of Chicago',
					description:
						'311 Service Requests received by the City of Chicago. This dataset includes requests created after the launch of the new 311 system on 12/18/2018 and some records from the previous system, indicated in the LEGACY\\_RECORD column.\n\nIncluded as a Data Source because in some cities 311 calls lead to police response; that does not appear to be the case in Chicago.\n',
					municipality: 'Chicago',
					name: 'Chicago Police Department - IL',
					record_format: "['CSV', 'XML', 'RDF', 'RSS']",
					record_type: 'Calls for Service',
					source_url:
						'https://data.cityofchicago.org/Service-Requests/311-Service-Requests/v6vf-nfxy',
					state_iso: 'IL',
				},
			],
		},
	});

	const wrapper = shallowMount(SearchResultPage, {
		global: {
			mocks: {
				$route: $routeMock,
			},
		},
	});

	test('renders search results after API call', () => {
		expect(wrapper.find('[data-test="search-results-page"]').exists()).toBe(
			true
		);
	});

	test('renders search results section after API call', () => {
		expect(wrapper.find('[data-test="search-results-section"]').exists()).toBe(
			true
		);
	});

	test('renders search results section header properly', () => {
		expect(
			wrapper.get('[data-test="search-results-section-header-p"]').text()
		).toBe(
			`You searched "${wrapper.vm.searchTerm}" in ${wrapper.vm.county} County and you got ${wrapper.vm.searchResult.count} results`
		);
	});

	test('renders request data button properly', () => {
		expect(
			wrapper
				.find('[data-test="search-results-section-header-button"]')
				.exists()
		).toBe(true);
	});

	test('request data button opens form', () => {
		window.open = vi.fn();

		wrapper
			.get('[data-test="search-results-section-header-button"]')
			.trigger('click');

		expect(window.open).toHaveBeenCalledWith(
			'https://airtable.com/shrbFfWk6fjzGnNsk',
			'_blank'
		);
	});

	test('search results content section renders', () => {
		expect(wrapper.find('[data-test="search-results-content"]').exists()).toBe(
			true
		);
	});

	test('search results card count matches search results returned in data', () => {
		expect(wrapper.findAll('[data-test="search-results-cards"]').length).toBe(
			wrapper.vm.searchResult.count
		);
	});
});

describe('SearchResultPage shows loading screen before API call completes', () => {
	test('loading section appears before API call completes', async () => {
		axios.get.mockImplementation(() => {
			return new Promise((resolve) => {
				setTimeout(() => resolve({ data: { count: 0, data: {} } }), 100); // Simulate 1-second delay
			});
		});

		const wrapper = shallowMount(SearchResultPage, {
			global: {
				mocks: {
					$route: $routeMock,
				},
			},
		});

		expect(wrapper.find('[data-test="loading-section"]').exists()).toBe(true);

		await wrapper.vm.search();

		expect(wrapper.find('[data-test="loading-section"]').exists()).toBe(false);

		expect(wrapper.find('[data-test="search-results-section"]').exists()).toBe(
			true
		);
	});
});

describe('SearchResultPage shows no results found when no data returns', () => {
	test('search results page shows no results properly', async () => {
		await axios.get.mockResolvedValue({
			data: {
				count: 0,
				data: [],
			},
		});

		const wrapper = shallowMount(SearchResultPage, {
			global: {
				mocks: {
					$route: $routeMock,
				},
			},
		});

		await flushPromises();

		expect(wrapper.find('[data-test="no-search-results"]').exists()).toBe(true);
	});
});
