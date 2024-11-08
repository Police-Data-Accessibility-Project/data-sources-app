<template>
	<main class="pdap-flex-container mx-auto max-w-2xl">
		<h1>Your account is now active</h1>
		<p data-test="success-subheading">Enjoy the data sources app.</p>

		<RouterLink class="pdap-button-secondary mt-6" :to="{ path: '/' }">
			Search data sources
		</RouterLink>

		<RouterLink class="pdap-button-secondary mt-6" :to="{ path: '/profile' }">
			Go to your profile
		</RouterLink>
	</main>
</template>

<script>
// Navigation guard via data loader
import { NavigationResult } from 'unplugin-vue-router/data-loaders';
import { defineBasicLoader } from 'unplugin-vue-router/data-loaders/basic';
import { useUserStore } from '@/stores/user';

const user = useUserStore();

export const useDataSourceData = defineBasicLoader(
	'/sign-up/success',
	async () => {
		if (!user.id)
			return new NavigationResult({ path: '/sign-up', replace: true });
	},
);
</script>
