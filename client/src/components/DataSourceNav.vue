<template>
	<nav v-if="searchIds.length" class="self-start justify-self-start w-full">
		<RouterLink
			:to="`/data-source/${searchIds[previousIndex]}`"
			:class="{ disabled: typeof previousIndex !== 'number' }"
			replace
		>
			PREV
		</RouterLink>
		/
		<RouterLink
			:to="`/data-source/${searchIds[nextIndex]}`"
			:class="{ disabled: typeof nextIndex !== 'number' }"
			replace
		>
			NEXT
		</RouterLink>
	</nav>
</template>

<script setup>
defineProps({
	searchIds: Array,
	previousIndex: Number,
	nextIndex: Number,
});
</script>

<style scoped>
.disabled {
	@apply pointer-events-none opacity-50;
}
</style>
