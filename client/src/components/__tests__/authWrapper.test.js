import { mount } from '@vue/test-utils';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import AuthWrapper from '../AuthWrapper.vue';
import { createTestingPinia } from '@pinia/testing';
import { useAuthStore } from '../../stores/auth';
import { nextTick } from 'vue';
import { useUserStore } from '@/stores/user';

const { mockRefreshAccessToken, mockSignOut, replace } = vi.hoisted(() => ({
	mockRefreshAccessToken: vi.fn(),
	mockSignOut: vi.fn(),
	replace: vi.fn(),
}));

vi.mock('../../api/auth', async () => {
	return {
		refreshTokens: mockRefreshAccessToken,
		signOut: mockSignOut,
	};
});

vi.mock('vue-router/auto-routes');
vi.mock('vue-router', async () => {
	const actual = await vi.importActual('vue-router');
	return {
		...actual,
		useRouter: vi.fn(() => {
			return {
				replace,
			};
		}),
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

const NOW = new Date().getTime();
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
		const user = useUserStore();
		auth.$patch({
			tokens: {
				accessToken: {
					value: 'foo',
					expires: NOW_PLUS_THIRTY,
				},
			},
		});
		user.$patch({ id: 42 });

		await wrapper.trigger('click');
		await nextTick();
		expect(mockRefreshAccessToken).toHaveBeenCalled();
	});

	it('logs user out when access token is expired on all expected events', async () => {
		const auth = useAuthStore();
		const user = useUserStore();

		auth.$patch({
			tokens: {
				accessToken: {
					value: 'foo',
					expires: NOW_MINUS_THIRTY,
				},
			},
		});
		user.$patch({ id: 42 });

		await wrapper.trigger('click');
		await nextTick();
		expect(mockSignOut).toHaveBeenCalled();
	});
});
