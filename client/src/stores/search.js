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
		/** Searches performed during session. Will remove later and add to user's saved searches instead, once API support is completed */
		sessionSearches: [],
	}),
	actions: {
		async search(params) {
			console.debug('search', { params });
			const response = await axios.get(SEARCH_URL, {
				params,
				headers: HEADERS_BASIC,
			});

			this.$patch({
				sessionSearches: [...this.sessionSearches, response.data],
			});

			return response.data;
		},
	},
});
