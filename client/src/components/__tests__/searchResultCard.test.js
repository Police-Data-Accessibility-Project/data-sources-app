import SearchResultCard from "../SearchResultCard.vue";
import { mount } from "@vue/test-utils";
import { describe, it, expect, beforeEach, vi } from "vitest";
import { nextTick } from "vue";

let wrapper;

// const $routerMock = vi.mock("vue-router");
const push = vi.fn();
const $routerMock = {
	push,
};

describe("SearchResultCard with all data", () => {
	const dataSource = {
		agency_name: "Cicero Police Department - IN",
		agency_supplied: false,
		airtable_uid: "rec7edsmcuVQwMMXG",
		coverage_end: "2018-01-01",
		coverage_start: "2017-01-01",
		data_source_name: "Calls for Service for Cicero Police Department - IN",
		municipality: "Bridgeview",
		name: "Cicero Police Department - IN",
		record_format: "['json', 'pdf']",
		record_type: "Calls for Service",
		source_url:
			"https://cityprotect.com/agency/cc0d9a3d-50b2-4424-ae25-5699ba6eaff9",
		state_iso: "IN",
	};

	beforeEach(() => {
		wrapper = mount(SearchResultCard, {
			props: { dataSource },
			global: {
				mocks: {
					$router: $routerMock,
				},
			},
		});

		vi.unstubAllGlobals();
	});

	it("search result card exists with full data", () => {
		expect(wrapper.find('[data-test="search-result-card"]').exists()).toBe(
			true,
		);
		expect(wrapper.html()).toMatchSnapshot();
	});

	it("search result card contains a title", () => {
		expect(wrapper.get('[data-test="search-result-title"]').text()).toBe(
			dataSource.data_source_name,
		);
	});

	it("search result card contains an agency section", () => {
		expect(wrapper.find('[data-test="search-result-agency"]').exists()).toBe(
			true,
		);
	});

	it("search result card contains correct agency name", () => {
		expect(wrapper.get('[data-test="search-result-agency-known"]').text()).toBe(
			dataSource.agency_name,
		);
	});
	/* hiding place for now
	it('search result card contains a place section', () => {
		expect(wrapper.find('[data-test="search-result-place"]').exists()).toBe(
			true
		);
	});

	it('search result card contains correct place format', () => {
		expect(
			wrapper.get('[data-test="search-result-place-state-municipality"]').text()
		).toBe(`${dataSource.municipality}, ${dataSource.state_iso}`);
	});
*/
	it("search result card contains a record section", () => {
		expect(
			wrapper.find('[data-test="search-result-record-label"]').exists(),
		).toBe(true);
	});

	it("search result card contains correct record type", () => {
		expect(wrapper.get('[data-test="search-result-record-type"]').text()).toBe(
			dataSource.record_type,
		);
	});

	it("search result card contains a coverage date section", () => {
		expect(
			wrapper.find('[data-test="search-result-label-coverage"]').exists(),
		).toBe(true);
	});

	it("search result card contains correct coverage start and end date", () => {
		expect(
			wrapper.get('[data-test="search-result-coverage-start-end"]').text(),
		).toBe(
			`${wrapper.vm.formatDate(
				dataSource.coverage_start,
			)}–${wrapper.vm.formatDate(dataSource.coverage_end)}`,
		);
	});

	it("search result card contains a record formats section", () => {
		expect(
			wrapper.find('[data-test="search-result-label-formats"]').exists(),
		).toBe(true);
	});

	it("search result card contains a record formats div for each format", () => {
		expect(wrapper.find('[data-test="search-result-formats"]').exists()).toBe(
			true,
		);
	});

	it("Visit source button exists and calls window navigation with correct value on click", async () => {
		const spy = vi.spyOn(window, "open");

		const button = wrapper.find(
			'[data-test="search-result-visit-source-button"]',
		);

		expect(button.exists()).toBe(true);

		await button.trigger("click");

		await nextTick();

		expect(spy).toHaveBeenCalledOnce();
		expect(spy).toHaveBeenCalledWith(dataSource.source_url, "_blank");
	});

	it("View details button exists and calls router.push with correct value on click", async () => {
		const button = wrapper.find(
			'[data-test="search-result-source-details-button"]',
		);

		expect(button.exists()).toBe(true);

		await button.trigger("click");

		await nextTick();

		expect(push).toHaveBeenCalledOnce();
		expect(push).toHaveBeenCalledWith(
			`/data-sources/${dataSource.airtable_uid}`,
		);
	});
});

