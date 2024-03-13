<template>
	<AuthWrapper>
		<Header :logo-image-src="lockup" />
		<ErrorBoundary component="main">
			<router-view />
		</ErrorBoundary>
		<Footer :logo-image-src="acronym" />
	</AuthWrapper>
</template>

<script>
import { Footer, Header } from 'pdap-design-system';
import AuthWrapper from './components/AuthWrapper.vue';
import ErrorBoundary from './components/ErrorBoundary.vue';
import acronym from 'pdap-design-system/images/acronym.svg';
import lockup from 'pdap-design-system/images/lockup.svg';

import { links } from './util/links';

export default {
	name: 'App',
	components: {
		AuthWrapper,
		ErrorBoundary,
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
	min-height: calc(100vh - 80px - 500px);
}
</style>
