import { createWebHistory, createRouter } from 'vue-router';
import { useAuthStore } from './stores/auth';

import ChangePassword from './pages/ChangePassword.vue';
import DataSourceStaticView from './pages/DataSourceStaticView.vue';
import LogIn from './pages/LogIn.vue';
import QuickSearchPage from './pages/QuickSearchPage.vue';
import ResetPassword from './pages/ResetPassword.vue';
import SearchResultPage from './pages/SearchResultPage.vue';
import NotFound from './pages/NotFound.vue';

import acronym from 'pdap-design-system/images/acronym.svg';

const routes = [
	{
		path: '/',
		component: QuickSearchPage,
		name: 'QuickSearchPage',
		// Use meta property on route to override meta tag defaults
		// meta: { title: 'Police Data Accessibility Project - Search', metaTags: [{ property: 'og:title', title: 'Police Data Accessibility Project - Search' }] },
	},
	{
		path: '/search',
		component: SearchResultPage,
		name: 'SearchResultPage',
	},
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

// Util
export const PRIVATE_ROUTES = ['/change-password'];

const DEFAULT_META_TAGS = new Map([
	[
		'description',
		'Data and tools for answering questions about any police system in the United States',
	],
	['title', 'Police Data Accessibility Project'],
	[
		'og:description',
		'Data and tools for answering questions about any police system in the United States',
	],
	['og:title', 'Police Data Accessibility Project'],
	['og:type', 'website'],
	['og:site_name', 'PDAP'],
	['og:image', acronym],
]);
const META_PROPERTIES = [...DEFAULT_META_TAGS.keys(), 'og:url'];

/**
 * Adds meta tags by route
 * @param {RouteLocationNormalized} to Vue router route location
 */
function refreshMetaTagsByRoute(to) {
	// Get nearest matched route that has title / meta tag overrides
	const nearestRouteWithTitle = [...to.matched]
		.reverse()
		.find((route) => route?.meta?.title);

	const nearestRouteWithMeta = [...to.matched]
		.reverse()
		.find((route) => route?.meta?.metaTags);

	// Update document title
	document.title =
		nearestRouteWithTitle?.meta?.title ?? DEFAULT_META_TAGS.get('title');

	// Update meta tags
	Array.from(document.querySelectorAll('[data-controlled-meta]')).forEach(
		(el) => el.parentNode.removeChild(el),
	);

	META_PROPERTIES.filter((prop) => prop !== 'title')
		.map((prop) => {
			const tagInRouteMetaData = nearestRouteWithMeta?.meta?.metaTags?.find(
				(tag) => tag.property === prop,
			);

			let content;
			switch (true) {
				case prop === 'og:url':
					content = `${import.meta.env.VITE_VUE_APP_BASE_URL}${to.fullPath}`;
					break;
				case Boolean(tagInRouteMetaData):
					content = tagInRouteMetaData.content;
					break;
				default:
					content = DEFAULT_META_TAGS.get(prop);
			}

			const tag = document.createElement('meta');
			tag.setAttribute(prop.includes(':') ? 'property' : 'name', prop);
			tag.setAttribute('content', content);
			tag.setAttribute('data-controlled-meta', true);
			return tag;
		})
		.forEach((tag) => document.head.appendChild(tag));
}

export default router;
