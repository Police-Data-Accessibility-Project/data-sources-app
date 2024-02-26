import axios from 'axios';
import { defineStore } from 'pinia';
import { useAuthStore } from './auth';

const HEADERS = {
	headers: { 'Content-Type': 'application/json' },
};
const SIGNUP_URL = `${import.meta.env.VITE_VUE_APP_BASE_URL}/user`;
const CHANGE_PASSWORD_URL = `${import.meta.env.VITE_VUE_APP_BASE_URL}/user`;
const REQUEST_PASSWORD_RESET_URL = `${import.meta.env.VITE_VUE_APP_BASE_URL}/request-reset-password`;
const PASSWORD_RESET_URL = `${import.meta.env.VITE_VUE_APP_BASE_URL}/reset-password`;

export const useUserStore = defineStore('user', {
	state: () => ({
		email: '',
	}),
	persist: true,
	actions: {
		async signup(email, password) {
			const auth = useAuthStore();

			try {
				await axios.post(SIGNUP_URL, { email, password }, HEADERS);
				// Update store with email
				this.$patch({ email });
				// Log users in after signup and return that response
				return await auth.login(email, password);
			} catch (error) {
				throw new Error(error.response.data.message);
			}
		},

		async changePassword(email, password) {
			const auth = useAuthStore();
			try {
				await axios.put(CHANGE_PASSWORD_URL, { email, password }, HEADERS);
				return await auth.login(email, password);
			} catch (error) {
				throw new Error(error.response.data.message);
			}
		},

		async requestPasswordReset(email) {
			try {
				await axios.get(REQUEST_PASSWORD_RESET_URL, { email }, HEADERS);
			} catch (error) {
				throw new Error(error.response.data.message);
			}
		},

		async resetPassword(email, password, token) {
			try {
				const resetResponse = await axios.get(
					`${PASSWORD_RESET_URL}/${token}`,
					HEADERS,
				);

				if (400 > resetResponse.status > 200) {
					return await this.changePassword(email, password);
				}
			} catch (error) {
				throw new Error(error.response.data.message);
			}
		},
	},
});
