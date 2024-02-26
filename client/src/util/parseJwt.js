import { jwtDecode } from 'jwt-decode';

/**
 * Util for parsing JSON Web Tokens
 * @param {string} token JWT to be decoded
 * @returns {{ expiration: number, iat: number, sub: string }} Decoded JWT
 */
export default function parseJwt(token) {
	return jwtDecode(token);
}
