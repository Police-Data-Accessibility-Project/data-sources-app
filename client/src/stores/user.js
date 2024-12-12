import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
	state: () => ({
		id: '',
		email: '',
	}),
	persist: {
		storage: sessionStorage,
	},
	actions: {
		setEmail(email) {
			this.$patch({ email });
		},
	},
});
