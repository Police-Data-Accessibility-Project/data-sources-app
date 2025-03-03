import CSSStyleSheet from '../../css/CSSStyleSheet.cjs';
import * as PropertySymbol from '../../PropertySymbol.cjs';
import HTMLElement from '../html-element/HTMLElement.cjs';
import IHTMLStyleElement from './IHTMLStyleElement.cjs';
/**
 * HTML Style Element.
 *
 * Reference:
 * https://developer.mozilla.org/en-US/docs/Web/API/HTMLStyleElement.
 */
export default class HTMLStyleElement extends HTMLElement implements IHTMLStyleElement {
    private [PropertySymbol.sheet];
    /**
     * Returns CSS style sheet.
     *
     * @returns CSS style sheet.
     */
    get sheet(): CSSStyleSheet;
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
}
//# sourceMappingURL=HTMLStyleElement.d.ts.map