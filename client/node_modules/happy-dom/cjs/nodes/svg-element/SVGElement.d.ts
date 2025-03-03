import CSSStyleDeclaration from '../../css/declaration/CSSStyleDeclaration.cjs';
import * as PropertySymbol from '../../PropertySymbol.cjs';
import Element from '../element/Element.cjs';
import ISVGElement from './ISVGElement.cjs';
import ISVGSVGElement from './ISVGSVGElement.cjs';
import Event from '../../event/Event.cjs';
import INamedNodeMap from '../../named-node-map/INamedNodeMap.cjs';
/**
 * SVG Element.
 *
 * Reference:
 * https://developer.mozilla.org/en-US/docs/Web/API/SVGElement.
 */
export default class SVGElement extends Element implements ISVGElement {
    #private;
    onabort: (event: Event) => void | null;
    onerror: (event: Event) => void | null;
    onload: (event: Event) => void | null;
    onresize: (event: Event) => void | null;
    onscroll: (event: Event) => void | null;
    onunload: (event: Event) => void | null;
    [PropertySymbol.attributes]: INamedNodeMap;
    [PropertySymbol.style]: CSSStyleDeclaration | null;
    /**
     * Returns viewport.
     *
     * @returns SVG rect.
     */
    get viewportElement(): ISVGElement;
    /**
     * Returns current translate.
     *
     * @returns Element.
     */
    get ownerSVGElement(): ISVGSVGElement;
    /**
     * Returns data set.
     *
     * @returns Data set.
     */
    get dataset(): {
        [key: string]: string;
    };
    /**
     * Returns style.
     *
     * @returns Style.
     */
    get style(): CSSStyleDeclaration;
    /**
     * Returns tab index.
     *
     * @returns Tab index.
     */
    get tabIndex(): number;
    /**
     * Returns tab index.
     *
     * @param tabIndex Tab index.
     */
    set tabIndex(tabIndex: number);
    /**
     * Triggers a blur event.
     */
    blur(): void;
    /**
     * Triggers a focus event.
     */
    focus(): void;
}
//# sourceMappingURL=SVGElement.d.ts.map