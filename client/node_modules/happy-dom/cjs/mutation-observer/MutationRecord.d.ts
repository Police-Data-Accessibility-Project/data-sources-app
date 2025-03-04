import INode from '../nodes/node/INode.cjs';
/**
 * MutationRecord is a model for a mutation.
 *
 * @see https://developer.mozilla.org/en-US/docs/Web/API/MutationRecord
 */
export default class MutationRecord {
    type: string;
    target: INode;
    addedNodes: INode[];
    removedNodes: INode[];
    previousSibling: INode;
    nextSibling: INode;
    attributeName: string;
    attributeNamespace: string;
    oldValue: string;
    /**
     * Constructor.
     *
     * @param init Options to initialize the mutation record.
     */
    constructor(init?: Partial<MutationRecord>);
}
//# sourceMappingURL=MutationRecord.d.ts.map