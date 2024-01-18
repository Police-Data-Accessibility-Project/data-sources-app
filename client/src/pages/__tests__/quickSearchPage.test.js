import { mount } from "@vue/test-utils";
import QuickSearchPage from "../QuickSearchPage.vue";
import { describe, expect, test } from "vitest";

describe("QuickSearchPage", () => {
	test("is a Vue instance", () => {
		const wrapper = mount(QuickSearchPage);
		expect(wrapper.vm).toBeTruthy();
		expect(wrapper.html()).toMatchSnapshot();
	});
});
