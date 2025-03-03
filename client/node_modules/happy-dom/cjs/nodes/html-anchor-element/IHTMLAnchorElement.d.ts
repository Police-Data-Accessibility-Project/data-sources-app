import IDOMTokenList from '../../dom-token-list/IDOMTokenList.cjs';
import IHTMLElement from '../html-element/IHTMLElement.cjs';
import IHTMLHyperlinkElementUtils from './IHTMLHyperlinkElementUtils.cjs';
/**
 * HTML Anchor Element.
 *
 * Reference:
 * https://developer.mozilla.org/en-US/docs/Web/API/HTMLAnchorElement.
 */
export default interface IHTMLAnchorElement extends IHTMLElement, IHTMLHyperlinkElementUtils {
    readonly relList: IDOMTokenList;
    download: string;
    ping: string;
    hreflang: string;
    referrerPolicy: string;
    rel: string;
    target: string;
    text: string;
    type: string;
}
//# sourceMappingURL=IHTMLAnchorElement.d.ts.map