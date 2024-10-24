import statesToAbbreviations from '@/util/statesToAbbreviations';

export default function formatText(item) {
	switch (item.type) {
		case 'Locality':
			return `${item.display_name} ${item.county} ${statesToAbbreviations.get(item.state)}`;
		case 'County':
			return `${item.display_name} ${statesToAbbreviations.get(item.state)}`;
		case 'State':
		default:
			return item.display_name;
	}
}
