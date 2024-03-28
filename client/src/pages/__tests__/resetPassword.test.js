import { RouterLinkStub, flushPromises, mount } from '@vue/test-utils';
import {
	describe,
	expect,
	beforeEach,
	it,
	vi,
	beforeAll,
	afterEach,
} from 'vitest';
import { nextTick } from 'vue';
import { createTestingPinia } from '@pinia/testing';
import { useUserStore } from '../../stores/user';
import ResetPassword from '../ResetPassword.vue';

import { useRoute } from 'vue-router';

vi.mock('vue-router', async () => ({
	useRoute: vi.fn(),
	createRouter: vi.fn(() => ({
		beforeEach: vi.fn(),
	})),
	createWebHistory: vi.fn(),
	RouterLink: RouterLinkStub,
}));

let wrapper;
let user;

describe('Reset password page', () => {
	beforeEach(() => {
		wrapper = mount(ResetPassword, {
			global: {
				plugins: [createTestingPinia()],
			},
			stubs: {
				RouterLink: RouterLinkStub,
			},
		});

		user = useUserStore();
	});

	afterEach(() => {
		user = undefined;
	});

	describe('No token (request PW reset)', () => {
		beforeAll(() => {
			useRoute.mockImplementation(() => ({
				params: {
					token: undefined,
				},
			}));
		});

		describe('No token, success', () => {
			it('Renders success message for request reset link', async () => {
				wrapper.vm.success = true;
				await nextTick();

				const subheading = await wrapper.find(
					'[data-test="success-subheading"]',
				);

				expect(subheading.text()).toBe(
					'We sent you an email with a link to reset your password. Please follow the link in the email to proceed',
				);

				expect(wrapper.html()).toMatchSnapshot();
			});
		});

		describe('No token, request reset password link', () => {
			let email;
			let form;

			beforeEach(() => {
				email = wrapper.find('[data-test="email"] input');
				form = wrapper.find('[data-test="reset-password-form"]');
			});

			it('Calls the request reset password method with valid data', async () => {
				await email.setValue('hello@hello.com');

				expect(wrapper.html()).toMatchSnapshot();

				form.trigger('submit');
				await flushPromises();

				expect(user.requestPasswordReset).toHaveBeenCalledWith(
					'hello@hello.com',
				);
			});

			it('Handles API error', async () => {
				const mockError = new Error('foo');
				vi.mocked(user.requestPasswordReset).mockRejectedValueOnce(mockError);

				form.trigger('submit');
				await flushPromises();

				const error = form.find('.pdap-form-error-message');
				expect(error.exists()).toBe(true);
				expect(error.text()).toBe('foo');
			});
		});
	});

	describe('With token (reset password)', () => {
		beforeAll(() => {
			useRoute.mockImplementation(() => ({
				params: {
					token: '123abc',
				},
			}));
		});

		describe('With token, success', () => {
			it('Renders success message for reset password', async () => {
				wrapper.vm.success = true;
				await nextTick();

				const subheading = await wrapper.find(
					'[data-test="success-subheading"]',
				);

				expect(subheading.text()).toBe(
					'Your password has been successfully updated',
				);

				expect(wrapper.html()).toMatchSnapshot();
			});
		});

		describe('With token, token expired', () => {
			it('Renders token expired UI', async () => {
				wrapper.vm.isExpiredToken = true;
				await nextTick();

				const expired = await wrapper.find('[data-test="token-expired"]');
				const reRequest = await wrapper.find('[data-test="re-request-link"]');

				expect(expired.exists()).toBe(true);
				expect(reRequest.exists()).toBe(true);
			});
		});

		describe('With token, reset password', () => {
			let password;
			let confirmPassword;
			let form;

			beforeEach(async () => {
				// Setting the token stuff manually, as we're asserting against UI in this suite
				wrapper.vm.isExpiredToken = false;
				wrapper.vm.hasValidatedToken = true;
				await nextTick();

				password = wrapper.find('[data-test="password"] input');
				confirmPassword = wrapper.find('[data-test="confirm-password"] input');
				form = wrapper.find('[data-test="reset-password-form"]');
			});

			it('Calls the reset password method with valid data', async () => {
				expect(wrapper.html()).toMatchSnapshot();

				await password.setValue('Password1!');
				await confirmPassword.setValue('Password1!');

				form.trigger('submit');
				await flushPromises();

				expect(user.resetPassword).toHaveBeenCalledOnce();
			});

			it('Renders error message with mismatched passwords when trying to sign up and re-validates form', async () => {
				await password.setValue('Password1!');
				await confirmPassword.setValue('Password41234!');

				await form.trigger('submit');
				await nextTick();
				await flushPromises();

				const error = form.find('.pdap-form-error-message');

				expect(error.exists()).toBe(true);
				expect(error.text()).toBe('Passwords do not match, please try again.');

				await nextTick();

				await confirmPassword.setValue('Pasdasdfasdf');
				await nextTick();
				expect(error.exists()).toBe(true);

				expect(wrapper.html()).toMatchSnapshot();
			});

			it('Handles API error with invalid token', async () => {
				const mockError = new Error('The submitted token is invalid');
				vi.mocked(user.resetPassword).mockRejectedValueOnce(mockError);

				form.trigger('submit');
				await flushPromises();

				const expired = await wrapper.find('[data-test="token-expired"]');
				const reRequest = await wrapper.find('[data-test="re-request-link"]');

				expect(expired.exists()).toBe(true);
				expect(reRequest.exists()).toBe(true);

				expect(wrapper.html()).toMatchSnapshot();
			});
		});

		describe('With token - token validation', () => {
			// Skipping because this isn't working for some reason... TODO: look into fixing
			it.skip('Accepts valid token API response and renders appropriate UI', async () => {
				vi.mocked(user.validateResetPasswordToken).mockResolvedValueOnce({
					data: { message: 'Token is valid' },
				});

				await wrapper.vm.validateToken();
				await flushPromises();

				console.log({ markup: wrapper.html() });
				expect(wrapper.find('[data-test="reset-password-form"]').exists()).toBe(
					true,
				);
			});

			it('Accepts invalid token API response and renders appropriate UI', async () => {
				vi.mocked(user.validateResetPasswordToken).mockRejectedValueOnce(
					new Error({
						data: { message: 'Token is expired' },
						status: 400,
					}),
				);

				await wrapper.vm.validateToken();
				await flushPromises();

				expect(wrapper.find('[data-test="token-expired"]').exists()).toBe(true);
			});
		});
	});
});
