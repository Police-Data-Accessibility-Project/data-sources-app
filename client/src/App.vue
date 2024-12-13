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
		<Footer
			:logo-image-src="acronym"
			:fundraising-data="{ raised: 0, goal: 0 }"
		/>
	</AuthWrapper>
</template>

<script setup>
import { ErrorBoundary, Footer, Header, Spinner } from 'pdap-design-system';
import AuthWrapper from './components/AuthWrapper.vue';
import acronym from 'pdap-design-system/images/acronym.svg';
import lockup from 'pdap-design-system/images/lockup.svg';

import { NAV_LINKS, FOOTER_LINKS } from '@/util/constants';
import { provide } from 'vue';

provide('navLinks', NAV_LINKS);
provide('footerLinks', FOOTER_LINKS);
</script>

<style>
@tailwind components;

#app {
	margin: 0;
}

main {
	@apply relative;
	min-height: calc(100vh - 200px);
}

.route-fade-enter-active,
.route-fade-leave-active {
	transition: opacity 200ms ease-in;
}

.route-fade-enter-from,
.route-fade-leave-to {
	opacity: 0;
}

.pdap-toast-container {
	top: 120px;
}

:root {
	--toastify-color-light: rgb(255 253 253);
	--toastify-color-dark: rgb(26 26 26);
	--toastify-color-info: #44799d;
	--toastify-color-success: #49934b;
	--toastify-color-warning: rgb(184 138 42);
	--toastify-color-error: #f15d4c;
	--toastify-color-transparent: rgba(255, 255, 255, 0.7);

	--toastify-icon-color-info: var(--toastify-color-info);
	--toastify-icon-color-success: var(--toastify-color-success);
	--toastify-icon-color-warning: var(--toastify-color-warning);
	--toastify-icon-color-error: var(--toastify-color-error);

	--toastify-toast-width: auto;
	--toastify-toast-background: #fff;
	--toastify-toast-min-height: 64px;
	--toastify-toast-max-height: 800px;
	--toastify-font-family: inherit;
	--toastify-z-index: 9999;

	--toastify-text-color-light: rgb(26 26 26);
	--toastify-text-color-dark: rgb(255 253 253);
}

@media (prefers-color-scheme: dark) {
	:root {
		--toastify-color-info: #67baf2;
		--toastify-color-success: #51eb56;
		--toastify-color-warning: rgb(184 138 42);
		--toastify-color-error: #b53b2d;
	}
}
</style>
