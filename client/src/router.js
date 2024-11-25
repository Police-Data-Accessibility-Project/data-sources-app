import { createWebHistory, createRouter } from 'vue-router';
import { useAuthStore } from './stores/auth';
import { routes, handleHotUpdate } from 'vue-router/auto-routes';
import { refreshMetaTagsByRoute } from '@/util/routeHelpers.js';

const router = createRouter({
	history: createWebHistory(),
	routes,
	scrollBehavior(_to, _from, savedPosition) {
		if (savedPosition) return savedPosition;
		return { top: 0 };
	},
});

if (import.meta.hot && !import.meta.test) {
	handleHotUpdate(router);
}

router.beforeEach(async (to, from, next) => {
	// Update meta tags per route
	refreshMetaTagsByRoute(to);

	// redirect to login page if not logged in and trying to access a restricted page
	const auth = useAuthStore();

	if (to.path === '/sign-in') {
		auth.setRedirectTo(from);
	}

	if (to.meta.auth && !auth.isAuthenticated()) {
		auth.setRedirectTo(to);

		next({ path: '/sign-in', replace: true });
	} else {
		next();
	}
});

router.afterEach((to, from, failure) => {
	if (failure) console.error('router failure', { failure, to, from });
});

export default router;
