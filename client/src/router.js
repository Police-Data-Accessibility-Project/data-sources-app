import { createWebHistory, createRouter } from 'vue-router';
import QuickSearchPage from '../src/pages/QuickSearchPage.vue';
import SearchResultPage from '../src/pages/SearchResultPage.vue';
import DataSourceStaticView from '../src/pages/DataSourceStaticView.vue';

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
