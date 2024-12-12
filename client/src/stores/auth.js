import { defineStore } from 'pinia';
import parseJwt from '@/util/parseJwt';
import { useUserStore } from './user';

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
