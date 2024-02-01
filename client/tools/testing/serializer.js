import { print as _print } from 'jest-serializer-vue-tjw';

const helpers = {
	isHtmlString: function (received) {
		return (
			typeof received === 'string' &&
			(received.startsWith('<') || received.startsWith('"<'))
		);
	},
	isVueWrapper: function (received) {
		return typeof received === 'object' && typeof received.html === 'function';
	},
};

function test(received) {
	return helpers.isHtmlString(received) || helpers.isVueWrapper(received);
}
function print(received) {
	// force to a string
	received = (received?.html && received?.html()) || received;
	return _print(received);
}

export default {
	print,
	test,
};
