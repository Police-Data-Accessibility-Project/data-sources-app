import * as PropertySymbol from '../../PropertySymbol.cjs';
import CharacterData from '../character-data/CharacterData.cjs';
import IText from './IText.cjs';
import INode from '../node/INode.cjs';
import NodeTypeEnum from '../node/NodeTypeEnum.cjs';
/**
 * Text node.
 */
export default class Text extends CharacterData implements IText {
    [PropertySymbol.nodeType]: NodeTypeEnum;
    /**
     * Node name.
     *
     * @returns Node name.
     */
    get nodeName(): string;
    /**
     * @override
     */
    get data(): string;
    /**
     * @override
     */
    set data(data: string);
    /**
     * Breaks the Text node into two nodes at the specified offset, keeping both nodes in the tree as siblings.
     *
     * @see https://dom.spec.whatwg.org/#dom-text-splittext
     * @param offset Offset.
     * @returns New text node.
     */
    splitText(offset: number): IText;
    /**
     * Converts to string.
     *
     * @returns String.
     */
    toString(): string;
    /**
     * Clones a node.
     *
     * @override
     * @param [deep=false] "true" to clone deep.
     * @returns Cloned node.
     */
    cloneNode(deep?: boolean): IText;
    /**
     * @override
     */
    [PropertySymbol.connectToNode](parentNode?: INode): void;
}
//# sourceMappingURL=Text.d.ts.map