import { defineStore } from 'pinia';

export const useSearchStore = defineStore('search', {
	state: () => ({
		/** Searches performed during session. */
		cache: {},
		/** Needed for `NEXT` / `BACK` functionality in data source id view */
		mostRecentSearchIds: [],
	}),
	persist: {
		storage: sessionStorage,
		pick: ['mostRecentSearchIds'],
	},
	getters: {
		getSearchFromCache: (state) => (key) => {
			if (!(key in state.cache)) {
				return null;
			}
			return state.cache[key];
		},
	},

	actions: {
		setMostRecentSearchIds(ids) {
			this.$patch({
				mostRecentSearchIds: ids,
			});
		},

		setSearchToCache(key, data, timestamp = new Date().getTime()) {
			this.$patch((state) => {
				// Use object notation for setting cache data
				state.cache[key] = {
					data,
					timestamp,
				};
			});
		},
	},
});
