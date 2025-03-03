import IElement from '../element/IElement.cjs';
import INode from '../node/INode.cjs';
export default interface INonDocumentTypeChildNode extends INode {
    readonly previousElementSibling: IElement;
    readonly nextElementSibling: IElement;
}
//# sourceMappingURL=INonDocumentTypeChildNode.d.ts.map