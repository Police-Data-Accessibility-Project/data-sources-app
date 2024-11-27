export class DataLoaderErrorPassThrough extends Error {
	constructor(message) {
		super(message);
		this.name = 'DataLoaderErrorPassThrough';
	}
}
