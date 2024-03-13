import { mount } from '@vue/test-utils';
import { beforeEach, describe, expect, it } from 'vitest';
import ErrorBoundary from '../ErrorBoundary.vue';
import { nextTick } from 'vue';

let wrapper;

describe('AuthWrapper', () => {
	beforeEach(() => {
		wrapper = mount(ErrorBoundary, {
			slots: {
				default: '<div data-test="default-slot" />',
			},
		});
	});

	it('renders slot content with no error', () => {
		expect(wrapper.find('[data-test="default-slot"]').exists()).toBe(true);
		expect(wrapper.html()).toMatchSnapshot();
	});

	it('renders error content with error', async () => {
		wrapper.vm.interceptError(new Error('Generic error'));
		await nextTick();

		expect(wrapper.find('[data-test="error-boundary-message"]').exists()).toBe(
			true,
		);
		expect(wrapper.html()).toMatchSnapshot();
	});
});
