import SearchResultPage from "../SearchResultPage.vue";
// import { FlexContainer } from "pdap-design-system";
import { flushPromises, mount } from "@vue/test-utils";
import { describe, expect, vi, test, beforeEach, beforeAll } from "vitest";
import axios from "axios";
import { resultsMock } from "../__mocks__";
import { nextTick } from "vue";

vi.mock("axios");

const $routeMock = {
	params: {
		searchTerm: "calls",
		location: "Cook",
	},
};

let wrapper;

beforeAll(() => {
	import.meta.env.VITE_VUE_APP_BASE_URL = "https://data-sources.pdap.io";
});

describe("SearchResultPage renders with data", () => {
	beforeEach(() => {
		wrapper = mount(SearchResultPage, {
			global: {
				mocks: {
					$route: $routeMock,
				},
				stubs: {
					FlexContainer: {
						template: "<main><slot /></main>",
					},
				},
			},
		});

		axios.get.mockResolvedValue({
			data: resultsMock,
		});
	});

	test("Calls API and renders search results", async () => {
		const searchTerm = wrapper.vm.searchTerm;
		const location = wrapper.vm.location;

		await wrapper.vm.search();
		await flushPromises();

		// TODO: figure out why this is called twice
		expect(axios.get).toHaveBeenCalledTimes(2);
		expect(axios.get).toHaveBeenCalledWith(
			`https://data-sources.pdap.io/search-tokens?endpoint=quick-search&arg1=${searchTerm}&arg2=${location}`,
		);

		await nextTick();

		expect(wrapper.find('[data-test="search-results-page"]').exists()).toBe(
			true,
		);
		expect(wrapper.html()).toMatchSnapshot();
	});

	test("renders search results section header properly", () => {
		axios.get.mockResolvedValue({
			data: resultsMock,
		});

		const searchTerm = wrapper.vm.searchTerm;
		const location = wrapper.vm.location;
		const count = wrapper.vm.searchResult.count;

		expect(
			wrapper.get('[data-test="search-results-section-header-p"]').text(),
		).toBe(
			`Searching for "${searchTerm}" in "${location}". Found ${count} results.`,
		);
	});

	test("renders search result count properly", () => {
		// const count = wrapper.vm.searchResult.count;

		expect(wrapper.get('[data-test="search-results-count"]').text()).toBe(
			`Found ${wrapper.vm.getResultsCopy()}.`,
		);
	});

	test("request data link has correct href value", () => {
		expect(
			wrapper.get('[data-test="search-results-request-link"]').attributes()
				.href,
		).toBe("https://airtable.com/shrbFfWk6fjzGnNsk");
	});

	test("search results card count matches search results returned in data", () => {
		expect(wrapper.findAll('[data-test="search-results-cards"]').length).toBe(
			wrapper.vm.searchResult.count,
		);
	});
});

describe("SearchResultPage shows no results found when no data returns", () => {
	test("search results page shows no results properly", async () => {
		axios.get.mockResolvedValue({
			data: {
				count: 0,
				data: [],
			},
		});

		wrapper = mount(SearchResultPage, {
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
