<template>
	<div class="grid grid-cols-3 gap-4 relative overflow-y-scroll max-h-[40vh]">
		<p v-if="error" class="col-span-3 text-neutral-500 text-left">
			Error loading requests, please try again later
		</p>
		<p
			v-else-if="!error && !requests?.length"
			class="col-span-3 text-neutral-500 text-left"
		>
			No requests found
		</p>
		<div
			v-else
			class="col-span-3 grid grid-cols-subgrid justify-center sticky top-0 bg-neutral-50 p-2"
		>
			<h4 class="text-left m-0">Request Title</h4>
			<h4 class="text-left m-0">Location</h4>
			<h4 class="text-right m-0">Details</h4>
		</div>

		<RouterLink
			v-for="request in requests"
			:key="request.id"
			:to="`/data-request/${request.id}`"
			class="col-span-3 grid grid-cols-subgrid gap-4 p-2 border-solid border-neutral-300 border-2 rounded-sm [&>*]:text-sm [&>*]:md:text-med [&>*]:lg:text-lg text-neutral-950 hover:bg-neutral-100"
		>
			<p class="text-left">
				{{ request.title }}
			</p>

			<div class="text-left">
				<p v-for="(location, index) in request.locations" :key="location.id">
					{{ formatText(location) }}
					<span v-if="index !== request.locations.length - 1">&bull;</span>
				</p>
			</div>

			<div class="text-right">
				<a
					v-if="request.github_issue_url"
					:href="request.github_issue_url"
					target="_blank"
					rel="noopener noreferrer"
					@keydown.stop.enter=""
					@click.stop=""
				>
					<FontAwesomeIcon :icon="faLink" />
					Github
				</a>
			</div>
		</RouterLink>
	</div>
</template>

<script setup>
import { RouterLink } from 'vue-router';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faLink } from '@fortawesome/free-solid-svg-icons';
import { formatText } from './util';

const { requests } = defineProps({
	requests: Array,
	error: Boolean,
});
</script>
