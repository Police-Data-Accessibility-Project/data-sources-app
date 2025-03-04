import IElement from './IElement.cjs';
import INode from '../node/INode.cjs';
import IDocument from '../document/IDocument.cjs';
import IDocumentFragment from '../document-fragment/IDocumentFragment.cjs';
/**
 * Element utility.
 */
export default class ElementUtility {
    /**
     * Handles appending a child element to the "children" property.
     *
     * @param ancestorNode Ancestor node.
     * @param node Node to append.
     * @param [options] Options.
     * @param [options.disableAncestorValidation] Disables validation for checking if the node is an ancestor of the ancestorNode.
     * @returns Appended node.
     */
    static appendChild(ancestorNode: IElement | IDocument | IDocumentFragment, node: INode, options?: {
        disableAncestorValidation?: boolean;
    }): INode;
    /**
     * Handles removing a child element from the "children" property.
     *
     * @param ancestorNode Ancestor node.
     * @param node Node.
     * @returns Removed node.
     */
    static removeChild(ancestorNode: IElement | IDocument | IDocumentFragment, node: INode): INode;
    /**
     *
     * Handles inserting a child element to the "children" property.
     *
     * @param ancestorNode Ancestor node.
     * @param newNode Node to insert.
     * @param referenceNode Node to insert before.
     * @param [options] Options.
     * @param [options.disableAncestorValidation] Disables validation for checking if the node is an ancestor of the ancestorNode.
     * @returns Inserted node.
     */
    static insertBefore(ancestorNode: IElement | IDocument | IDocumentFragment, newNode: INode, referenceNode: INode | null, options?: {
        disableAncestorValidation?: boolean;
    }): INode;
}
//# sourceMappingURL=ElementUtility.d.ts.map