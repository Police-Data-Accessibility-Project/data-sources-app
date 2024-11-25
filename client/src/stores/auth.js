import axios from 'axios';
import { defineStore } from 'pinia';
import parseJwt from '@/util/parseJwt';
import { useUserStore } from './user';

const HEADERS = {
	'Content-Type': 'application/json',
};
const LOGIN_WITH_EMAIL_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/login`;
const LOGIN_WITH_GITHUB_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/auth/login-with-github`;
const LINK_WITH_GITHUB_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/auth/link-to-github`;
const REFRESH_SESSION_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/refresh-session`;
const START_OAUTH_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/auth/oauth`;

export const useAuthStore = defineStore('auth', {
	state: () => ({
		tokens: {
			accessToken: {
				value: null,
				expires: new Date().getTime(),
			},
			refreshToken: {
				value: null,
				expires: new Date().getTime(),
			},
		},
		redirectTo: null,
	}),
	persist: {
		storage: localStorage,
		pick: ['tokens'],
	},
	getters: {
		isAuthenticated: (state) => {
			const user = useUserStore();

			return (time = new Date().getTime()) =>
				!!state.$state.tokens.accessToken.value &&
				state.$state.tokens.accessToken.expires > time &&
				!!user.$state.id;
		},
	},
	actions: {
		async loginWithEmail(email, password) {
			const response = await axios.post(
				LOGIN_WITH_EMAIL_URL,
				{ email, password },
				{
					headers: {
						...HEADERS,
						// TODO: API should require auth
						// authorization: `Basic ${import.meta.env.VITE_ADMIN_API_KEY}`,
					},
				},
			);

			this.parseTokensAndSetData(response);
		},

		async beginOAuthLogin(redirectPath = '/sign-in') {
			const redirectTo = encodeURI(
				`${START_OAUTH_URL}?redirect_url=${import.meta.env.VITE_VUE_APP_BASE_URL}${redirectPath}`,
			);

			window.location.href = redirectTo;
		},

		async loginWithGithub(gh_access_token) {
			const response = await axios.post(
				LOGIN_WITH_GITHUB_URL,
				{ gh_access_token },
				{
					headers: {
						...HEADERS,
					},
				},
			);

			this.parseTokensAndSetData(response);
			return true;
		},

		async linkAccountWithGithub(gh_access_token) {
			const { email: user_email } = useUserStore();

			return await axios.post(
				LINK_WITH_GITHUB_URL,
				{ gh_access_token, user_email },
				{
					headers: {
						...HEADERS,
						// authorization: `Bearer ${this.$state.tokens.accessToken.value}`,
					},
				},
			);
		},

		async logout() {
			const user = useUserStore();

			this.$reset();
			user.$reset();
		},

		async refreshAccessToken() {
			const user = useUserStore();

			if (!user.$state.id) return;
			try {
				const response = await axios.post(
					REFRESH_SESSION_URL,
					{ refresh_token: this.$state.tokens.refreshToken.value },
					{
						headers: {
							...HEADERS,
							authorization: `Bearer ${this.$state.tokens.accessToken.value}`,
						},
					},
				);
				return this.parseTokensAndSetData(response);
			} catch (error) {
				console.error(error);
				throw new Error(error.response?.data?.message);
			}
		},

		parseTokensAndSetData(response) {
			const user = useUserStore();

			const accessToken = response.data.access_token;
			const refreshToken = response.data.refresh_token;
			const accessTokenParsed = parseJwt(accessToken);
			const refreshTokenParsed = parseJwt(refreshToken);

			this.$patch({
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

			user.$patch({
				id: accessTokenParsed.sub.id,
				email: accessTokenParsed.sub.user_email,
			});
		},

		setRedirectTo(route) {
			this.$patch({
				redirectTo: route,
			});
		},
	},
});
