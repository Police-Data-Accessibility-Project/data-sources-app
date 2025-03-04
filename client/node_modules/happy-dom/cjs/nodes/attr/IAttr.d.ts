import IElement from '../element/IElement.cjs';
import INode from './../node/INode.cjs';
/**
 * Attr.
 */
export default interface IAttr extends INode {
    value: string;
    name: string;
    namespaceURI: string;
    readonly ownerElement: IElement;
    readonly specified: boolean;
    readonly localName: string;
    readonly prefix: string;
}
//# sourceMappingURL=IAttr.d.ts.map