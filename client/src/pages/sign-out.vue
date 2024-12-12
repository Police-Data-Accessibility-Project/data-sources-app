<template>
	<main class="flex items-center justify-center">
		<Spinner :size="48" :show="true" text="Signing out..." />
	</main>
</template>

<script setup>
import { Spinner } from 'pdap-design-system';
import { onMounted } from 'vue';
import { signOut } from '@/api/auth';

onMounted(async () => {
	await signOut();
});
</script>
