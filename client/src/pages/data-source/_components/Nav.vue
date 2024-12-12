<template>
	<nav
		v-if="
			searchIds?.length &&
			[nextIndex, previousIndex].some((id) => typeof id === 'number' && id > -1)
		"
		class="self-start justify-self-start w-full"
	>
		<RouterLink
			:to="`/data-source/${searchIds[previousIndex]}`"
			:class="{ disabled: typeof previousIndex !== 'number' }"
			replace
			@mouseenter="setNavIs('decrement')"
		>
			PREV
		</RouterLink>
		/
		<RouterLink
			:to="`/data-source/${searchIds[nextIndex]}`"
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
	searchIds: Array,
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
