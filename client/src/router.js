import { createWebHistory, createRouter } from 'vue-router';
import QuickSearchPage from '../src/pages/QuickSearchPage';
import SearchResultPage from '../src/pages/SearchResultPage';

const routes = [
	{ path: '/', component: QuickSearchPage, name: 'QuickSearchPage' },
	{
		path: '/search/:searchTerm/:location',
		component: SearchResultPage,
		name: 'SearchResultPage',
	},
];

const router = createRouter({
	history: createWebHistory(),
	routes,
});

export default router;
