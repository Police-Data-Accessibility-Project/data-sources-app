import { useAuthStore } from '@/stores/auth';
import axios from 'axios';
import { defineStore } from 'pinia';

// Constants
const HEADERS_BASE = {
	authorization: `Basic ${import.meta.env.VITE_ADMIN_API_KEY}`,
	'Content-Type': 'application/json',
};
const REQUESTS_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/data-requests`;

export const useRequestStore = defineStore('request', {
	state: () => ({}),
	// persist: {
	// 	storage: sessionStorage,
	// },
	actions: {
		async createRequest(data) {
			const { tokens } = useAuthStore();
			const response = await axios.post(REQUESTS_URL, data, {
				headers: {
					...HEADERS_BASE,
					authorization: `Bearer ${tokens.accessToken.value}`,
				},
			});

			return response.data;
		},
	},
});
