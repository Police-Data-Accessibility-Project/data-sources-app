<!-- <template>
	<div> -->
<!-- Here we will render requests -->
<!-- This div should be a grid container with three columns -->
<!-- First we will render a row of headings: (Request title | Location | Details) 
      Request title justified left, location center, details right -->
<!-- We will take an array of objects and loop through them 
     Each object will have the following properties: 
     id: number
     title: string
     location: array of objects with the following properties:
     {
        "type": "string",
        "state_iso": "string",
        "county_fips": "string",
        "locality_name": "string",
        "id": 0
      }
      github_issue_url: string

      Each rendered row should be wrapped in a router link to `/data-request/{id}`

      Each row should use sub-grid to align columns with parent and each other

      In the first column, we render the title.

      In the second column, we loop through the location array and render each location.

      In the third column, we render a nested anchor tag that leads to github_issue_url. It should contain a font awesome link icon as well as the text "Github"
     -->
<!-- </div>
</template> -->

<template>
	<div class="grid grid-cols-3 gap-4 relative overflow-y-scroll max-h-[40vh]">
		<div
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
					{{ location.locality_name }}, {{ location.state_iso }}
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

const { requests } = defineProps({
	requests: Array,
});
</script>
