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
		/** Searches performed during session. Will remove later and add to user's saved searches instead, once API support is completed */
		sessionSearches: [],
		/** Needed for `NEXT` / `BACK` functionality in data source id view */
		mostRecentSearchIds: [],
	}),
	persist: {
		storage: sessionStorage,
	},
	actions: {
		async search(params) {
			const response = await axios.get(SEARCH_URL, {
				params,
				headers: HEADERS_BASIC,
			});

			this.$patch({
				sessionSearches: [...this.sessionSearches, response.data],
			});

			return response.data;
		},
		async getDataSource(id) {
			return await axios.get(`${DATA_SOURCE_BY_ID_URL}/${id}`, {
				headers: HEADERS_BASIC,
			});
		},
		setMostRecentSearchIds(ids) {
			this.$patch({
				mostRecentSearchIds: ids,
			});
		},
	},
});
