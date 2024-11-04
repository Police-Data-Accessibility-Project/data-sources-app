<template>
	<main class="p-6 py-10 @container w-full overflow-scroll">
		<h1>We help people use police data for public oversight</h1>
		<p>What types of data are you looking for?</p>

		<SearchForm />
	</main>
</template>

<script setup>
import SearchForm from '@/components/SearchForm.vue';
</script>

<route>
	{
		alias: '/search',
	}
</route>
