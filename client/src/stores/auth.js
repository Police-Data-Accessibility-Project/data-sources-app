import axios from 'axios';
import { defineStore } from 'pinia';
import parseJwt from '../util/parseJwt';
import router from '../router';

const HEADERS = {
	headers: { 'Content-Type': 'application/json' },
};
const LOGIN_URL = `${import.meta.env.VITE_VUE_APP_BASE_URL}/login`;
const SIGNUP_URL = `${import.meta.env.VITE_VUE_APP_BASE_URL}/user`;
const REFRESH_SESSION_URL = `${import.meta.env.VITE_VUE_APP_BASE_URL}/refresh-session`;

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
			try {
				const response = await axios.post(
					LOGIN_URL,
					{ email, password },
					HEADERS,
				);

				this.parseTokenAndSetData(response);
				if (this.returnUrl) router.push(this.returnUrl);
			} catch (error) {
				throw new Error(error.message);
			}
		},

		logout(isAuthRoute) {
			this.$patch({
				userId: null,
				accessToken: { value: null, expires: Date.now() },
				returnUrl: null,
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
				throw new Error(error.message);
			}
		},

		// We may eventually want to move signup to a separate "User" store, but as of now it would be the only thing in that store, so we'll wait for the time being
		async signup(email, password) {
			try {
				await axios.post(
					SIGNUP_URL,
					{ email, password },
					{
						headers: { 'Content-Type': 'application/json' },
					},
				);

				// Log users in after signup and return that response
				return await this.login(email, password);
			} catch (error) {
				throw new Error(error.message);
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
