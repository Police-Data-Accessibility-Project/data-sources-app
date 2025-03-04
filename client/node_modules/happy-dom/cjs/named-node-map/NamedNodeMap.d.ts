import INamedNodeMap from './INamedNodeMap.cjs';
import * as PropertySymbol from '../PropertySymbol.cjs';
import IAttr from '../nodes/attr/IAttr.cjs';
/**
 * Named Node Map.
 *
 * @see https://developer.mozilla.org/en-US/docs/Web/API/NamedNodeMap
 */
export default class NamedNodeMap implements INamedNodeMap {
    [index: number]: IAttr;
    length: number;
    protected [PropertySymbol.namedItems]: {
        [k: string]: IAttr;
    };
    /**
     * Returns string.
     *
     * @returns string.
     */
    get [Symbol.toStringTag](): string;
    /**
     * Iterator.
     *
     * @returns Iterator.
     */
    [Symbol.iterator](): IterableIterator<IAttr>;
    /**
     * Returns item by index.
     *
     * @param index Index.
     */
    item(index: number): IAttr | null;
    /**
     * Returns named item.
     *
     * @param name Name.
     * @returns Item.
     */
    getNamedItem(name: string): IAttr | null;
    /**
     * Returns item by name and namespace.
     *
     * @param namespace Namespace.
     * @param localName Local name of the attribute.
     * @returns Item.
     */
    getNamedItemNS(namespace: string, localName: string): IAttr | null;
    /**
     * Sets named item.
     *
     * @param item Item.
     * @returns Replaced item.
     */
    setNamedItem(item: IAttr): IAttr | null;
    /**
     * Adds a new namespaced item.
     *
     * @alias setNamedItem()
     * @param item Item.
     * @returns Replaced item.
     */
    setNamedItemNS(item: IAttr): IAttr | null;
    /**
     * Removes an item.
     *
     * @throws DOMException
     * @param name Name of item.
     * @returns Removed item.
     */
    removeNamedItem(name: string): IAttr;
    /**
     * Removes a namespaced item.
     *
     * @param namespace Namespace.
     * @param localName Local name of the item.
     * @returns Removed item.
     */
    removeNamedItemNS(namespace: string, localName: string): IAttr | null;
    /**
     * Sets named item without calling listeners for certain attributes.
     *
     * @param item Item.
     * @returns Replaced item.
     */
    [PropertySymbol.setNamedItemWithoutConsequences](item: IAttr): IAttr | null;
    /**
     * Removes an item without throwing if it doesn't exist.
     *
     * @param name Name of item.
     * @returns Removed item, or null if it didn't exist.
     */
    [PropertySymbol.removeNamedItem](name: string): IAttr | null;
    /**
     * Removes an item without calling listeners for certain attributes.
     *
     * @param name Name of item.
     * @returns Removed item, or null if it didn't exist.
     */
    [PropertySymbol.removeNamedItemWithoutConsequences](name: string): IAttr | null;
    /**
     * Removes an item from index.
     *
     * @param item Item.
     */
    protected [PropertySymbol.removeNamedItemIndex](item: IAttr): void;
    /**
     * Returns "true" if the property name is valid.
     *
     * @param name Name.
     * @returns True if the property name is valid.
     */
    protected [PropertySymbol.isValidPropertyName](name: string): boolean;
}
//# sourceMappingURL=NamedNodeMap.d.ts.map