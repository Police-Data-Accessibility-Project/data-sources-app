import CharacterData from '../character-data/CharacterData.cjs';
import IComment from './IComment.cjs';
import * as PropertySymbol from '../../PropertySymbol.cjs';
import NodeTypeEnum from '../node/NodeTypeEnum.cjs';
/**
 * Comment node.
 */
export default class Comment extends CharacterData implements IComment {
    [PropertySymbol.nodeType]: NodeTypeEnum;
    /**
     * Node name.
     *
     * @returns Node name.
     */
    get nodeName(): string;
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
    cloneNode(deep?: boolean): IComment;
}
//# sourceMappingURL=Comment.d.ts.map