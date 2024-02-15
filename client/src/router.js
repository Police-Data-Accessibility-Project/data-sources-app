import { createWebHistory, createRouter } from 'vue-router';
import QuickSearchPage from '../src/pages/QuickSearchPage.vue';
import SearchResultPage from '../src/pages/SearchResultPage.vue';
import DataSourceStaticView from '../src/pages/DataSourceStaticView.vue';
import ChangePassword from './pages/ChangePassword.vue';
import LogIn from './pages/LogIn.vue';

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

export default router;
