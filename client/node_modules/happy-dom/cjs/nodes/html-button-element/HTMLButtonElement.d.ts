import Event from '../../event/Event.cjs';
import * as PropertySymbol from '../../PropertySymbol.cjs';
import INamedNodeMap from '../../named-node-map/INamedNodeMap.cjs';
import ValidityState from '../../validity-state/ValidityState.cjs';
import HTMLElement from '../html-element/HTMLElement.cjs';
import IHTMLFormElement from '../html-form-element/IHTMLFormElement.cjs';
import IHTMLLabelElement from '../html-label-element/IHTMLLabelElement.cjs';
import INode from '../node/INode.cjs';
import INodeList from '../node/INodeList.cjs';
import IHTMLButtonElement from './IHTMLButtonElement.cjs';
/**
 * HTML Button Element.
 *
 * Reference:
 * https://developer.mozilla.org/en-US/docs/Web/API/HTMLButtonElement.
 */
export default class HTMLButtonElement extends HTMLElement implements IHTMLButtonElement {
    #private;
    [PropertySymbol.attributes]: INamedNodeMap;
    [PropertySymbol.validationMessage]: string;
    [PropertySymbol.validity]: ValidityState;
    /**
     * Returns validation message.
     *
     * @returns Validation message.
     */
    get validationMessage(): string;
    /**
     * Returns validity.
     *
     * @returns Validity.
     */
    get validity(): ValidityState;
    /**
     * Returns name.
     *
     * @returns Name.
     */
    get name(): string;
    /**
     * Sets name.
     *
     * @param name Name.
     */
    set name(name: string);
    /**
     * Returns value.
     *
     * @returns Value.
     */
    get value(): string;
    /**
     * Sets value.
     *
     * @param value Value.
     */
    set value(value: string);
    /**
     * Returns disabled.
     *
     * @returns Disabled.
     */
    get disabled(): boolean;
    /**
     * Sets disabled.
     *
     * @param disabled Disabled.
     */
    set disabled(disabled: boolean);
    /**
     * Returns type
     *
     * @returns Type
     */
    get type(): string;
    /**
     * Sets type
     *
     * @param v Type
     */
    set type(v: string);
    /**
     * Returns no validate.
     *
     * @returns No validate.
     */
    get formNoValidate(): boolean;
    /**
     * Sets no validate.
     *
     * @param formNoValidate No validate.
     */
    set formNoValidate(formNoValidate: boolean);
    /**
     * Returns the parent form element.
     *
     * @returns Form.
     */
    get form(): IHTMLFormElement;
    /**
     * Returns the associated label elements.
     *
     * @returns Label elements.
     */
    get labels(): INodeList<IHTMLLabelElement>;
    /**
     * Checks validity.
     *
     * @returns "true" if the field is valid.
     */
    checkValidity(): boolean;
    /**
     * Reports validity.
     *
     * @returns Validity.
     */
    reportValidity(): boolean;
    /**
     * Sets validation message.
     *
     * @param message Message.
     */
    setCustomValidity(message: string): void;
    /**
     * @override
     */
    dispatchEvent(event: Event): boolean;
    /**
     * @override
     */
    [PropertySymbol.connectToNode](parentNode?: INode): void;
}
//# sourceMappingURL=HTMLButtonElement.d.ts.map