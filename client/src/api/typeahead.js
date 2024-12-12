import axios from 'axios';

const TYPEAHEAD_BASE = `${import.meta.env.VITE_VUE_API_BASE_URL}/typeahead`;

import { useTypeaheadStore } from '@/stores/typeahead';
import { isCachedResponseValid } from '@/api/util';

/**
 * Returns a function that can be used to handle typeahead requests.
 *
 * @param {locations|agencies} type Record to search. Locations or agencies
 */
const makeTypeaheadHandler = (type) => async (e) => {
	const store = useTypeaheadStore();
	const key = e.target.value;

	const cached = store.getTypeaheadResultsFromCache(type, key);

	if (
		cached &&
		isCachedResponseValid({
			cacheTime: cached.timestamp,
			// Cache for 1 day. This data won't change often.
			intervalBeforeInvalidation: 1000 * 60 * 60 * 24,
		})
	) {
		return store.getTypeaheadResultsFromCache(type, key).data;
	}

	try {
		const response = await axios.get(`${TYPEAHEAD_BASE}/${type}`, {
			headers: {
				Authorization: import.meta.env.VITE_ADMIN_API_KEY,
			},
			params: {
				query: e.target.value,
			},
		});

		const suggestions = response.data.suggestions;

		store.setTypeaheadResultsToCache(type, key, suggestions);

		return suggestions;
	} catch (err) {
		console.error(err);
	}
};

export const getTypeaheadLocations = makeTypeaheadHandler('locations');
export const getTypeaheadAgencies = makeTypeaheadHandler('agencies');
