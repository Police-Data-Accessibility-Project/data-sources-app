export function isDescendantOf(child, parent) {
	console.debug('iDO', { child, parent });
	if (!child || !parent) return false;
	if (child === parent) return true;
	return isDescendantOf(child.parentNode, parent);
}
