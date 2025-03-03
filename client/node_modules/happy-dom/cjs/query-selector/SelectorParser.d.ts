import SelectorItem from './SelectorItem.cjs';
/**
 * Utility for parsing a selection string.
 */
export default class SelectorParser {
    /**
     * Parses a selector string and returns an instance of SelectorItem.
     *
     * @param selector Selector.
     * @returns Selector item.
     */
    static getSelectorItem(selector: string): SelectorItem;
    /**
     * Parses a selector string and returns groups with SelectorItem instances.
     *
     * @param selector Selector.
     * @returns Selector groups.
     */
    static getSelectorGroups(selector: string): Array<Array<SelectorItem>>;
    /**
     * Returns attribute RegExp.
     *
     * @param attribute Attribute.
     * @param attribute.value Attribute value.
     * @param attribute.operator Attribute operator.
     * @param attribute.modifier Attribute modifier.
     * @returns Attribute RegExp.
     */
    private static getAttributeRegExp;
    /**
     * Returns pseudo.
     *
     * @param name Pseudo name.
     * @param args Pseudo arguments.
     * @returns Pseudo.
     */
    private static getPseudo;
    /**
     * Returns pseudo nth function.
     *
     * Based on:
     * https://github.com/dperini/nwsapi/blob/master/src/nwsapi.js
     *
     * @param args Pseudo arguments.
     * @returns Pseudo nth function.
     */
    private static getPseudoNthFunction;
}
//# sourceMappingURL=SelectorParser.d.ts.map