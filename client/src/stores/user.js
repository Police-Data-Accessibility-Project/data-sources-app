import axios from 'axios';
import { defineStore } from 'pinia';
import { useAuthStore } from './auth';

const HEADERS = { 'Content-Type': 'application/json' };
const SIGNUP_WITH_EMAIL_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/user`;
const CHANGE_PASSWORD_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/user`;
const REQUEST_PASSWORD_RESET_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/request-reset-password`;
const PASSWORD_RESET_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/reset-password`;
const VALIDATE_PASSWORD_RESET_TOKEN_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/reset-token-validation`;

export const useUserStore = defineStore('user', {
	state: () => ({
		id: '',
		email: '',
	}),
	persist: {
		storage: sessionStorage,
	},
	actions: {
		async signupWithEmail(email, password) {
			const auth = useAuthStore();

			await axios.post(
				SIGNUP_WITH_EMAIL_URL,
				{ email, password },
				{ headers: HEADERS },
			);
			// Update store with email
			this.$patch({ email });
			// Log users in after signup and return that response
			return await auth.loginWithEmail(email, password);
		},
		async changePassword(email, password) {
			const auth = useAuthStore();
			await axios.put(
				CHANGE_PASSWORD_URL,
				{ email, password },
				{
					headers: {
						...HEADERS,
						Authorization: `Bearer ${auth.$state.tokens.accessToken.value}`,
					},
				},
			);
			return await auth.loginWithEmail(email, password);
		},

		async requestPasswordReset(email) {
			return await axios.post(
				REQUEST_PASSWORD_RESET_URL,
				{ email },
				{ headers: HEADERS },
			);
		},

		async resetPassword(password, token) {
			return await axios.post(
				PASSWORD_RESET_URL,
				{ password },
				{ headers: { ...HEADERS, Authorization: 'Bearer ' + token } },
			);
		},

		async validateResetPasswordToken(token) {
			return await axios.post(VALIDATE_PASSWORD_RESET_TOKEN_URL, {
				headers: {
					...HEADERS,
					Authorization: `Bearer ${token}`,
				},
			});
		},

		setEmail(email) {
			this.$patch({ email });
		},
	},
});
