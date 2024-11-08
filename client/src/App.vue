<template>
	<AuthWrapper>
		<Header :logo-image-src="lockup" />
		<ErrorBoundary component="main">
			<router-view v-slot="{ Component }">
				<transition name="route-fade" mode="out-in">
					<component :is="Component ?? 'main'">
						<Spinner
							class="absolute m-auto top-0 right-0 bottom-0 left-0"
							:show="!Component"
							:size="64"
							text="Loading..."
						/>
					</component>
				</transition>
			</router-view>
		</ErrorBoundary>
		<Footer :logo-image-src="acronym" />
	</AuthWrapper>
</template>

<script>
import { ErrorBoundary, Footer, Header, Spinner } from 'pdap-design-system';
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
		Spinner,
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
@tailwind components;

#app {
	margin: 0;
}

@layer components {
	.pdap-footer {
		@apply fixed bottom-0;
	}
}

main {
	@apply relative;
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
