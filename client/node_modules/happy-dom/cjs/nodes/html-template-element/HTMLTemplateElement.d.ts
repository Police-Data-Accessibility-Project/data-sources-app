import HTMLElement from '../html-element/HTMLElement.cjs';
import * as PropertySymbol from '../../PropertySymbol.cjs';
import IDocumentFragment from '../document-fragment/IDocumentFragment.cjs';
import INode from '../node/INode.cjs';
import IHTMLTemplateElement from './IHTMLTemplateElement.cjs';
/**
 * HTML Template Element.
 *
 * Reference:
 * https://developer.mozilla.org/en-US/docs/Web/API/HTMLTemplateElement.
 */
export default class HTMLTemplateElement extends HTMLElement implements IHTMLTemplateElement {
    [PropertySymbol.content]: IDocumentFragment;
    /**
     * Returns content.
     *
     * @returns Content.
     */
    get content(): IDocumentFragment;
    /**
     * @override
     */
    get innerHTML(): string;
    /**
     * @override
     */
    set innerHTML(html: string);
    /**
     * @override
     */
    get firstChild(): INode;
    /**
     * @override
     */
    get lastChild(): INode;
    /**
     * @override
     */
    getInnerHTML(options?: {
        includeShadowRoots?: boolean;
    }): string;
    /**
     * @override
     */
    appendChild(node: INode): INode;
    /**
     * @override
     */
    removeChild(node: INode): INode;
    /**
     * @override
     */
    insertBefore(newNode: INode, referenceNode: INode): INode;
    /**
     * @override
     */
    replaceChild(newChild: INode, oldChild: INode): INode;
    /**
     * @override
     */
    cloneNode(deep?: boolean): IHTMLTemplateElement;
}
//# sourceMappingURL=HTMLTemplateElement.d.ts.map