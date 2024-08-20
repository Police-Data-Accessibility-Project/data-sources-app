import axios from 'axios';
import { defineStore } from 'pinia';
import parseJwt from '../util/parseJwt';
import router from '../router';
import { useUserStore } from './user';
import { useRoute } from 'vue-router';

const HEADERS = {
	'Content-Type': 'application/json',
};
const LOGIN_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/login`;
const REFRESH_SESSION_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/refresh-session`;

export const useAuthStore = defineStore('auth', {
	state: () => ({
		userId: null,
		tokens: {
			accessToken: {
				value: null,
				expires: Date.now(),
			},
			refreshToken: {
				value: null,
				expires: Date.now(),
			},
		},
		redirectTo: null,
	}),
	persist: true,
	actions: {
		async login(email, password) {
			const user = useUserStore();

			const response = await axios.post(
				LOGIN_URL,
				{ email, password },
				{
					headers: {
						...HEADERS,
						// TODO: API should require auth
						// authorization: `Basic ${import.meta.env.VITE_ADMIN_API_KEY}`,
					},
				},
			);

			// Update user store with email
			user.$patch({ email });

			this.parseTokenAndSetData(response);
		},

		async logout() {
			const user = useUserStore();
			const route = useRoute();

			this.$patch({
				userId: null,
				accessToken: { value: null, expires: Date.now() },
				redirectTo: null,
			});

			user.$patch({
				email: '',
			});

			if (route.redirectedFrom?.meta.auth) router.push({ path: '/sign-in' });
		},

		async refreshAccessToken() {
			if (!this.$state.userId) return;
			try {
				const response = await axios.post(
					REFRESH_SESSION_URL,
					{ session_token: this.$state.accessToken.value },
					{
						headers: {
							...HEADERS,
							authorization: `Basic ${this.refreshToken.value}`,
						},
					},
				);
				return this.parseTokenAndSetData(response);
			} catch (error) {
				throw new Error(error.response?.data?.message);
			}
		},

		parseTokenAndSetData(response) {
			const accessToken = response.data.access_token;
			const refreshToken = response.data.refresh_token;
			const accessTokenParsed = parseJwt(accessToken);
			const refreshTokenParsed = parseJwt(refreshToken);

			this.$patch({
				userId: accessTokenParsed.sub,
				tokens: {
					accessToken: {
						value: accessToken,
						expires: new Date(accessTokenParsed.exp * 1000).getTime(),
					},
					refreshToken: {
						value: refreshToken,
						expires: new Date(refreshTokenParsed.exp * 1000).getTime(),
					},
				},
			});
		},
	},
});
