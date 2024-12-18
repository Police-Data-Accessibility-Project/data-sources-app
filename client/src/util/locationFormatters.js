import { STATES_TO_ABBREVIATIONS } from './constants';

export function getFullLocationText(location) {
	const searched = getMostNarrowSearchLocationWithResults(location);
	switch (searched) {
		case 'locality':
			return `${location.locality_name}, ${STATES_TO_ABBREVIATIONS.get(location.state_name)}`;
		case 'county':
			return `${location.county_name} ${STATES_TO_ABBREVIATIONS.get(location.state_name) === 'LA' ? 'Parish' : 'County'}, ${location.state_name}`;
		case 'state':
			return location.stat_name;
		default:
			return location.display_name;
	}
}

export function getLocationCityState(location) {
	const locality = location.locality_name ?? '';
	const state = STATES_TO_ABBREVIATIONS.get(location.state_name) ?? '';
	return `${locality}${locality && state ? ', ' : ''}${state}`;
}

export function getMinimalLocationText(location) {
	return getLocationCityState(location) || location.display_name;
}

export function getMostNarrowSearchLocationWithResults(location) {
	if (!location) return null;
	if ('locality_name' in location) return 'locality';
	if ('county_name' in location) return 'county';
	if ('state_name' in location) return 'state';
}
