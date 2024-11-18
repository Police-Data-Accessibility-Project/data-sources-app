import { useAuthStore } from '@/stores/auth';
import axios from 'axios';
import { defineStore } from 'pinia';

// Constants
const HEADERS_BASE = {
	authorization: `Basic ${import.meta.env.VITE_ADMIN_API_KEY}`,
	'Content-Type': 'application/json',
};
const DATA_SOURCES_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/data-sources`;

export const useDataSourceStore = defineStore('data-source', {
	state: () => ({
		/** Data sources fetched during session. */
		sessionDataSourceCache: {},
		/** Previous route visited - useful for determining whether we are incrementing or decrementing pages in data source by id */
		previousDataSourceRoute: null,
	}),
	persist: {
		storage: sessionStorage,
	},
	actions: {
		async createDataSource(data) {
			const auth = useAuthStore();
			return await axios.post(DATA_SOURCES_URL, data, {
				headers: {
					...HEADERS_BASE,
					authorization: `Bearer ${auth.$state.tokens.accessToken.value}`,
				},
			});
		},

		async getDataSource(id) {
			const responseFromCache = this.sessionDataSourceCache?.[id];
			const cacheAge =
				new Date().getTime() - Number(responseFromCache?.cacheLastUpdated);

			let response;

			// TODO: THIS IS VERY BASIC: either implement own caching plugin OR JUST USE PINIA/COLADA (https://github.com/posva/pinia-colada?tab=readme-ov-file).
			if (responseFromCache && cacheAge < 1000 * 60 * 2) {
				// Cache for 2 minutes
				response = responseFromCache.data;
			} else {
				response = await axios.get(`${DATA_SOURCES_URL}/${id}`, {
					headers: HEADERS_BASE,
				});
			}

			this.$patch({
				sessionDataSourceCache: {
					...this.sessionDataSourceCache,
					[id]: {
						data: response,
						cacheLastUpdated: new Date().getTime(),
					},
				},
			});

			return response;
		},

		setMostRecentSearchIds(ids) {
			this.$patch({
				mostRecentSearchIds: ids,
			});
		},

		setPreviousDataSourceRoute(route) {
			this.$patch({
				previousDataSourceRoute: route,
			});
		},
	},
});
