<template>
	<AuthWrapper>
		<Header :logo-image-src="lockup" />
		<ErrorBoundary component="main">
			<router-view v-slot="{ Component }">
				<transition name="route-fade" mode="out-in">
					<component :is="Component" />
				</transition>
			</router-view>
		</ErrorBoundary>
		<Footer :logo-image-src="acronym" />
	</AuthWrapper>
</template>

<script>
import { ErrorBoundary, Footer, Header } from 'pdap-design-system';
import AuthWrapper from './components/AuthWrapper.vue';
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
	min-height: calc(100vh - 80px - 400px);
}

.route-fade-enter-active,
.route-fade-leave-active {
	transition: opacity 200ms ease-in;
}

.route-fade-enter-from,
.route-fade-leave-to {
	opacity: 0;
}
</style>
