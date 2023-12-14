<template>
	<FlexContainer
		component="section"
		class="h-auto p-0 mt-12"
		>
		<h2 class="mt-0">Search our database</h2>
			<p class="pb-4 md:pb-8">
				If you have a question to answer, we may already know about helpful data in your area.
				<RouterLink to="/data">Learn more about the data here.</RouterLink>
			</p>
	</FlexContainer>
	<QuickSearchForm />
</template>

<script>
import { GridContainer, QuickSearchForm } from "pdap-design-system";

export default {
	name: "QuickSearchPage",
	components: {
    QuickSearchForm,
    GridContainer
},
};
</script>
