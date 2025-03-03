import IDocument from '../nodes/document/IDocument.cjs';
import IElement from '../nodes/element/IElement.cjs';
import IDocumentFragment from '../nodes/document-fragment/IDocumentFragment.cjs';
/**
 * XML parser.
 */
export default class XMLParser {
    /**
     * Parses XML/HTML and returns a root element.
     *
     * @param document Document.
     * @param xml XML/HTML string.
     * @param [options] Options.
     * @param [options.rootNode] Node to append elements to. Otherwise a new DocumentFragment is created.
     * @param [options.evaluateScripts = false] Set to "true" to enable script execution.
     * @returns Root node.
     */
    static parse(document: IDocument, xml: string, options?: {
        rootNode?: IElement | IDocumentFragment | IDocument;
        evaluateScripts?: boolean;
    }): IElement | IDocumentFragment | IDocument;
    /**
     * Returns document type node.
     *
     * @param document Document.
     * @param value Value.
     * @returns Document type node.
     */
    private static getDocumentTypeNode;
}
//# sourceMappingURL=XMLParser.d.ts.map