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
	const locality = location.locality_name ?? '';
	const stateAbbr =
		STATES_TO_ABBREVIATIONS.get(location.state_name) ??
		// TODO: remove this once we have all the location data standardized
		location.state_iso ??
		'';
	const state = location.state_name;
	const displayName = location.display_name;

	if (locality && !state && !stateAbbr) return locality;
	else if (locality && stateAbbr) return `${locality}, ${stateAbbr}`;
	else if (locality && state) return `${locality}, ${state}`;
	else if (state) return state;
	else return displayName;
}

export function getMinimalLocationText(location) {
	return getLocationCityState(location) || location.display_name;
}

export function getMostNarrowSearchLocationWithResults(location) {
	if (!location) return null;
	// Checking for string 'null' because of all the data processing that happens before we get here.
	if (location?.locality_name !== 'null') return 'locality';
	if (location?.county_name !== 'null') return 'county';
	if (location?.state_name !== 'null') return 'state';
	return location?.type?.toLowerCase();
}

// TODO: cache getLocationById function and fetch to get locations by id rather than all of this parsing.
export const mapSearchParamsToLocation = (obj) =>
	(({ state, county, locality, location_id, id }) => ({
		state_name: state,
		state_iso: state,
		county_name: county,
		locality_name: locality,
		id: location_id ?? id,
	}))(obj);

export const mapLocationToSearchParams = (obj) =>
	(({
		state_name,
		state_iso,
		county_name,
		locality_name,
		id,
		location_id,
	}) => ({
		state: state_name ?? state_iso,
		county: county_name,
		locality: locality_name,
		location_id: id ?? location_id,
	}))(obj);
