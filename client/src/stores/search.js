import axios from 'axios';
import { defineStore } from 'pinia';

// Constants
const HEADERS_BASIC = {
	authorization: `Basic ${import.meta.env.VITE_ADMIN_API_KEY}`,
	'Content-Type': 'application/json',
};
const SEARCH_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/search/search-location-and-record-type`;

export const useSearchStore = defineStore('search', {
	state: () => ({
		/** Searches performed during session. */
		sessionSearchResultsCache: {},
		/** Needed for `NEXT` / `BACK` functionality in data source id view */
		mostRecentSearchIds: [],
	}),
	persist: {
		storage: sessionStorage,
		pick: ['mostRecentSearchIds'],
	},
	actions: {
		async search(params) {
			const paramsStringified = JSON.stringify(params);
			const responseFromCache =
				this.sessionSearchResultsCache?.[paramsStringified];
			const cacheAge =
				new Date().getTime() - Number(responseFromCache?.cacheLastUpdated);

			let response;

			// TODO: THIS IS VERY BASIC: either implement own caching plugin OR JUST USE PINIA/COLADA (https://github.com/posva/pinia-colada?tab=readme-ov-file).
			if (responseFromCache && cacheAge < 1000 * 60 * 2) {
				// Cache for 2 minutes
				response = responseFromCache.data;
			} else {
				response = await axios.get(SEARCH_URL, {
					params,
					headers: HEADERS_BASIC,
				});
			}

			this.$patch({
				sessionSearchResultsCache: {
					...this.sessionSearchResultsCache,
					[paramsStringified]: {
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
	},
});
