import Element from './Element.cjs';
/**
 * Storage type for a dataset proxy.
 */
type DatasetRecord = Record<string, string>;
/**
 * Dataset helper proxy.
 *
 * Reference:
 * https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/dataset
 */
export default class Dataset {
    readonly proxy: DatasetRecord;
    /**
     * @param element The parent element.
     */
    constructor(element: Element);
    /**
     * Transforms a kebab cased string to camel case.
     *
     * @param text Text string.
     * @returns Camel cased string.
     */
    static kebabToCamelCase(text: string): string;
    /**
     * Transforms a camel cased string to kebab case.
     *
     * @param text Text string.
     * @returns Kebab cased string.
     */
    static camelCaseToKebab(text: string): string;
}
export {};
//# sourceMappingURL=Dataset.d.ts.map