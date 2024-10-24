<template>
	<div class="wrapper">
		<p class="text">
			{{ content }}
		</p>
		<Button class="button" intent="tertiary" type="button" @click="click">
			<FontAwesomeIcon :icon="faMinus" />
		</Button>
	</div>
</template>

<script setup>
import { Button } from 'pdap-design-system';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faMinus } from '@fortawesome/free-solid-svg-icons';
import { ref } from 'vue';

const show = ref(true);

const { onClick } = defineProps({
	content: {
		type: String,
	},
	onClick: {
		type: Function,
	},
});

function click() {
	show.value = false;
	onClick();
}
</script>

<style scoped>
.wrapper {
	@apply flex gap-4 w-full mb-2;
}

.button {
	@apply w-14 h-auto flex items-center justify-center [&>svg]:m-0 bg-neutral-50 dark:bg-neutral-950 text-neutral-950 dark:text-neutral-50 border border-neutral-500 border-solid;
}

.text {
	@apply bg-neutral-50 dark:bg-neutral-950 border border-neutral-500 border-solid p-2 text-neutral-950 dark:text-neutral-50 w-full max-w-full mb-0;
}
</style>
