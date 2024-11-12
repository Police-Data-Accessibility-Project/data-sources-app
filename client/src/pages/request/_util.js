import { STATES_TO_ABBREVIATIONS } from '@/util/constants';

export function formatText(item) {
	switch (item.type) {
		case 'Locality':
			return `${item.display_name} ${item.county} ${STATES_TO_ABBREVIATIONS.get(item.state)}`;
		case 'County':
			return `${item.display_name} ${STATES_TO_ABBREVIATIONS.get(item.state)}`;
		case 'State':
		default:
			return item.display_name;
	}
}
