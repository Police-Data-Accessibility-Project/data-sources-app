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
		path: "/",
		text: "Search",
		method: "route",
	},
	{
		href: "https://pdap.io/data",
		text: "Data",
		method: "href",
	},
	{
		href: "https://pdap.io/volunteer",
		text: "Volunteer",
		method: "href",
	},
	{
		href: "https://pdap.io/about",
		text: "About",
		method: "href",
	},
	{
		href: "https://pdap.io/donate",
		text: "Donate",
		method: "href",
	},
	{
		href: "https://docs.pdap.io/",
		text: "Docs",
		method: "href",
	},
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

main {
	min-height: calc(100% - 80px - 500px);
}
</style>
