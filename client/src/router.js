import { createWebHistory, createRouter } from 'vue-router';
import QuickSearchPage from '../src/pages/QuickSearchPage';
import SearchResultPage from '../src/pages/SearchResultPage';
import DataSourceStaticView from '../src/pages/DataSourceStaticView';

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
];

const router = createRouter({
	history: createWebHistory(),
	routes,
});

export default router;
