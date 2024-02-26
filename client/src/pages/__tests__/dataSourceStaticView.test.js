import { flushPromises, mount } from '@vue/test-utils';
import DataSourceStaticView from '../DataSourceStaticView.vue';
import { beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import axios from 'axios';
import { nextTick } from 'vue';
import { dataSourceMock } from '../__mocks__';

let wrapper;

const push = vi.fn();
const $routerMock = {
	push,
};
const $routeMock = {
	params: {
		id: 'test',
	},
};
vi.mock('axios');

beforeAll(() => {
	import.meta.env.VITE_VUE_API_BASE_URL = 'https://data-sources.pdap.io';
});

describe('DataSourceStaticView', () => {
	beforeEach(() => {
		wrapper = mount(DataSourceStaticView, {
			global: {
				mocks: {
					$router: $routerMock,
					$route: $routeMock,
				},
			},
		});

		axios.get.mockResolvedValue({ data: dataSourceMock });
	});

	it('Calls API and renders search results', async () => {
		const id = wrapper.vm.id;

		await wrapper.vm.getDataSourceDetails();
		await flushPromises();

		// TODO: figure out why this is called twice
		expect(axios.get).toHaveBeenCalledTimes(2);
		expect(axios.get).toHaveBeenLastCalledWith(
			`https://data-sources.pdap.io/search-tokens?endpoint=data-sources-by-id&arg1=${id}`,
		);

		await nextTick();

		expect(wrapper.find('[data-test="data-source-static-view"]').exists()).toBe(
			true,
		);
		expect(wrapper.html()).toMatchSnapshot();
	});

	it('Routes back to / on new search button click', () => {
		wrapper.find('[data-test="new-search-button"]').trigger('click');
		expect(push).toHaveBeenCalledWith('/');
	});

	it('Routes back to /search on Record Type button click with correct parameters', async () => {
		const button = wrapper.find('[data-test="record-type-button"]');

		expect(button.exists()).toBe(true);

		const type = button.text();

		button.trigger('click');

		await nextTick();

		expect(push).toHaveBeenLastCalledWith(`/search/${type}/all`);
	});

	it('Routes back to /search on Agency Name button click with correct parameters', async () => {
		const button = wrapper.find('[data-test="agency-name-button"]');

		expect(button.exists()).toBe(true);

		const name = button.text();

		button.trigger('click');

		await nextTick();

		expect(push).toHaveBeenLastCalledWith(`/search/all/${name}`);
	});

	it('Opens link on archive button click.', async () => {
		const spy = vi.spyOn(window, 'open');
		const button = wrapper.find('[data-test="view-archives-button"]');

		expect(button.exists()).toBe(true);

		button.trigger('click');

		await nextTick();

		expect(spy).toHaveBeenLastCalledWith(
			`https://web.archive.org/web/*/${dataSourceMock.source_url}`,
			'_blank',
		);
	});

	// it("renders correctly when there is no data", () => {
	// 	const wrapper = mount(DataSourceStaticView, {
	// 		data() {
	// 			return {
	// 				noData: true,
	// 				errorMessage: "No data available",
	// 			};
	// 		},
	// 	});

	// 	expect(wrapper.find("h2").text()).toBe("No data available");
	// });

	// Add more test cases as needed
});
