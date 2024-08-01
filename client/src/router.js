import { createWebHistory, createRouter } from 'vue-router';
import { useAuthStore } from './stores/auth';
import { routes, handleHotUpdate } from 'vue-router/auto-routes';
import { refreshMetaTagsByRoute } from '@/util/routes.js';
import { PRIVATE_ROUTES } from '@/util/routes.js';

const router = createRouter({
	history: createWebHistory(),
	routes,
});

if (import.meta.hot) {
	handleHotUpdate(router);
}

router.beforeEach(async (to, _, next) => {
	// Update meta tags per route
	refreshMetaTagsByRoute(to);

	// redirect to login page if not logged in and trying to access a restricted page
	const auth = useAuthStore();
	if (PRIVATE_ROUTES.includes(to.fullPath) && !auth.userId) {
		auth.returnUrl = to.path;
		router.push('/login');
	}

	next();
});

export default router;
