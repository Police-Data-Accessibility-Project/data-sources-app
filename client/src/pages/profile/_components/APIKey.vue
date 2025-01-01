<template>
	<div
		class="p-4 rounded-lg border border-neutral-600 shadow-xs shadow-neutral-800 max-w-max"
	>
		<div>
			<div class="flex justify-between items-center mb-2">
				<h5 class="flex gap-2 items-center not-italic text-lg mb-4">
					<FontAwesomeIcon :icon="faClock" class="w-4 h-4" />
					Your new API Key
				</h5>
				<Button
					v-if="onDismiss"
					class="h-max p-0 hover:brightness-95 max-w-max py-1 px-2"
					intent="tertiary"
					@click="onDismiss"
				>
					<FontAwesomeIcon :icon="faClose" />
				</Button>
			</div>
			<div class="relative">
				<Button
					class="h-max p-0 hover:brightness-95 text-left max-w-full rounded"
					intent="tertiary"
					@click="copyToClipboard"
				>
					<code
						class="flex justify-between items-center w-full p-2 bg-neutral-200 border border-neutral-500 rounded font-mono text-sm overflow-x-auto shadow-[inset_0_2px_4px_rgba(0,0,0,0.1)]"
					>
						<span class="break-all">
							{{ apiKey }}
						</span>
						<FontAwesomeIcon
							:icon="copied ? faCircleCheck : faCopy"
							class="ml-4"
							:class="{ 'success-icon': copied }"
						/>
					</code>
				</Button>
			</div>
		</div>
		<div
			class="text-sm flex flex-col justify-center max-w-full mt-2 bg-goldneutral-100 text-goldneutral-900 p-2 rounded"
		>
			<p class="flex items-center gap-1 max-w-full">
				<FontAwesomeIcon :icon="faExclamationCircle" class="w-4 h-4 mr-1" />
				<span class="block">
					This key will not be displayed again. Please store it in a secure
					location. <br />
					All previously generated keys have been invalidated.
				</span>
			</p>
		</div>
	</div>
</template>

<script setup>
import { ref } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import {
	faCopy,
	faCircleCheck,
	faClock,
} from '@fortawesome/free-regular-svg-icons';
import {
	faExclamationCircle,
	faClose,
} from '@fortawesome/free-solid-svg-icons';
import { Button } from 'pdap-design-system';

const props = defineProps({
	apiKey: {
		type: String,
		required: true,
	},
	onDismiss: Function,
});

const copied = ref(false);

const copyToClipboard = async () => {
	try {
		await navigator.clipboard.writeText(props.apiKey);
		copied.value = true;
		setTimeout(() => {
			copied.value = false;
		}, 2000); // Reset after 2 seconds
	} catch (err) {
		console.error('Failed to copy text: ', err);
	}
};
</script>

<style scoped>
.success-icon {
	color: #4caf50; /* Green color */
	animation: popIn 0.3s ease-out;
}

@keyframes popIn {
	0% {
		transform: scale(1);
	}
	50% {
		transform: scale(1.2);
	}
	100% {
		transform: scale(1);
	}
}
</style>
