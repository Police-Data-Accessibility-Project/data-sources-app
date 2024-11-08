import axios from 'axios';
import { defineStore } from 'pinia';

// Constants
const HEADERS_BASIC = {
	authorization: `Basic ${import.meta.env.VITE_ADMIN_API_KEY}`,
	'Content-Type': 'application/json',
};
const SEARCH_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/search/search-location-and-record-type`;
const DATA_SOURCE_BY_ID_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/data-sources`;

export const useSearchStore = defineStore('search', {
	state: () => ({
		/** Data sources fetched during session. */
		sessionDataSourceCache: {},
		/** Searches performed during session. */
		sessionSearchResultsCache: {},
		/** Strings searched via location typeahead, and an array of location suggestions returned */
		sessionLocationTypeaheadCache: {},
		/** Needed for `NEXT` / `BACK` functionality in data source id view */
		mostRecentSearchIds: [],
		/** Previous route visited - useful for determining whether we are incrementing or decrementing pages in data source by id */
		previousDataSourceRoute: null,
	}),
	persist: {
		storage: sessionStorage,
		pick: ['mostRecentSearchIds'],
	},
	getters: {
		getPreviousDataSourceRoute(state) {
			return state.previousDataSourceRoute;
		},
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
				response = await axios.get(`${DATA_SOURCE_BY_ID_URL}/${id}`, {
					headers: HEADERS_BASIC,
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

		upsertSessionLocationTypeaheadCache(updatedValues) {
			this.$patch({
				sessionLocationTypeaheadCache: {
					...this.sessionDataSourceCache,
					...updatedValues,
				},
			});
		},
	},
});
