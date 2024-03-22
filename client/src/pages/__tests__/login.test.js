import { RouterLinkStub, flushPromises, mount } from '@vue/test-utils';
import { describe, expect, vi, beforeEach, it } from 'vitest';
import { nextTick } from 'vue';
import LogIn from '../LogIn.vue';
import { createTestingPinia } from '@pinia/testing';
import { useAuthStore } from '../../stores/auth';
import { useUserStore } from '../../stores/user';

const push = vi.fn();
const $routerMock = {
	push,
};

let wrapper;

describe('Login page', () => {
	beforeEach(() => {
		wrapper = mount(LogIn, {
			global: {
				mocks: {
					router: $routerMock,
				},
				plugins: [createTestingPinia()],
				stubs: {
					RouterLink: RouterLinkStub,
				},
			},
		});
	});

	describe('Login/Logout', () => {
		let auth;

		beforeEach(() => {
			auth = useAuthStore();
		});

		it('Calls the login method with valid form data', async () => {
			const email = wrapper.find('[data-test="email"] input');
			const password = wrapper.find('[data-test="password"] input');
			const form = wrapper.find('[data-test="login-form"]');

			await email.setValue('hello@hello.com');
			await password.setValue('Password1!');

			form.trigger('submit');
			await flushPromises();

			expect(auth.login).toHaveBeenCalledWith('hello@hello.com', 'Password1!');
			expect(wrapper.html()).toMatchSnapshot();
		});

		describe('Success and already logged in states', async () => {
			beforeEach(() => {
				auth.userId = 42;
			});

			it('Displays success copy', async () => {
				wrapper.vm.success = "You're now logged in!";
				await nextTick();

				const heading = await wrapper.find('[data-test="success-heading"]');
				const subheading = await wrapper.find(
					'[data-test="success-subheading"]',
				);

				expect(heading.text()).toBe('Success');
				expect(subheading.text()).toBe("You're now logged in!");
			});

			it('Logs user out', async () => {
				const logout = await wrapper.find('[data-test="logout-button"]');

				expect(logout.exists()).toBe(true);

				logout.trigger('click');
				await flushPromises();

				expect(auth.logout).toHaveBeenCalledOnce();
			});
		});

		it('Handles API error', async () => {
			const mockError = new Error('foo');
			vi.mocked(auth.login).mockRejectedValueOnce(mockError);

			const email = wrapper.find('[data-test="email"] input');
			const password = wrapper.find('[data-test="password"] input');
			const form = wrapper.find('[data-test="login-form"]');

			await email.setValue('hello@hello.com');
			await password.setValue('Password1!');

			form.trigger('submit');
			await flushPromises();

			const error = form.find('.pdap-form-error-message');
			expect(error.exists()).toBe(true);
			expect(error.text()).toBe('Something went wrong, please try again.');
		});
	});

	describe('Signup', () => {
		let toggle;
		let user;

		beforeEach(() => {
			toggle = wrapper.find('[data-test="toggle-button"]');
			user = useUserStore();
		});

		it('Calls the signup method with valid data', async () => {
			expect(toggle.exists()).toBe(true);
			toggle.trigger('click');

			await nextTick();

			const email = wrapper.find('[data-test="email"] input');
			const password = wrapper.find('[data-test="password"] input');
			const confirmPassword = wrapper.find(
				'[data-test="confirm-password"] input',
			);
			const form = wrapper.find('[data-test="login-form"]');

			await email.setValue('hello@hello.com');
			await password.setValue('Password1!');
			await confirmPassword.setValue('Password1!');

			form.trigger('submit');
			await flushPromises();
			await nextTick();

			expect(user.signup).toHaveBeenCalledOnce();
			expect(wrapper.html()).toMatchSnapshot();
		});

		it('Renders error message with mismatched passwords when trying to sign up and re-validates form', async () => {
			expect(toggle.exists()).toBe(true);
			toggle.trigger('click');

			await nextTick();

			const email = wrapper.find('[data-test="email"] input');
			const password = wrapper.find('[data-test="password"] input');
			const confirmPassword = wrapper.find(
				'[data-test="confirm-password"] input',
			);
			const form = wrapper.find('[data-test="login-form"]');

			await email.setValue('hello@hello.com');
			await password.setValue('Password1!');
			await confirmPassword.setValue('Password');

			form.trigger('submit');
			await flushPromises();
			await nextTick();

			const error = form.find('.pdap-form-error-message');

			expect(error.exists()).toBe(true);
			expect(error.text()).toBe('Passwords do not match, please try again.');
			expect(wrapper.html()).toMatchSnapshot();

			await nextTick();

			confirmPassword.setValue('Pasdasdfasdf');
			await nextTick();
			expect(error.exists()).toBe(true);
		});
	});

	describe('Miscellaneous states', () => {
		it('Toggles form type', async () => {
			const toggle = wrapper.find('[data-test="toggle-button"]');
			const submit = wrapper.find('[data-test="submit-button"]');

			toggle.trigger('click');
			await nextTick();

			expect(submit.text()).toBe('Create account');

			toggle.trigger('click');
			await nextTick();

			expect(submit.text()).toBe('Login');
		});

		it('Renders button loading copy', async () => {
			wrapper.vm.loading = true;
			wrapper.vm.$forceUpdate();

			expect(wrapper.vm.getSubmitButtonCopy()).toBe('Loading...');
		});
	});
});
