// This file contains utils related to the search results page

import { ALL_LOCATION_TYPES } from '@/util/constants';
import statesToAbbreviations from '@/util/statesToAbbreviations';

/**
 * Manipulates data to be renderable by search results component (grouped by agency)
 * @param results {{count: number; data: Record<federal | state | county | locality, {count: number, results: []}>}}
 */
export function groupResultsByAgency(results) {
	const resultsGroupedByLocalityThenAgency = {};
	resultsGroupedByLocalityThenAgency.count = results.count;

	Object.keys(results.data).forEach((locale) => {
		// Create new object keyed by agency
		const sourcesByAgency = {};

		// add data sources to it.
		results.data[locale].results.forEach((source) => {
			if (source.agency_name in sourcesByAgency) {
				sourcesByAgency[source.agency_name] = sourcesByAgency[
					source.agency_name
				].concat([source]);
			} else if (source.agency_name) {
				sourcesByAgency[source.agency_name] = [source];
			}
		});

		resultsGroupedByLocalityThenAgency[locale] = {
			count: results.data[locale].count,
			sourcesByAgency,
		};
	});

	return resultsGroupedByLocalityThenAgency;
}

export function getMostNarrowSearchLocationWithResults(params) {
	if ('locality' in params) return 'locality';
	if ('county' in params) return 'county';
	if ('state' in params) return 'state';
	if ('federal' in params) return 'federal';
}

export function normalizeLocaleForHash(locale, results) {
	if (results.data[locale].count) return locale;

	for (let i = ALL_LOCATION_TYPES.indexOf(locale) - 1; i > 0; i--) {
		const narrowerLocale = ALL_LOCATION_TYPES[i];

		if (results.data[narrowerLocale].count) return narrowerLocale;
	}
}

export function getLocationText({ searched, params }) {
	switch (searched) {
		case 'locality':
			return `${params.locality}, ${statesToAbbreviations.get(params.state)}`;
		case 'county':
			return `${params.county} ${statesToAbbreviations.get(params.state) === 'LA' ? 'Parish' : 'County'}, ${params.state}`;
		case 'state':
			return params.state;
		default:
			return 'federal';
	}
}

export function getAnchorLinkText(locale) {
	if (locale === 'locality') return 'local';
	else return locale;
}
