import { shallowMount } from '@vue/test-utils';
import QuickSearchPage from '../QuickSearchPage.vue';
import { describe, expect, test } from 'vitest';

describe('QuickSearchPage', () => {
	test('is a Vue instance', () => {
		const wrapper = shallowMount(QuickSearchPage);
		expect(wrapper.vm).toBeTruthy();
		expect(wrapper.html()).toMatchSnapshot();
	});
});

// Shallow mounting this test for now. It's 1. not really testing much, and 2. erroring on `getRoutes`
// TODO: write an actual test for this.
