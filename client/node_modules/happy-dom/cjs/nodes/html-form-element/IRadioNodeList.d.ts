import IElement from '../element/IElement.cjs';
import INodeList from '../node/INodeList.cjs';
/**
 * RadioNodeList.
 *
 * @see https://developer.mozilla.org/en-US/docs/Web/API/RadioNodeList
 */
export default interface IRadioNodeList extends INodeList<IElement> {
    /**
     * Returns value.
     *
     * @returns Value.
     */
    readonly value: string;
}
//# sourceMappingURL=IRadioNodeList.d.ts.map