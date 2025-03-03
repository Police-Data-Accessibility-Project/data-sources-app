import CSSStyleSheet from '../../css/CSSStyleSheet.cjs';
import IDOMTokenList from '../../dom-token-list/IDOMTokenList.cjs';
import IHTMLElement from '../html-element/IHTMLElement.cjs';
/**
 * HTML Link Element.
 *
 * Reference:
 * https://developer.mozilla.org/en-US/docs/Web/API/HTMLLinkElement.
 */
export default interface IHTMLLinkElement extends IHTMLElement {
    readonly sheet: CSSStyleSheet;
    readonly relList: IDOMTokenList;
    as: string;
    crossOrigin: string;
    href: string;
    hreflang: string;
    media: string;
    referrerPolicy: string;
    rel: string;
    type: string;
}
//# sourceMappingURL=IHTMLLinkElement.d.ts.map