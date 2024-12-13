import { createWebHistory, createRouter } from 'vue-router';
import { useAuthStore } from './stores/auth';
import { routes, handleHotUpdate } from 'vue-router/auto-routes';
import { refreshMetaTagsByRoute } from '@/util/routeHelpers.js';
import { toast } from 'vue3-toastify';

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

	if (to.path === '/sign-in' && from.meta.auth) {
		delete from.query;
		delete from.hash;

		auth.$patch({ redirectTo: from });
		next();
	}

	if (to.meta.auth && !auth.isAuthenticated()) {
		delete to.query;
		delete to.hash;

		auth.$patch({ redirectTo: to });

		next({ path: '/sign-in', replace: true });
	} else {
		next();
	}
});

router.afterEach((to, from, failure) => {
	if (failure) console.error('router failure', { failure, to, from });
});

router.onError((error) => {
	console.error('router error', error);
	toast.error('An error occurred. Please try again later.', {
		autoClose: false,
	});
});

export default router;
