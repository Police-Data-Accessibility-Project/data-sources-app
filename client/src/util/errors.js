export class IgnoredError extends Error {
	constructor(message) {
		super(message);
		this.name = 'IgnoredError';
	}
}
