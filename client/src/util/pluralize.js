/**
 * Pluralizes a word based on a count.
 *
 * @param {string} word - The word to be pluralized.
 * @param {number} count - The count used to determine if the word should be pluralized.
 * @param {string} [suffix="s"] - The suffix to be added to the word when it is pluralized. Defaults to 's'
 * @returns {string} The pluralized word.
 */
export default function pluralize(word, count, suffix = "s") {
	return count === 1 ? word : `${word}${suffix}`;
}
