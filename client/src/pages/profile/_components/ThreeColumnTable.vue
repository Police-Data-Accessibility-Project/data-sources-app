<template>
	<div
		class="grid grid-cols-3 gap-4 relative overflow-y-scroll max-h-[40vh]"
		v-bind="$attrs"
	>
		<TransitionGroup v-if="items" name="list">
			<RouterLink
				v-for="item in items"
				:key="item.to"
				:to="item.to"
				class="col-span-3 grid grid-cols-subgrid gap-4 p-2 border-solid border-neutral-300 border-2 rounded-sm [&>*]:text-sm [&>*]:md:text-med [&>*]:lg:text-lg text-neutral-950 hover:bg-neutral-100"
			>
				<slot name="left" :item="item" />
				<slot name="center" :item="item" />
				<slot name="right" :item="item" />
			</RouterLink>
		</TransitionGroup>
	</div>
</template>

<script setup>
defineProps({
	items: {
		type: Array,
		required: true,
	},
});
</script>

<style scoped>
.list-move,
.list-enter-active,
.list-leave-active {
	transition:
		opacity 500ms ease,
		transform 500ms ease;
}

.list-enter-from {
	opacity: 0;
	transform: translateX(-50%);
}

.list-leave-to {
	opacity: 0;
	transform: translateX(50%);
}
</style>
