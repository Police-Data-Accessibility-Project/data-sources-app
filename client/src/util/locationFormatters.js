import { STATES_TO_ABBREVIATIONS } from './constants';

export function getFullLocationText(location) {
	const searched = getMostNarrowSearchLocationWithResults(location);
	switch (searched) {
		case 'locality':
			return `${location.locality}, ${STATES_TO_ABBREVIATIONS.get(location.state)}`;
		case 'county':
			return `${location.county} ${STATES_TO_ABBREVIATIONS.get(location.state) === 'LA' ? 'Parish' : 'County'}, ${location.state}`;
		case 'state':
			return location.state;
		default:
			return location.display_name;
	}
}

export function getLocationCityState(location) {
	const locality = location.locality ?? '';
	const state = STATES_TO_ABBREVIATIONS.get(location.state) ?? '';
	return `${locality}${locality && state ? ', ' : ''}${state}`;
}

export function getMinimalLocationText(location) {
	return getLocationCityState(location) || location.display_name;
}

export function getMostNarrowSearchLocationWithResults(params) {
	if (!params) return null;
	if ('locality' in params) return 'locality';
	if ('county' in params) return 'county';
	if ('state' in params) return 'state';
	if ('federal' in params) return 'federal';
}
