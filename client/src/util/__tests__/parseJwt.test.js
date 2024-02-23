import { describe, expect, it } from 'vitest';
import parseJwt from '../parseJwt';

const token =
	'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDg3MTc3NjAsImlhdCI6MTcwODcxNzQ2MCwic3ViIjo2OX0.vX3JKqlUb-L_IWEYyG7R0zlMnY-kj5py5XsUviyAJN4';

describe('parseJwt', () => {
	it('should parse a valid Jwt', () => {
		expect(parseJwt(token)).toEqual({
			exp: 1708717760,
			iat: 1708717460,
			sub: 69,
		});
	});
});
