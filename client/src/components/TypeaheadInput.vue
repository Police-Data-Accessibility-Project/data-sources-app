<template>
	<div
		:id="wrapperId"
		data-test="typeahead-wrapper"
		class="pdap-typeahead"
		:class="{ 'pdap-typeahead-expanded': isListOpen }"
	>
		<slot name="label" />
		<input
			:id="id"
			ref="inputRef"
			v-model="input"
			data-test="typeahead-input"
			class="pdap-typeahead-input"
			type="text"
			:placeholder="placeholder"
			autocomplete="off"
			v-bind="$attrs"
			@input="onInput"
			@focus="onFocus"
			@blur="onBlur"
			@keydown.down.prevent="onArrowDown"
		/>
		<ul
			v-if="itemsToDisplay?.length && inputRef?.value"
			data-test="typeahead-list"
			class="pdap-typeahead-list"
		>
			<li
				v-for="(item, index) in itemsToDisplay"
				:key="index"
				class="pdap-typeahead-list-item"
				data-test="typeahead-list-item"
				role="button"
				tabindex="0"
				@click="selectItem(item)"
				@keydown.enter.prevent="selectItem(item)"
				@keydown.down.prevent="onArrowDown"
				@keydown.up.prevent="onArrowUp"
			>
				<!-- This implementation is extremely coupled to the PDAP /search functionality. If we want to use it elsewhere, we'll need to develop a slot and/or render function mechanism instead -->
				<!-- eslint-disable-next-line vue/no-v-html This data is coming from our API, so we can trust it-->
				<span v-html="boldMatchText(formatText(item))" />
				<span class="locale-type">
					{{ item.type }}
				</span>
				<span class="select">Select</span>
			</li>
		</ul>
		<ul
			v-else-if="typeof itemsToDisplay === 'undefined' && input.length > 1"
			class="pdap-typeahead-list"
			data-test="typeahead-list-not-found"
		>
			<li class="max-w-[unset]">
				<span>
					<strong>No results found.</strong> Please check your spelling and
					search for a place in the United States.
				</span>
			</li>
		</ul>
	</div>
</template>

<script setup>
import { ref, computed, watchEffect, onMounted, onUnmounted } from 'vue';
import statesToAbbreviations from '@/util/statesToAbbreviations';

/* Props and emits */
const props = defineProps({
	id: {
		type: String,
	},
	placeholder: {
		type: String,
		default: '',
	},
	items: {
		type: Array,
	},
});
const emit = defineEmits(['onInput', 'onFocus', 'onBlur', 'selectItem']);

/* Refs and reactive vars */
const inputRef = ref();
const input = ref('');

/* Computed vars */
const wrapperId = computed(() => `${props.id}_wrapper`);
const itemsToDisplay = computed(() => props.items);
const isListOpen = computed(
	() =>
		(itemsToDisplay.value?.length && inputRef?.value?.value) ||
		(typeof itemsToDisplay.value === 'undefined' && input.value.length > 1),
);

watchEffect(() => {
	if (inputRef.value) {
		setInputPositionForList();
	}
});

onMounted(() => {
	window.addEventListener('resize', setInputPositionForList);
});

onUnmounted(() => {
	window.removeEventListener('resize', setInputPositionForList);
});

/* Methods */
function setInputPositionForList() {
	document.documentElement.style.setProperty(
		'--typeaheadBottom',
		inputRef.value.offsetTop + inputRef.value.offsetHeight + 'px',
	);
	document.documentElement.style.setProperty(
		'--typeaheadListWidth',
		inputRef.value.offsetWidth + 'px',
	);
}
function onInput(e) {
	emit('onInput', e);
}
function onFocus(e) {
	if (Array.isArray(itemsToDisplay.value) && !itemsToDisplay.value.length) {
		clearInput();
		emit('selectItem', undefined);
	}

	emit('onFocus', e);
}
function onBlur(e) {
	emit('onBlur', e);
}

function onArrowDown() {
	const items = Array.from(
		document.getElementsByClassName('pdap-typeahead-list-item'),
	);

	const focusedIndex = items.indexOf(document.activeElement);

	if (focusedIndex === items.length - 1) return;

	if (focusedIndex === -1) {
		items[0].focus();
	} else {
		items[focusedIndex + 1].focus();
	}
}

function onArrowUp() {
	const items = Array.from(
		document.getElementsByClassName('pdap-typeahead-list-item'),
	);

	const focusedIndex = items.indexOf(document.activeElement);

	if (focusedIndex === 0) {
		inputRef.value.focus();
	} else {
		items[focusedIndex - 1].focus();
	}
}

function selectItem(item) {
	input.value = formatText(item);
	inputRef.value.blur();
	emit('selectItem', item);
}

function formatText(item) {
	switch (item.type) {
		case 'Locality':
			return `${item.display_name} ${item.county} ${statesToAbbreviations.get(item.state)}`;
		case 'County':
			return `${item.display_name} ${statesToAbbreviations.get(item.state)}`;
		case 'State':
		default:
			return item.display_name;
	}
}
function escapeRegExp(string) {
	return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
function boldMatchText(text) {
	const regexp = new RegExp(`(${escapeRegExp(input.value)})`, 'ig');
	return text.replace(regexp, '<strong>$1</strong>');
}
function clearInput() {
	input.value = '';
}
// function getInput() {
// 	return inputRef.value;
// }
// function focusInput() {
// 	inputRef.value.focus();
// 	onFocus();
// }
// function blurInput() {
// 	inputRef.value.blur();
// 	onBlur();
// }
</script>

<style>
.pdap-typeahead {
	@apply leading-normal w-full flex flex-col;
}

.pdap-typeahead label {
	@apply max-w-[max-content] text-lg py-1 font-medium;
}

.pdap-typeahead-input,
.pdap-typeahead-list {
	@apply bg-neutral-50 dark:bg-neutral-950 border border-neutral-500 border-solid p-2 text-neutral-950 dark:text-neutral-50;
}

.pdap-typeahead-input::placeholder {
	@apply text-neutral-600 text-lg;
}

.pdap-typeahead-input:focus,
.pdap-typeahead-input:focus-within,
.pdap-typeahead-input:focus-visible {
	@apply border-2 border-blue-light border-solid outline-none;
}

.pdap-typeahead-list {
	@apply absolute w-[var(--typeaheadListWidth)] top-[var(--typeaheadBottom)] z-50 overflow-scroll;
}

.pdap-typeahead-list-item {
	@apply mt-1 max-w-[unset] p-2 flex items-center gap-6 text-sm @md:text-lg;
}

.pdap-typeahead-list-item .locale-type {
	@apply border-solid border-2 border-neutral-700 dark:border-neutral-400 rounded-full text-neutral-700 dark:text-neutral-400 text-xs @md:text-sm px-2 py-1;
}

.pdap-typeahead-list-item .select {
	@apply ml-auto;
}

.pdap-typeahead-list-item:focus,
.pdap-typeahead-list-item:focus-visible,
.pdap-typeahead-list-item:focus-within,
.pdap-typeahead-list-item:hover {
	@apply outline-none text-neutral-950 dark:text-neutral-50 bg-neutral-300 dark:bg-neutral-700;
}
</style>
