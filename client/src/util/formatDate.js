/**
 * Date formatter for PDAP search results
 * @param {string | Date} date Date to be formatted
 * @returns {string} Date formatted MM/DD/YYYY | YYYY (if first or last day of year)
 */
export default function formatDateForSearchResults(date) {
	// Whether string or Date, convert to date object
	date = new Date(date);

	// Get values
	const month = date.getMonth();
	const day = date.getDate();
	const isFirstDayOfYear = month === 0 && day === 1;
	const isLastDayOfYear = month === 11 && day === 31;

	// If first or last day of year, return year only
	if (isFirstDayOfYear || isLastDayOfYear) {
		return date.getFullYear();
	} else {
		// Otherwise, return date formatted MM/DD/YYYY
		return date.toLocaleDateString("es-pa");
	}
}
