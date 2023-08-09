import SearchResultPage from '../pages/SearchResultPage.vue';
import { mount } from '@vue/test-utils';
import { describe, it, expect } from 'vitest';

describe('SearchResultPage successfully renders components', async () => {
	const wrapper = mount(SearchResultPage, {
		global: {
			mocks: {
				$route: {
					params: {
						searchTerm: 'calls',
						county: 'Cook',
					},
				},
			},
		},
	});

	it('search results page exists', () => {
		expect(wrapper.find('[data-test="search-result-page"]').exists()).toBe(
			true
		);
	});
});
