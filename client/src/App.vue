<template>
	<Header :logo-image-src="lockup" />
	<router-view />
	<Footer :logo-image-src="acronym" />
</template>

<script>
import { Footer, Header } from "pdap-design-system";
import acronym from "pdap-design-system/images/acronym.svg";
import lockup from "pdap-design-system/images/lockup.svg";

const links = [
	{
		href: "https://airtable.com/shrbFfWk6fjzGnNsk",
		text: "Request data",
		method: "href",
	},
	{
		href: "https://airtable.com/shrJafakrcmTxHU2i",
		text: "Submit a Data Source",
		method: "href",
	},
	{ href: "https://docs.pdap.io/", text: "Docs", method: "href" },
];

export default {
	name: "App",
	components: {
		Header,
		Footer,
	},
	provide: {
		navLinks: [...links],
		footerLinks: [...links],
	},
	data() {
		return {
			acronym,
			lockup,
		};
	},
};
</script>

<style>
#app {
	margin: 0;
}
</style>
