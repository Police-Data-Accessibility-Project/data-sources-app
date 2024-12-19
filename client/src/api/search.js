import axios from 'axios';
import { ENDPOINTS } from './constants';
import { useAuthStore } from '@/stores/auth';
import { useSearchStore } from '@/stores/search';
import { isCachedResponseValid } from '@/api/util';

const SEARCH_BASE = `${import.meta.env.VITE_VUE_API_BASE_URL}/search`;
const HEADERS = {
	'Content-Type': 'application/json',
};
const HEADERS_BASIC = {
	...HEADERS,
	authorization: `Basic ${import.meta.env.VITE_ADMIN_API_KEY}`,
};

export async function search(params) {
	const searchStore = useSearchStore();
	const cached = searchStore.getSearchFromCache(JSON.stringify(params));

	if (
		cached &&
		isCachedResponseValid({
			cacheTime: cached.timestamp,
			// Cache for 5 minutes
			intervalBeforeInvalidation: 1000 * 60 * 5,
		})
	) {
		return cached.data;
	}

	const response = await axios.get(
		`${SEARCH_BASE}/${ENDPOINTS.SEARCH.RESULTS}`,
		{
			params,
			headers: HEADERS_BASIC,
		},
	);

	searchStore.setSearchToCache(JSON.stringify(params), response);

	return response;
}

export async function followSearch(location_id) {
	const auth = useAuthStore();

	return await axios.post(`${SEARCH_BASE}/${ENDPOINTS.SEARCH.FOLLOW}`, null, {
		params: {
			location_id,
		},
		headers: {
			...HEADERS,
			Authorization: `Bearer ${auth.$state.tokens.accessToken.value}`,
		},
	});
}
export async function getFollowedSearches() {
	const auth = useAuthStore();

	const response = await axios.get(
		`${SEARCH_BASE}/${ENDPOINTS.SEARCH.FOLLOW}`,
		{
			headers: {
				...HEADERS,
				Authorization: `Bearer ${auth.$state.tokens.accessToken.value}`,
			},
		},
	);

	response.data.data.map((followed) => {
		Object.entries(followed).forEach(([key, value]) => {
			if (!value) {
				delete followed[key];
			}
		});
		return followed;
	});

	return response;
}
export async function getFollowedSearch(location_id) {
	const auth = useAuthStore();

	if (!auth.isAuthenticated()) return false;

	try {
		const response = await getFollowedSearches();

		return response.data.data.find(
			({ id: followed_id }) => Number(followed_id) === Number(location_id),
		);
	} catch (error) {
		return null;
	}
}
export async function deleteFollowedSearch(location_id) {
	const auth = useAuthStore();

	return await axios.delete(`${SEARCH_BASE}/${ENDPOINTS.SEARCH.FOLLOW}`, {
		params: {
			location_id,
		},
		headers: {
			...HEADERS,
			Authorization: `Bearer ${auth.$state.tokens.accessToken.value}`,
		},
	});
}
