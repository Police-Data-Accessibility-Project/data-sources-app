import { createWebHistory, createRouter } from 'vue-router';
import { useAuthStore } from './stores/auth';

import ChangePassword from './pages/ChangePassword.vue';
import DataSourceStaticView from './pages/DataSourceStaticView.vue';
import LogIn from './pages/LogIn.vue';
import QuickSearchPage from './pages/QuickSearchPage.vue';
import ResetPassword from './pages/ResetPassword.vue';
import SearchResultPage from './pages/SearchResultPage.vue';
import NotFound from './pages/NotFound.vue';

export const PRIVATE_ROUTES = ['/change-password'];

const routes = [
	{ path: '/', component: QuickSearchPage, name: 'QuickSearchPage' },
	{
		path: '/search/:searchTerm/:location',
		component: SearchResultPage,
		name: 'SearchResultPage',
	},
	{
		path: '/data-sources/:id',
		component: DataSourceStaticView,
		name: 'DataSourceStaticView',
	},
	{
		path: '/login',
		component: LogIn,
		name: 'LogIn',
	},
	{
		path: '/change-password',
		component: ChangePassword,
		name: 'ChangePassword',
	},
	{
		path: '/reset-password/:token?',
		component: ResetPassword,
		name: 'ResetPassword',
	},
	{ path: '/:pathMatch(.*)*', name: 'not-found', component: NotFound },
];

const router = createRouter({
	history: createWebHistory(),
	routes,
});

router.beforeEach(async (to) => {
	// redirect to login page if not logged in and trying to access a restricted page
	const auth = useAuthStore();

	if (PRIVATE_ROUTES.includes(to.fullPath) && !auth.userId) {
		auth.returnUrl = to.path;
		router.push('/login');
	}
});

export default router;
