import { mount } from '@vue/test-utils';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import AuthWrapper from '../AuthWrapper.vue';
import { createTestingPinia } from '@pinia/testing';
import { useAuthStore } from '../../stores/auth';
import { nextTick } from 'vue';

vi.mock('vue-router/auto-routes');
vi.mock('vue-router', async () => {
	const actual = await vi.importActual('vue-router');
	return {
		...actual,
		useRoute: vi.fn(() => {
			return routeMock;
		}),
	};
});

const routeMock = {
	meta: {
		auth: true,
	},
};

let wrapper;

const NOW = Date.now();
const NOW_MINUS_THIRTY = NOW - 30 * 1000;
const NOW_PLUS_THIRTY = NOW + 30 * 1000;

describe('AuthWrapper', () => {
	beforeEach(() => {
		wrapper = mount(AuthWrapper, {
			global: {
				plugins: [createTestingPinia()],
			},
		});

		vi.unstubAllGlobals();
	});

	it('renders auth wrapper', () => {
		expect(wrapper.find('[id="wrapper"]').exists()).toBe(true);
		expect(wrapper.html()).toMatchSnapshot();
	});

	it('refreshes access token when less than 1 minute remaining before access token expiry on event', async () => {
		const auth = useAuthStore();
		auth.$patch({
			userId: 42,
			tokens: {
				accessToken: {
					expires: NOW_PLUS_THIRTY,
				},
			},
		});

		await wrapper.trigger('click');
		await nextTick();
		expect(auth.refreshAccessToken).toHaveBeenCalled();
	});

	it('logs user out when access token is expired on all expected events', async () => {
		const auth = useAuthStore();
		auth.$patch({
			userId: 42,
			tokens: {
				accessToken: {
					expires: NOW_MINUS_THIRTY,
				},
			},
		});

		await wrapper.trigger('click');
		await nextTick();
		expect(auth.logout).toHaveBeenCalled();
	});
});
