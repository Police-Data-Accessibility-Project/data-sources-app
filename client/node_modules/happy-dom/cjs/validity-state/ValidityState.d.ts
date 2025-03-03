import IHTMLButtonElement from '../nodes/html-button-element/IHTMLButtonElement.cjs';
import IHTMLInputElement from '../nodes/html-input-element/IHTMLInputElement.cjs';
import IHTMLSelectElement from '../nodes/html-select-element/IHTMLSelectElement.cjs';
import IHTMLTextAreaElement from '../nodes/html-text-area-element/IHTMLTextAreaElement.cjs';
/**
 * Input validity state.
 *
 * Based on:
 * https://github.com/cferdinandi/validate/blob/master/src/js/_validityState.polyfill.js
 *
 * @see https://developer.mozilla.org/en-US/docs/Web/API/ValidityState
 */
export default class ValidityState {
    private element;
    /**
     * Constructor.
     *
     * @param element Input element.
     */
    constructor(element: IHTMLInputElement | IHTMLTextAreaElement | IHTMLSelectElement | IHTMLButtonElement);
    /**
     * Returns validity.
     *
     * @returns "true" if valid.
     */
    get badInput(): boolean;
    /**
     * Returns validity.
     *
     * @returns "true" if valid.
     */
    get customError(): boolean;
    /**
     * Returns validity.
     *
     * @returns "true" if valid.
     */
    get patternMismatch(): boolean;
    /**
     * Returns validity.
     *
     * @returns "true" if valid.
     */
    get rangeOverflow(): boolean;
    /**
     * Returns validity.
     *
     * @returns "true" if valid.
     */
    get rangeUnderflow(): boolean;
    /**
     * Returns validity.
     *
     * @returns "true" if valid.
     */
    get stepMismatch(): boolean;
    /**
     * Returns validity.
     *
     * @returns "true" if valid.
     */
    get tooLong(): boolean;
    /**
     * Returns validity.
     *
     * @returns "true" if valid.
     */
    get tooShort(): boolean;
    /**
     * Returns validity.
     *
     * @returns "true" if valid.
     */
    get typeMismatch(): boolean;
    /**
     * Returns validity.
     *
     * @returns "true" if valid.
     */
    get valueMissing(): boolean;
    /**
     * Returns validity.
     *
     * @returns "true" if valid.
     */
    get valid(): boolean;
}
//# sourceMappingURL=ValidityState.d.ts.map