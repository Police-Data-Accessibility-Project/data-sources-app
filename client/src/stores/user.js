import axios from 'axios';
import { defineStore } from 'pinia';
import { useAuthStore } from './auth';

const HEADERS = {
	headers: { 'Content-Type': 'application/json' },
};
const SIGNUP_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/user`;
const CHANGE_PASSWORD_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/user`;
const REQUEST_PASSWORD_RESET_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/request-reset-password`;
const PASSWORD_RESET_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/reset-password`;

export const useUserStore = defineStore('user', {
	state: () => ({
		email: '',
	}),
	persist: true,
	actions: {
		async signup(email, password) {
			const auth = useAuthStore();

			await axios.post(SIGNUP_URL, { email, password }, HEADERS);
			// Update store with email
			this.$patch({ email });
			// Log users in after signup and return that response
			return await auth.login(email, password);
		},

		async changePassword(email, password) {
			const auth = useAuthStore();
			await axios.put(
				CHANGE_PASSWORD_URL,
				{ email, password },
				{
					headers: {
						...HEADERS.headers,
						Authorization: `Bearer ${auth.accessToken.value}`,
					},
				},
			);
			return await auth.login(email, password);
		},

		async requestPasswordReset(email) {
			await axios.post(REQUEST_PASSWORD_RESET_URL, { email }, HEADERS);
		},

		async resetPassword(password, token) {
			await axios.post(`${PASSWORD_RESET_URL}`, { password, token }, HEADERS);
		},
	},
});
