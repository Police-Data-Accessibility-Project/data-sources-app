import { defineStore } from 'pinia';

export const useTypeaheadStore = defineStore('typeahead', {
	state: () => ({
		/** Searches performed during session. */
		cache: {
			agencies: {},
			locations: {},
		},
	}),
	getters: {
		getTypeaheadResultsFromCache: (state) => (type, key) => {
			return state.cache?.[type]?.[key] ?? null;
		},
	},

	actions: {
		setTypeaheadResultsToCache(type, key, data) {
			console.debug('setting results to cache');
			this.$patch((state) => {
				// Use object notation for setting cache data
				state.cache[type][key] = {
					data,
					timestamp: new Date().getTime(),
				};
			});
		},
	},
});
