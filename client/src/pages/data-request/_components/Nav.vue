<template>
	<nav
		v-if="
			requestIds?.length &&
			[nextIndex, previousIndex].some((id) => Number(id) > -1)
		"
		class="self-start justify-self-start w-full"
	>
		<RouterLink
			:to="`/data-request/${requestIds[previousIndex]}`"
			:class="{ disabled: typeof previousIndex !== 'number' }"
			replace
			@mouseenter="setNavIs('decrement')"
		>
			PREV
		</RouterLink>
		/
		<RouterLink
			:to="`/data-request/${requestIds[nextIndex]}`"
			:class="{ disabled: typeof nextIndex !== 'number' }"
			replace
			@mouseenter="setNavIs('increment')"
		>
			NEXT
		</RouterLink>
	</nav>
</template>

<script setup>
defineProps({
	requestIds: Array,
	previousIndex: Number,
	nextIndex: Number,
	setNavIs: Function,
});
</script>

<style scoped>
.disabled {
	@apply pointer-events-none opacity-50;
}
</style>
