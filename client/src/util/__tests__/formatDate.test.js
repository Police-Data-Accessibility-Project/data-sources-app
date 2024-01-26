import { describe, expect, it } from 'vitest';
import formatDate from '../formatDate';

describe('formatDate', () => {
	it('should format a valid date string - not first or last day of year', () => {
		const date = '01-02-2021';
		const formattedDate = formatDate(date);
		expect(formattedDate).toBe('01/02/2021');
	});

	it('should format a valid Date object - not first or last day of year', () => {
		const date = new Date('01/02/2022');
		const formattedDate = formatDate(date);
		expect(formattedDate).toBe('01/02/2022');
	});

	it('should format a valid date string and return year only - first or last day of year', () => {
		const date = '01-01-2021';
		const formattedDate = formatDate(date);
		expect(formattedDate).toBe('2021');
	});

	it('should format a valid date string and return year only - first or last day of year', () => {
		const date = new Date('12/31/2022');
		const formattedDate = formatDate(date);
		expect(formattedDate).toBe('2022');
	});

	it('should return undefined if passed non-string, non-date value as argument', () => {
		const formatDateWithNumber = formatDate(1);
		const formatDateWithUndefined = formatDate(undefined);
		expect(formatDateWithNumber).toBe(undefined);
		expect(formatDateWithUndefined).toBe(undefined);
	});

	it('should format a valid date string and return year only - first or last day of year', () => {
		const date = '01-01-2021';
		const formattedDate = formatDate(date);
		expect(formattedDate).toBe('2021');
	});

	it('should format a valid date string and return year only - first or last day of year', () => {
		const date = new Date('12/31/2022');
		const formattedDate = formatDate(date);
		expect(formattedDate).toBe('2022');
	});

	it('should return undefined if passed non-string, non-date value as argument', () => {
		const formatDateWithNumber = formatDate(1);
		const formatDateWithUndefined = formatDate(undefined);
		expect(formatDateWithNumber).toBe(undefined);
		expect(formatDateWithUndefined).toBe(undefined);
	});
});
