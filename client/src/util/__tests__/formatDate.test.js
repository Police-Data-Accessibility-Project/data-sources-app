import { describe, expect, it } from "vitest";
import formatDate from "../formatDate";

describe("formatDate", () => {
	it("should format a valid date string", () => {
		const date = "01-02-2021";
		const formattedDate = formatDate(date);
		expect(formattedDate).toBe("01/02/2021");
	});

	it("should format a valid Date object", () => {
		const date = new Date("01/02/2022");
		const formattedDate = formatDate(date);
		expect(formattedDate).toBe("01/02/2022");
	});
});
