import acronym from 'pdap-design-system/images/acronym.svg';

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
export function refreshMetaTagsByRoute(to) {
	// Get nearest matched route that has title / meta tag overrides
	const nearestRouteWithTitle = getNearestRouteByMetaProperty(to, 'title');
	const nearestRouteWithMeta = getNearestRouteByMetaProperty(to, 'metaTags');

	// Update document title
	document.title =
		nearestRouteWithTitle?.meta?.title ?? DEFAULT_META_TAGS.get('title');

	refreshMetaTags(to, nearestRouteWithMeta);
}

/**
 * Gets closest route of matching routes that has a particular meta property
 *
 * @param {RouteLocationNormalized} to route navigating to
 * @param {string} property meta property to find
 * @returns {RouteLocationNormalized} nearest matching route
 */
function getNearestRouteByMetaProperty(to, property) {
	return [...to.matched].reverse().find((route) => route?.meta?.[property]);
}

/**
 * appends meta tags to routes
 *
 * @param {RouteLocationNormalized} nearestRouteWithMeta route navigating to
 * @param {RouteLocationNormalized} nearestRouteWithMeta nearest route to `to` that has a meta tag defined
 */
function refreshMetaTags(to, nearestRouteWithMeta) {
	// Remove current tags
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
					content = `${import.meta.env.VITE_VUE_APP_BASE_URL}/${to.fullPath}`;
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
