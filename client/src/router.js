import { createWebHistory, createRouter } from 'vue-router';
import QuickSearchPage from '../src/pages/QuickSearchPage';
import SearchResultPage from '../src/pages/SearchResultPage';

const routes = [
	{ path: '/', component: QuickSearchPage, name: 'QuickSearchPage' },
	{
		path: '/search/:searchTerm/:county',
		component: SearchResultPage,
		name: 'SearchResultPage',
	},
    { path: "*", redirect: "/" },
];

const router = createRouter({
	history: createWebHistory(),
	routes,
});

export default router;
