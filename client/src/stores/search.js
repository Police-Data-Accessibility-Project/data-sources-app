import { useAuthStore } from '@/stores/auth';
import axios from 'axios';
import { defineStore } from 'pinia';
import _isEqual from 'lodash/isEqual';

// Constants
const HEADERS_BASE = {
	'Content-Type': 'application/json',
};
const HEADERS_BASIC = {
	...HEADERS_BASE,
	authorization: `Basic ${import.meta.env.VITE_ADMIN_API_KEY}`,
};
const SEARCH_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/search/search-location-and-record-type`;
const SEARCH_FOLLOW_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/search/follow`;
const CHECK_UNIQUE_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/check/unique-url`;

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
		async followSearch(params) {
			const auth = useAuthStore();

			return await axios.post(SEARCH_FOLLOW_URL, null, {
				params,
				headers: {
					...HEADERS_BASE,
					Authorization: `Bearer ${auth.$state.tokens.accessToken.value}`,
				},
			});
		},
		async getFollowedSearches() {
			const auth = useAuthStore();

			return await axios.get(SEARCH_FOLLOW_URL, {
				headers: {
					...HEADERS_BASE,
					Authorization: `Bearer ${auth.$state.tokens.accessToken.value}`,
				},
			});
		},
		async getFollowedSearch(params) {
			const auth = useAuthStore();

			if (!auth.isAuthenticated()) return false;

			try {
				const response = await axios.get(SEARCH_FOLLOW_URL, {
					headers: {
						...HEADERS_BASE,
						Authorization: `Bearer ${auth.$state.tokens.accessToken.value}`,
					},
				});

				return response.data.data.find((search) => {
					return _isEqual(search, params);
				});
			} catch (error) {
				return null;
			}
		},
		async deleteFollowedSearch(params) {
			const auth = useAuthStore();

			return await axios.delete(SEARCH_FOLLOW_URL, {
				params,
				headers: {
					...HEADERS_BASE,
					Authorization: `Bearer ${auth.$state.tokens.accessToken.value}`,
				},
			});
		},
		async findDuplicateURL(url) {
			const response = await axios.get(CHECK_UNIQUE_URL, {
				params: {
					url,
				},
				headers: HEADERS_BASIC,
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
