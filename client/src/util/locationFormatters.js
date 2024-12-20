import { STATES_TO_ABBREVIATIONS } from './constants';

export function getFullLocationText(location) {
	const searched = getMostNarrowSearchLocationWithResults(location);
	switch (searched) {
		case 'locality':
			return `${location.locality_name}, ${location.county_name}, ${STATES_TO_ABBREVIATIONS.get(location.state_name)}`;
		case 'county':
			return `${location.county_name} ${STATES_TO_ABBREVIATIONS.get(location.state_name) === 'LA' ? 'Parish' : 'County'}, ${location.state_name}`;
		case 'state':
			return location.state_name;
		default:
			return location.display_name ?? '';
	}
}

export function getLocationCityState(location) {
	const searched = getMostNarrowSearchLocationWithResults(location);

	const locality = location.locality_name;
	const stateAbbr = STATES_TO_ABBREVIATIONS.get(location.state_name);
	const state = location.state_name;
	const displayName = location.display_name;

	if (searched === 'locality') {
		if (locality && !state && !stateAbbr) return locality;
		else if (locality && stateAbbr) return `${locality}, ${stateAbbr}`;
		else if (locality && state) return `${locality}, ${state}`;
	} else if (searched === 'county' || searched === 'state') {
		return state;
	} else return displayName;
}

export function getMinimalLocationText(location) {
	return getLocationCityState(location) || location.display_name;
}

export function getMostNarrowSearchLocationWithResults(location) {
	if (!location) return null;
	if (location?.locality_name) return 'locality';
	if (location?.county_name) return 'county';
	if (location?.state_name) return 'state';
	return location?.type?.toLowerCase();
}

// TODO: cache getLocationById function and fetch to get locations by id rather than all of this parsing.
export const mapSearchParamsToLocation = (obj) => {
	const { state, county, locality, location_id, id } = obj;
	const mapped = {};

	if (state) {
		mapped.state_name = state;
		mapped.state_iso = state;
	}
	if (county) {
		mapped.county_name = county;
	}
	if (locality) {
		mapped.locality_name = locality;
	}
	if (location_id || id) {
		mapped.id = location_id ?? id;
	}

	return mapped;
};

export const mapLocationToSearchParams = (obj) => {
	const { state_name, state_iso, county_name, locality_name, id, location_id } =
		obj;
	const mapped = {};

	if (state_name || state_iso) {
		mapped.state = state_name ?? state_iso;
	}
	if (county_name) {
		mapped.county = county_name;
	}
	if (locality_name) {
		mapped.locality = locality_name;
	}
	if (id || location_id) {
		mapped.location_id = id ?? location_id;
	}

	return mapped;
};
