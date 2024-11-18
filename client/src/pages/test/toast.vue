<template>
	<main>
		<h1>Test toast messages</h1>
	</main>
</template>

<script setup>
import { toast } from 'vue3-toastify';

toast.success('Success! We did thing you wanted us to do.', {
	onClose: () => {
		toast.info('This is information', {
			onClose: () => {
				toast.warn('This is a warning', {
					onClose: () => {
						toast.error('This is an error');
					},
				});
			},
		});
	},
});
</script>
