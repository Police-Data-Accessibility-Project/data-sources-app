import { describe, expect, it } from 'vitest';
import pluralize from '../pluralize';

describe('pluralize', () => {
	it('should return the pluralized word when count is greater than 1', () => {
		expect(pluralize('apple', 2)).toBe('apples');
		expect(pluralize('cat', 3)).toBe('cats');
		expect(pluralize('box', 5, 'es')).toBe('boxes');
	});

	it('should return the singular word when count is 1', () => {
		expect(pluralize('apple', 1)).toBe('apple');
		expect(pluralize('cat', 1)).toBe('cat');
		expect(pluralize('box', 1)).toBe('box');
	});

	it('should use default suffix "s" when no suffix is provided', () => {
		expect(pluralize('apple', 2)).toBe('apples');
		expect(pluralize('cat', 3)).toBe('cats');
	});
});
