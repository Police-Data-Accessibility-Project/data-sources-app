import IDocument from '../nodes/document/IDocument.cjs';
/**
 * Node factory used for setting the owner document to nodes.
 */
export default class NodeFactory {
    static ownerDocuments: IDocument[];
    /**
     * Creates a node instance with the given owner document.
     *
     * @param ownerDocument Owner document.
     * @param nodeClass Node class.
     * @param [args] Node arguments.
     * @returns Node instance.
     */
    static createNode<T>(ownerDocument: IDocument, nodeClass: new (...args: any[]) => T, ...args: any[]): T;
    /**
     * Pulls an owner document from the queue.
     *
     * @returns Document.
     */
    static pullOwnerDocument(): IDocument;
}
//# sourceMappingURL=NodeFactory.d.ts.map