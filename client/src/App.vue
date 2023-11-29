<template>
	<AppHeader />
	<router-view></router-view>
	<AppFooter />
</template>

<script>
import AppHeader from './components/AppHeader.vue';
import AppFooter from './components/AppFooter.vue';

export default {
	name: 'App',
	components: {
		AppHeader,
		AppFooter,
	},
};
</script>

<style>
#app {
	margin: 0;
	padding: 1rem;
}

.logo {
	width: 50px;
	margin: 1rem;
	cursor: pointer;
}

/* Temporary code to override user agent styles
    TODO: remove when https://github.com/Police-Data-Accessibility-Project/design-system/issues/19 is addressed and released */
.pdap-button-primary[type='submit'] {
	background-color: rgba(var(--color-brand-gold) / var(--tw-bg-opacity));
}
</style>
