import TypeaheadInput from '@/components/TypeaheadInput.vue';
import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import { nextTick } from 'vue';

const MOCK_SEARCH_VALUE = 'lev';
const MOCK_ITEMS = [
	{
		county: 'Hockley',
		display_name: 'Levelland',
		locality: 'Levelland',
		state: 'Texas',
		type: 'Locality',
	},
	{
		county: 'Franklin',
		display_name: 'Leverett',
		locality: 'Leverett',
		state: 'Massachusetts',
		type: 'Locality',
	},
	{
		county: 'Levy',
		display_name: 'Levy',
		locality: null,
		state: 'Florida',
		type: 'County',
	},
	{
		county: 'Marion',
		display_name: 'Belleview',
		locality: 'Belleview',
		state: 'Florida',
		type: 'Locality',
	},
];

// Setup function to mount the component with optional props
const mountComponent = (props = {}) => {
	return mount(TypeaheadInput, {
		props: {
			items: MOCK_ITEMS,
			...props,
		},
		attachTo: document.body,
	});
};

// Function to get the input element
const getInput = (wrapper) => wrapper.find('[data-test="typeahead-input"]');

// Function to get the list items
const getListItems = (wrapper) =>
	wrapper.findAll('[data-test="typeahead-list-item"]');

// Function to set input value and wait for update
const setInputValue = async (input, value) => {
	input.setValue(value);
	await nextTick();
};

// Function to focus input and set value
const focusAndSetInput = async (wrapper, value) => {
	const input = getInput(wrapper);
	await input.trigger('focus');
	await setInputValue(input, value);
};

// Test suite
describe('TypeaheadInput', () => {
	it('emits onInput event', async () => {
		const wrapper = mountComponent();
		const input = getInput(wrapper);

		await input.trigger('input');

		expect(wrapper.html()).toMatchSnapshot();
		expect(wrapper.emitted().onInput).toBeTruthy();
	});

	it('emits onFocus event and clears input if no items', async () => {
		const wrapper = mountComponent();
		const input = getInput(wrapper);
		await setInputValue(input, MOCK_SEARCH_VALUE);

		wrapper.setProps({ items: [] });
		await input.trigger('click');
		await input.trigger('focus');

		await nextTick();

		expect(wrapper.html()).toMatchSnapshot();
		expect(wrapper.emitted().onFocus).toBeTruthy();
		expect(input.text()).toBe('');
	});

	it('emits onBlur event', async () => {
		const wrapper = mountComponent();
		const input = getInput(wrapper);

		await input.trigger('blur');

		expect(wrapper.html()).toMatchSnapshot();
		expect(wrapper.emitted().onBlur).toBeTruthy();
	});

	it('focuses next list item on arrow down', async () => {
		const wrapper = mountComponent();
		await focusAndSetInput(wrapper, MOCK_SEARCH_VALUE);
		const [item1, item2] = getListItems(wrapper);

		await getInput(wrapper).trigger('click');
		await getInput(wrapper).trigger('keydown', {
			key: 'ArrowDown',
			keyCode: 40,
		});

		expect(document.activeElement).toBe(item1.element);

		await item1.trigger('keydown', { key: 'ArrowDown', keyCode: 40 });

		expect(document.activeElement).toBe(item2.element);
		expect(wrapper.html()).toMatchSnapshot();
	});

	it('focuses previous list item on arrow up', async () => {
		const wrapper = mountComponent();
		await focusAndSetInput(wrapper, MOCK_SEARCH_VALUE);
		const [item1, item2] = getListItems(wrapper);

		await item2.trigger('focus');
		await item2.trigger('keydown', { key: 'ArrowUp', keyCode: 38 });

		expect(document.activeElement.innerText).toContain(
			item1.element.textContent,
		);
		expect(wrapper.html()).toMatchSnapshot();
	});

	it('focuses input on arrow up from first list item', async () => {
		const wrapper = mountComponent();
		await focusAndSetInput(wrapper, MOCK_SEARCH_VALUE);
		const [item1] = getListItems(wrapper);

		await item1.trigger('focus');
		await item1.trigger('keydown', { key: 'ArrowUp', keyCode: 38 });

		expect(document.activeElement).toBe(getInput(wrapper).element);
		expect(wrapper.html()).toMatchSnapshot();
	});

	it('selects item and emits selectItem event on click', async () => {
		const wrapper = mountComponent();
		await focusAndSetInput(wrapper, MOCK_SEARCH_VALUE);
		const item1 = getListItems(wrapper)[0];

		await item1.trigger('click');
		expect(wrapper.emitted().selectItem).toBeTruthy();
		expect(wrapper.emitted().selectItem[0][0]).toEqual(MOCK_ITEMS[0]);
	});

	it('selects item and emits selectItem event on enter', async () => {
		const wrapper = mountComponent();
		await focusAndSetInput(wrapper, MOCK_SEARCH_VALUE);
		const item1 = getListItems(wrapper)[0];

		await item1.trigger('keydown', { key: 'Enter', keyCode: 13 });
		expect(wrapper.emitted().selectItem).toBeTruthy();
		expect(wrapper.emitted().selectItem[0][0]).toEqual(MOCK_ITEMS[0]);
	});

	it('formats text correctly for different item types', () => {
		const { vm } = mountComponent();

		const localityItem = {
			display_name: 'City',
			county: 'County',
			state: 'California',
			type: 'Locality',
		};
		const countyItem = {
			display_name: 'County',
			state: 'California',
			type: 'County',
		};
		const stateItem = { display_name: 'California', type: 'State' };

		expect(vm.formatText(localityItem)).toBe('City County CA');
		expect(vm.formatText(countyItem)).toBe('County CA');
		expect(vm.formatText(stateItem)).toBe('California');
	});

	it('bolds matched text correctly', () => {
		const { vm } = mountComponent();
		vm.input = 'test';

		expect(vm.boldMatchText('This is a test string')).toBe(
			'This is a <strong>test</strong> string',
		);
	});

	it('computes wrapperId correctly', () => {
		const { vm } = mountComponent({
			id: 'test-id',
		});

		expect(vm.wrapperId).toBe('test-id_wrapper');
	});

	it('computes itemsToDisplay correctly', () => {
		const { vm } = mountComponent();

		expect(vm.itemsToDisplay).toEqual(MOCK_ITEMS);
	});

	it('sets --typeahead-input-height CSS variable', async () => {
		const wrapper = mountComponent();
		const input = getInput(wrapper);

		const root = document.querySelector(':root');
		const inputHeight = input.element.scrollHeight;

		expect(root.style.getPropertyValue('--typeahead-input-height')).toBe(
			`${inputHeight}px`,
		);
	});
});
