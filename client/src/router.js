import { createWebHistory, createRouter } from 'vue-router';
import QuickSearchPage from '../src/pages/QuickSearchPage.vue';
import SearchResultPage from '../src/pages/SearchResultPage.vue';
import DataSourceStaticView from '../src/pages/DataSourceStaticView.vue';
import ChangePassword from './pages/ChangePassword.vue';
import LogIn from './pages/LogIn.vue';
import { useAuthStore } from './stores/auth';

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
