import IElement from '../element/IElement.cjs';
import INonDocumentTypeChildNode from './INonDocumentTypeChildNode.cjs';
/**
 * Non Document Child node utility.
 */
export default class NonDocumentChildNodeUtility {
    /**
     * Previous element sibling.
     *
     * @param childNode Child node.
     * @returns Element.
     */
    static previousElementSibling(childNode: INonDocumentTypeChildNode): IElement;
    /**
     * Next element sibling.
     *
     * @param childNode Child node.
     * @returns Element.
     */
    static nextElementSibling(childNode: INonDocumentTypeChildNode): IElement;
}
//# sourceMappingURL=NonDocumentChildNodeUtility.d.ts.map