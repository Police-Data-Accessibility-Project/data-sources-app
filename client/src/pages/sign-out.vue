<template>
	<main class="flex items-center justify-center">
		<Spinner :size="48" :show="true" text="Signing out..." />
	</main>
</template>

<script setup>
import { Spinner } from 'pdap-design-system';
import { onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter, useRoute } from 'vue-router';

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

onMounted(async () => {
	await auth.logout();
	router.replace({ path: route.redirectedFrom ?? '/' });
});
</script>
