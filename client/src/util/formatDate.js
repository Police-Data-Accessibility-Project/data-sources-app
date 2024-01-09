/**
 * Date formatter for PDAP search results
 * @param {string | Date} date Date to be formatted
 * @returns {string} Date formatted MM/DD/YYYY
 */
export default function formatDateForSearchResults(date) {
	return new Date(date).toLocaleDateString("es-pa");
}
