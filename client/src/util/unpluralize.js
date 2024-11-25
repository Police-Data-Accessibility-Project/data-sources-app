export default function unpluralize(word, count, trim = 1) {
	return count === 1 ? word : word.slice(0, -trim);
}
