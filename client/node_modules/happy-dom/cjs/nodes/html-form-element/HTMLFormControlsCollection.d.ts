import IHTMLFormControlsCollection from './IHTMLFormControlsCollection.cjs';
import * as PropertySymbol from '../../PropertySymbol.cjs';
import IHTMLInputElement from '../html-input-element/IHTMLInputElement.cjs';
import IHTMLTextAreaElement from '../html-text-area-element/IHTMLTextAreaElement.cjs';
import IHTMLSelectElement from '../html-select-element/IHTMLSelectElement.cjs';
import RadioNodeList from './RadioNodeList.cjs';
import IHTMLButtonElement from '../html-button-element/IHTMLButtonElement.cjs';
/**
 * HTMLFormControlsCollection.
 *
 * @see https://developer.mozilla.org/en-US/docs/Web/API/HTMLFormControlsCollection
 */
export default class HTMLFormControlsCollection extends Array<IHTMLInputElement | IHTMLTextAreaElement | IHTMLSelectElement | IHTMLButtonElement> implements IHTMLFormControlsCollection {
    [PropertySymbol.namedItems]: {
        [k: string]: RadioNodeList;
    };
    /**
     * Returns item by index.
     *
     * @param index Index.
     */
    item(index: number): IHTMLInputElement | IHTMLTextAreaElement | IHTMLSelectElement | IHTMLButtonElement | null;
    /**
     * Returns named item.
     *
     * @param name Name.
     * @returns Node.
     */
    namedItem(name: string): IHTMLInputElement | IHTMLTextAreaElement | IHTMLSelectElement | IHTMLButtonElement | RadioNodeList | null;
    /**
     * Appends named item.
     *
     * @param node Node.
     * @param name Name.
     */
    [PropertySymbol.appendNamedItem](node: IHTMLInputElement | IHTMLTextAreaElement | IHTMLSelectElement | IHTMLButtonElement, name: string): void;
    /**
     * Appends named item.
     *
     * @param node Node.
     * @param name Name.
     */
    [PropertySymbol.removeNamedItem](node: IHTMLInputElement | IHTMLTextAreaElement | IHTMLSelectElement | IHTMLButtonElement, name: string): void;
    /**
     * Returns "true" if the property name is valid.
     *
     * @param name Name.
     * @returns True if the property name is valid.
     */
    protected [PropertySymbol.isValidPropertyName](name: string): boolean;
}
//# sourceMappingURL=HTMLFormControlsCollection.d.ts.map