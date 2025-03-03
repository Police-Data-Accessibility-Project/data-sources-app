import IElement from '../nodes/element/IElement.cjs';
import INodeList from '../nodes/node/INodeList.cjs';
import IDocument from '../nodes/document/IDocument.cjs';
import IDocumentFragment from '../nodes/document-fragment/IDocumentFragment.cjs';
import ISelectorMatch from './ISelectorMatch.cjs';
/**
 * Utility for query selection in an HTML element.
 *
 * @class QuerySelector
 */
export default class QuerySelector {
    /**
     * Finds elements based on a query selector.
     *
     * @param node Node to search in.
     * @param selector Selector.
     * @returns HTML elements.
     */
    static querySelectorAll(node: IElement | IDocument | IDocumentFragment, selector: string): INodeList<IElement>;
    /**
     * Finds an element based on a query selector.
     *
     * @param node Node to search in.
     * @param selector Selector.
     * @returns HTML element.
     */
    static querySelector(node: IElement | IDocument | IDocumentFragment, selector: string): IElement | null;
    /**
     * Checks if an element matches a selector and returns priority weight.
     *
     * @param element Element to match.
     * @param selector Selector to match with.
     * @returns Result.
     */
    static match(element: IElement, selector: string): ISelectorMatch | null;
    /**
     * Checks if a node matches a selector.
     *
     * @param targetElement Target element.
     * @param currentElement Current element.
     * @param selectorItems Selector items.
     * @param [priorityWeight] Priority weight.
     * @returns Result.
     */
    private static matchSelector;
    /**
     * Finds elements based on a query selector for a part of a list of selectors separated with comma.
     *
     * @param rootElement Root element.
     * @param children Child elements.
     * @param selectorItems Selector items.
     * @param [documentPosition] Document position of the element.
     * @returns Document position and element map.
     */
    private static findAll;
    /**
     * Finds an element based on a query selector for a part of a list of selectors separated with comma.
     *
     * @param rootElement Root element.
     * @param children Child elements.
     * @param selectorItems Selector items.
     * @returns HTML element.
     */
    private static findFirst;
}
//# sourceMappingURL=QuerySelector.d.ts.map