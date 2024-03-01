import { flushPromises, mount } from '@vue/test-utils';
import { describe, expect, beforeEach, it, vi } from 'vitest';
import { nextTick } from 'vue';
import { createTestingPinia } from '@pinia/testing';
import { useUserStore } from '../../stores/user';

import ChangePassword from '../ChangePassword.vue';

let wrapper;
let user;

describe('Change password page', () => {
	beforeEach(() => {
		wrapper = mount(ChangePassword, {
			global: {
				plugins: [createTestingPinia()],
			},
		});
		user = useUserStore();
	});

	it('Calls the change password method with valid data and displays success message', async () => {
		const password = wrapper.find('[data-test="password"] input');
		const confirmPassword = wrapper.find(
			'[data-test="confirm-password"] input',
		);
		const form = wrapper.find('[data-test="change-password-form"]');

		[confirmPassword, password, form].forEach((el) =>
			expect(el.exists()).toBe(true),
		);

		expect(wrapper.html()).toMatchSnapshot();

		await password.setValue('Password1!');
		await confirmPassword.setValue('Password1!');

		form.trigger('submit');
		await flushPromises();

		expect(user.changePassword).toHaveBeenCalledOnce();
	});

	it('Renders error message with mismatched passwords when trying to sign up and re-validates form', async () => {
		const password = wrapper.find('[data-test="password"] input');
		const confirmPassword = wrapper.find(
			'[data-test="confirm-password"] input',
		);
		const form = wrapper.find('[data-test="change-password-form"]');

		[confirmPassword, password, form].forEach((el) =>
			expect(el.exists()).toBe(true),
		);

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

	it('Handles API error', async () => {
		const mockError = new Error('foo');
		vi.mocked(user.changePassword).mockRejectedValueOnce(mockError);

		const password = wrapper.find('[data-test="password"] input');
		const confirmPassword = wrapper.find(
			'[data-test="confirm-password"] input',
		);
		const form = wrapper.find('[data-test="change-password-form"]');

		await password.setValue('Password1!');
		await confirmPassword.setValue('Password1!');

		form.trigger('submit');
		await flushPromises();
		await nextTick();

		await flushPromises();

		const error = form.find('.pdap-form-error-message');
		expect(error.exists()).toBe(true);
		expect(error.text()).toBe('foo');
	});
});
