import DOMRect from './DOMRect.cjs';
import IDOMRectList from './IDOMRectList.cjs';
/**
 * DOM rect list factory.
 *
 * @see https://developer.mozilla.org/en-US/docs/Web/API/Element/getClientRects
 */
export default class DOMRectListFactory {
    /**
     * Creates an HTMLCollection.
     *
     * @param list Nodes.
     * @returns HTMLCollection.
     */
    static create(list?: DOMRect[]): IDOMRectList<DOMRect>;
    /**
     * Returns node by index.
     *
     * @param list
     * @param index Index.
     */
    private static getItem;
}
//# sourceMappingURL=DOMRectListFactory.d.ts.map