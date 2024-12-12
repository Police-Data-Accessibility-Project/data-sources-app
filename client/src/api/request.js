import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

const REQUESTS_BASE = `${import.meta.env.VITE_VUE_API_BASE_URL}/data-requests`;
const HEADERS_BASE = {
	'Content-Type': 'application/json',
};

export async function createRequest(data) {
	const auth = useAuthStore();
	const response = await axios.post(REQUESTS_BASE, data, {
		headers: {
			...HEADERS_BASE,
			authorization: `Bearer ${auth.$state.tokens.accessToken.value}`,
		},
	});

	return response.data;
}
