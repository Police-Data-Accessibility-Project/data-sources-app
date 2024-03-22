import axios from 'axios';
import { defineStore } from 'pinia';
import parseJwt from '../util/parseJwt';
import router from '../router';
import { useUserStore } from './user';

const HEADERS = {
	headers: { 'Content-Type': 'application/json' },
};
const LOGIN_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/login`;
const REFRESH_SESSION_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/refresh-session`;

export const useAuthStore = defineStore('auth', {
	state: () => ({
		userId: null,
		accessToken: {
			value: null,
			expires: Date.now(),
		},
		returnUrl: null,
	}),
	persist: true,
	actions: {
		async login(email, password) {
			const user = useUserStore();

			const response = await axios.post(
				LOGIN_URL,
				{ email, password },
				HEADERS,
			);

			// Update user store with email
			user.$patch({ email });

			this.parseTokenAndSetData(response);
			if (this.returnUrl) router.push(this.returnUrl);
		},

		logout(isAuthRoute) {
			const user = useUserStore();

			this.$patch({
				userId: null,
				accessToken: { value: null, expires: Date.now() },
				returnUrl: null,
			});

			user.$patch({
				email: '',
			});
			if (isAuthRoute) router.push('/login');
		},

		async refreshAccessToken() {
			if (!this.$state.userId) return;
			try {
				const response = await axios.post(
					REFRESH_SESSION_URL,
					{ session_token: this.$state.accessToken.value },
					HEADERS,
				);
				return this.parseTokenAndSetData(response);
			} catch (error) {
				throw new Error(error.response?.data?.message);
			}
		},

		parseTokenAndSetData(response) {
			const token = response.data.data;
			const tokenParsed = parseJwt(token);

			this.$patch({
				userId: tokenParsed.sub,
				accessToken: {
					value: token,
					expires: new Date(tokenParsed.exp * 1000).getTime(),
				},
			});
		},
	},
});
