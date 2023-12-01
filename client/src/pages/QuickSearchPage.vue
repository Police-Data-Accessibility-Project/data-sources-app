<template>
	<FlexContainer alignment="center" component="main" class="quick-search-card">
		<p class="quick-search-description">
			We maintain a catalog of public records about police, court, and jail systems across the
			United States.
		</p>
		<Form
			class="small"
			:schema="formSchema"
			@submit="handleSubmit"
			id="quick-search-form"
			name="quickSearchForm"
		>
			<Button type="submit">Search Data Sources</Button>
		</Form>
	</FlexContainer>
</template>

<script>
import { Button, FlexContainer, Form } from 'pdap-design-system';

export default {
	name: 'QuickSearchPage',
	components: {
		Button,
		FlexContainer,
		Form,
	},
	data: () => ({
		formSchema: [
			{
				id: 'search-term',
				name: 'searchTerm',
				label: 'What are you looking for?',
				type: 'text',
				placeholder: "Enter a keyword, type of public records, or 'all'",
				value: '',
				validators: {
					required: {
						message: 'Search term is required',
						value: true,
					},
				},
			},
			{
				id: 'location',
				name: 'location',
				label: 'From where?',
				type: 'text',
				placeholder: "Enter a state, county, municipality, or 'all'",
				value: '',
				validators: {
					required: {
						message: 'Location is required',
						value: true,
					},
				},
			},
		],
	}),
	methods: {
		async handleSubmit({ location, searchTerm }) {
			this.$router.push(`/search/${searchTerm}/${location}`);
		},
	},
};
</script>

<style scoped>
.quick-search-card {
	height: 100%;
	max-height: 75vh;
	max-width: 42rem;
}

.quick-search-description {
	display: flex;
	justify-content: center;
	text-align: center;
	width: 100%;
	margin: 0 auto 40px;
}
</style>

<style>
.quick-search-card .pdap-form {
	display: flex;
	flex-wrap: wrap;
	column-gap: 1rem;
}

.quick-search-card .pdap-button {
	flex: 0 0 100%;
	max-width: unset;
	margin-top: 32px;
}

.quick-search-card .pdap-input {
	flex-direction: column;
	row-gap: 0;
	flex: 1 0 45%;
}
.quick-search-card .pdap-input-label {
	justify-content: flex-start;
}
</style>
