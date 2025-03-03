import Node from '../node/Node.cjs';
import * as PropertySymbol from '../../PropertySymbol.cjs';
import IElement from '../element/IElement.cjs';
import IDocumentFragment from './IDocumentFragment.cjs';
import INode from '../node/INode.cjs';
import IHTMLCollection from '../element/IHTMLCollection.cjs';
import INodeList from '../node/INodeList.cjs';
import NodeTypeEnum from '../node/NodeTypeEnum.cjs';
/**
 * DocumentFragment.
 */
export default class DocumentFragment extends Node implements IDocumentFragment {
    readonly [PropertySymbol.children]: IHTMLCollection<IElement>;
    [PropertySymbol.rootNode]: INode;
    [PropertySymbol.nodeType]: NodeTypeEnum;
    /**
     * Returns the document fragment children.
     */
    get children(): IHTMLCollection<IElement>;
    /**
     * Last element child.
     *
     * @returns Element.
     */
    get childElementCount(): number;
    /**
     * First element child.
     *
     * @returns Element.
     */
    get firstElementChild(): IElement;
    /**
     * Last element child.
     *
     * @returns Element.
     */
    get lastElementChild(): IElement;
    /**
     * Get text value of children.
     *
     * @returns Text content.
     */
    get textContent(): string;
    /**
     * Sets text content.
     *
     * @param textContent Text content.
     */
    set textContent(textContent: string);
    /**
     * Inserts a set of Node objects or DOMString objects after the last child of the ParentNode. DOMString objects are inserted as equivalent Text nodes.
     *
     * @param nodes List of Node or DOMString.
     */
    append(...nodes: (INode | string)[]): void;
    /**
     * Inserts a set of Node objects or DOMString objects before the first child of the ParentNode. DOMString objects are inserted as equivalent Text nodes.
     *
     * @param nodes List of Node or DOMString.
     */
    prepend(...nodes: (INode | string)[]): void;
    /**
     * Replaces the existing children of a node with a specified new set of children.
     *
     * @param nodes List of Node or DOMString.
     */
    replaceChildren(...nodes: (INode | string)[]): void;
    /**
     * Query CSS selector to find matching nodes.
     *
     * @param selector CSS selector.
     * @returns Matching elements.
     */
    querySelectorAll(selector: string): INodeList<IElement>;
    /**
     * Query CSS Selector to find matching node.
     *
     * @param selector CSS selector.
     * @returns Matching element.
     */
    querySelector(selector: string): IElement;
    /**
     * Returns an element by ID.
     *
     * @param id ID.
     * @returns Matching element.
     */
    getElementById(id: string): IElement;
    /**
     * Clones a node.
     *
     * @override
     * @param [deep=false] "true" to clone deep.
     * @returns Cloned node.
     */
    cloneNode(deep?: boolean): IDocumentFragment;
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
    insertBefore(newNode: INode, referenceNode: INode | null): INode;
}
//# sourceMappingURL=DocumentFragment.d.ts.map