import { defineStore } from 'pinia';

export const useDataSourceStore = defineStore('data-source', {
	state: () => ({
		/** Previous route visited - useful for determining whether we are incrementing or decrementing pages in data source by id */
		previousDataSourceRoute: null,
		/** Cache by ID -- useful for avoiding unnecessary API calls */
		cache: {},
	}),
	persist: {
		storage: sessionStorage,
	},
	getters: {
		getDataSourceFromCache: (state) => (key) => {
			if (!(key in state.cache)) {
				return null;
			}
			return state.cache[key];
		},
	},
	actions: {
		clearCache() {
			this.$patch((state) => {
				state.cache = {};
			});
		},

		setPreviousDataSourceRoute(route) {
			this.$patch({
				previousDataSourceRoute: route,
			});
		},

		setDataSourceToCache(key, data) {
			this.$patch((state) => {
				state.cache[key] = {
					data,
					timestamp: new Date().getTime(),
				};
			});
		},
	},
});
