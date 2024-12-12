import axios from 'axios';
import { ENDPOINTS } from './constants';

const CHECK_BASE = `${import.meta.env.VITE_VUE_API_BASE_URL}/check`;
const HEADERS = {
	'Content-Type': 'application/json',
};
const HEADERS_BASIC = {
	...HEADERS,
	authorization: `Basic ${import.meta.env.VITE_ADMIN_API_KEY}`,
};

export async function findDuplicateURL(url) {
	const response = await axios.get(
		`${CHECK_BASE}/${ENDPOINTS.CHECK.UNIQUE_URL}`,
		{
			params: {
				url,
			},
			headers: HEADERS_BASIC,
		},
	);

	return response;
}
