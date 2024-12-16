import { STATES_TO_ABBREVIATIONS } from '@/util/constants';

// TODO: replace with common util
export function formatText(location) {
	return (
		location.locality_name +
		', ' +
		STATES_TO_ABBREVIATIONS.get(location.state_name)
	);
}
