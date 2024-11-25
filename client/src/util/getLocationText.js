import { STATES_TO_ABBREVIATIONS } from './constants';

export default function getLocationText({ searched, params }) {
	switch (searched) {
		case 'locality':
			return `${params.locality}, ${STATES_TO_ABBREVIATIONS.get(params.state)}`;
		case 'county':
			return `${params.county} ${STATES_TO_ABBREVIATIONS.get(params.state) === 'LA' ? 'Parish' : 'County'}, ${params.state}`;
		case 'state':
			return params.state;
		default:
			return 'federal';
	}
}

export function getMostNarrowSearchLocationWithResults(params) {
	if ('locality' in params) return 'locality';
	if ('county' in params) return 'county';
	if ('state' in params) return 'state';
	if ('federal' in params) return 'federal';
}
