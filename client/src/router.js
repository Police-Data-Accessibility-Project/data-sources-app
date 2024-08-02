import { createWebHistory, createRouter } from 'vue-router';
import { useAuthStore } from './stores/auth';
import { routes, handleHotUpdate } from 'vue-router/auto-routes';
import { refreshMetaTagsByRoute } from '@/util/routes.js';

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

router.beforeEach(async (to, _, next) => {
	// Update meta tags per route
	refreshMetaTagsByRoute(to);

	// redirect to login page if not logged in and trying to access a restricted page
	const auth = useAuthStore();
	if (to.meta.auth && !auth.userId) {
		auth.returnUrl = to.path;
		router.push('/login');
	}

	next();
});

export default router;