describe("SearchResultCard with missing data", () => {
	const dataSource = {
		agency_name: null,
		agency_supplied: false,
		airtable_uid: "rec7edsmcuVQwMMXG",
		coverage_end: null,
		coverage_start: null,
		data_source_name: "Calls for Service for Cicero Police Department - IN",
		municipality: null,
		name: null,
		record_format: null,
		record_type: null,
		source_url: null,
		state_iso: null,
	};

	beforeEach(() => {
		wrapper = mount(SearchResultCard, {
			props: { dataSource },
		});
	});

	it("search result card exists with missing data", () => {
		expect(wrapper.find('[data-test="search-result-card"]').exists()).toBe(
			true,
		);
		expect(wrapper.html()).toMatchSnapshot();
	});

	it("search result card contains unknown for agency name", () => {
		expect(
			wrapper.find('[data-test="search-result-agency-unknown"]').exists(),
		).toBe(true);
	});

	// it("search result card contains unknown for place", () => {
	// 	expect(
	// 		wrapper.find('[data-test="search-result-place-unknown"]').exists(),
	// 	).toBe(true);
	// });

	it("search result card contains unknown for record type", () => {
		expect(
			wrapper.find('[data-test="search-result-record-type-unknown"]').exists(),
		).toBe(true);
	});

	it("search result card contains unknown for coverage", () => {
		expect(
			wrapper.find('[data-test="search-result-coverage-unknown"]').exists(),
		).toBe(true);
	});

	it("search result card contains unknown for record formats", () => {
		expect(
			wrapper.find('[data-test="search-result-format-unknown"]').exists(),
		).toBe(true);
	});
});

// describe("SearchResultCard with municipality but not state", () => {
// 	const dataSource = {
// 		municipality: "Bridgeview",
// 		state_iso: null,
// 	};

// 	wrapper = mount(SearchResultCard, {
// 		props: { dataSource },
// 	});

// 	it("search result card has only municipality", () => {
// 		expect(
// 			wrapper.get('[data-test="search-result-place-municipality"]').text(),
// 		).toBe(dataSource.municipality);
// 	});
// });

// describe("SearchResultCard with state but not municipality", () => {
// 	const dataSource = {
// 		municipality: null,
// 		state_iso: "IN",
// 	};

// 	wrapper = mount(SearchResultCard, {
// 		props: { dataSource },
// 	});

// 	it("search result card has only state", () => {
// 		expect(wrapper.get('[data-test="search-result-place-state"]').text()).toBe(
// 			dataSource.state_iso,
// 		);
// 	});
// });

describe("SearchResultCard with coverage start but not end", () => {
	const dataSource = {
		coverage_start: "2017-01-01",
		coverage_end: null,
	};

	beforeEach(() => {
		wrapper = mount(SearchResultCard, {
			props: { dataSource },
		});
	});

	it("search result card exists with coverage start but not end", () => {
		expect(wrapper.find('[data-test="search-result-card"]').exists()).toBe(
			true,
		);
		expect(wrapper.html()).toMatchSnapshot();
	});

	it("search result card has only coverage start date", () => {
		expect(
			wrapper.get('[data-test="search-result-coverage-start"]').text(),
		).toContain(wrapper.vm.formatDate(dataSource.coverage_start));
	});
});

describe("SearchResultCard with coverage end but not start", () => {
	const dataSource = {
		coverage_start: null,
		coverage_end: "2017-01-01",
	};

	beforeEach(() => {
		wrapper = mount(SearchResultCard, {
			props: { dataSource },
		});
	});

	it("search result card exists with coverage end but not start", () => {
		expect(wrapper.find('[data-test="search-result-card"]').exists()).toBe(
			true,
		);
		expect(wrapper.html()).toMatchSnapshot();
	});

	it("search result card has only coverage end date", () => {
		expect(
			wrapper.get('[data-test="search-result-coverage-end"]').text(),
		).toContain(wrapper.vm.formatDate(dataSource.coverage_end));
	});
});
