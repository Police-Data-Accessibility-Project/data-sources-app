<template>
	<Header :logo-image-src="lockup" />
	<router-view></router-view>
	<Footer :logo-image-src="acronym" />
</template>

<script>
import { Footer, Header } from 'pdap-design-system';
import acronym from 'pdap-design-system/images/acronym.svg';
import lockup from 'pdap-design-system/images/lockup.svg';

const links = [
	{ href: 'https://airtable.com/shrbFfWk6fjzGnNsk', text: 'Request data', method: 'href' },
	{
		href: 'https://airtable.com/shrJafakrcmTxHU2i',
		text: 'Submit a Data Source',
		method: 'href',
	},
	{ href: 'https://docs.pdap.io/', text: 'Docs', method: 'href' },
];

export default {
	name: 'App',
	components: {
		Header,
		Footer,
	},
	data() {
		return {
			acronym,
			lockup,
		};
	},
	provide: {
		navLinks: [...links],
		footerLinks: [...links],
	},
};
</script>

<style>
#app {
	margin: 0;
}

main,
main.pdap-flex-container,
main.pdap-grid-container {
	/* header height is generally 80px, footer height is (at tallest, on smaller mob devices) 600px. 
	This will prevent content from taking up too much space, 
	while also ensuring that the viewport is always full. Adding support 
	to unset 100% height when flex or grid container passed as main  */
	min-height: calc(100vh - 80px - 600px);
	height: auto;
}

.pdap-footer .pdap-footer-social-link {
	color: rgba(var(--color-neutral-950) / var(--tw-text-opacity));
}

/* TODO: Add this to future design system patch as well and remove from here */
.pdap-footer p,
.pdap-footer ul,
.pdap-footer li,
.pdap-footer .pdap-footer-social-link {
	max-width: unset;
}

/* Temporary code to override user agent styles
    TODO: remove when https://github.com/Police-Data-Accessibility-Project/design-system/issues/19 is addressed and released */
.pdap-button-primary[type='submit'] {
	background-color: rgba(var(--color-brand-gold) / var(--tw-bg-opacity));
}
</style>
