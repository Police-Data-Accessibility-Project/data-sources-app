import { mount, RouterLinkStub, RouterViewStub } from '@vue/test-utils';
import App from '../../App.vue';
import { beforeEach, describe, expect, it } from 'vitest';
import { links } from '../../util/links';
import { createTestingPinia } from '@pinia/testing';

let wrapper;

describe('App', () => {
	beforeEach(() => {
		wrapper = mount(App, {
			global: {
				plugins: [createTestingPinia()],
				provide: {
					navLinks: links,
					footerLinks: links,
				},
				stubs: {
					RouterLink: RouterLinkStub,
					RouterView: RouterViewStub,
				},
			},
		});
	});

	it('renders the App', () => {
		expect(wrapper.html()).toMatchSnapshot();
	});

	it('provides the correct navLinks and footerLinks data', () => {
		expect(wrapper.vm.$options.provide.navLinks).toEqual(links);
		expect(wrapper.vm.$options.provide.footerLinks).toEqual(links);
	});
});
