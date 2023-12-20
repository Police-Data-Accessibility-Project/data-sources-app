<template>
	<main class="p-4 md:p-0 md:pb-[60vh] md:mt-24">
		<QuickSearchForm />
	</main>
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
