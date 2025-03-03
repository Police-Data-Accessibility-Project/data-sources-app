import INode from '../nodes/node/INode.cjs';
type INodeFilter = ((node: INode) => number) | {
    acceptNode(node: INode): number;
};
export default INodeFilter;
//# sourceMappingURL=INodeFilter.d.ts.map