import { defineStore } from 'pinia';

export const useDataRequestsStore = defineStore('data-requests', {
	state: () => ({
		/** Searches performed during session. */
		cache: {},
		/** Previous route visited - useful for determining whether we are incrementing or decrementing pages in data request by id */
		previousDataRequestRoute: null,
	}),
	getters: {
		getDataRequestFromCache: (state) => (key) => {
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
		setDataRequestToCache(key, data, timestamp = new Date().getTime()) {
			this.$patch((state) => {
				state.cache[key] = {
					data,
					timestamp,
				};
			});
		},
		setPreviousDataRequestRoute(route) {
			this.$patch({
				previousDataSourceRoute: route,
			});
		},
	},
});
