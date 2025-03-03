import CSSStyleSheet from '../../css/CSSStyleSheet.cjs';
import * as PropertySymbol from '../../PropertySymbol.cjs';
import HTMLElement from '../html-element/HTMLElement.cjs';
import IHTMLLinkElement from './IHTMLLinkElement.cjs';
import Event from '../../event/Event.cjs';
import ErrorEvent from '../../event/events/ErrorEvent.cjs';
import INode from '../../nodes/node/INode.cjs';
import DOMTokenList from '../../dom-token-list/DOMTokenList.cjs';
import IDOMTokenList from '../../dom-token-list/IDOMTokenList.cjs';
import INamedNodeMap from '../../named-node-map/INamedNodeMap.cjs';
import IBrowserFrame from '../../browser/types/IBrowserFrame.cjs';
/**
 * HTML Link Element.
 *
 * Reference:
 * https://developer.mozilla.org/en-US/docs/Web/API/HTMLLinkElement.
 */
export default class HTMLLinkElement extends HTMLElement implements IHTMLLinkElement {
    #private;
    onerror: (event: ErrorEvent) => void;
    onload: (event: Event) => void;
    [PropertySymbol.attributes]: INamedNodeMap;
    readonly [PropertySymbol.sheet]: CSSStyleSheet;
    [PropertySymbol.evaluateCSS]: boolean;
    [PropertySymbol.relList]: DOMTokenList;
    /**
     * Constructor.
     *
     * @param browserFrame Browser frame.
     */
    constructor(browserFrame: IBrowserFrame);
    /**
     * Returns sheet.
     */
    get sheet(): CSSStyleSheet;
    /**
     * Returns rel list.
     *
     * @returns Rel list.
     */
    get relList(): IDOMTokenList;
    /**
     * Returns as.
     *
     * @returns As.
     */
    get as(): string;
    /**
     * Sets crossOrigin.
     *
     * @param crossOrigin CrossOrigin.
     */
    set as(as: string);
    /**
     * Returns crossOrigin.
     *
     * @returns CrossOrigin.
     */
    get crossOrigin(): string;
    /**
     * Sets crossOrigin.
     *
     * @param crossOrigin CrossOrigin.
     */
    set crossOrigin(crossOrigin: string);
    /**
     * Returns href.
     *
     * @returns Href.
     */
    get href(): string;
    /**
     * Sets href.
     *
     * @param href Href.
     */
    set href(href: string);
    /**
     * Returns hreflang.
     *
     * @returns Hreflang.
     */
    get hreflang(): string;
    /**
     * Sets hreflang.
     *
     * @param hreflang Hreflang.
     */
    set hreflang(hreflang: string);
    /**
     * Returns media.
     *
     * @returns Media.
     */
    get media(): string;
    /**
     * Sets media.
     *
     * @param media Media.
     */
    set media(media: string);
    /**
     * Returns referrerPolicy.
     *
     * @returns ReferrerPolicy.
     */
    get referrerPolicy(): string;
    /**
     * Sets referrerPolicy.
     *
     * @param referrerPolicy ReferrerPolicy.
     */
    set referrerPolicy(referrerPolicy: string);
    /**
     * Returns rel.
     *
     * @returns Rel.
     */
    get rel(): string;
    /**
     * Sets rel.
     *
     * @param rel Rel.
     */
    set rel(rel: string);
    /**
     * Returns type.
     *
     * @returns Type.
     */
    get type(): string;
    /**
     * Sets type.
     *
     * @param type Type.
     */
    set type(type: string);
    /**
     * @override
     */
    [PropertySymbol.connectToNode](parentNode?: INode): void;
}
//# sourceMappingURL=HTMLLinkElement.d.ts.map