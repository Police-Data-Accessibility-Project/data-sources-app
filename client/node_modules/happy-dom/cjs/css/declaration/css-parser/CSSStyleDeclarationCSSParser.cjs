"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
// PropName   => \s*([^:;]+?)\s*:
// PropValue  => \s*((?:[^(;]*?(?:\([^)]*\))?)*?) <- will match any non ';' char except inside (), nested parentheses are not supported
// !important => \s*(!important)?
// EndOfRule  => \s*(?:$|;)
const SPLIT_RULES_REGEXP = /\s*([^:;]+?)\s*:\s*((?:[^(;]*?(?:\([^)]*\))?)*?)\s*(!important)?\s*(?:$|;)/g;
/**
 * CSS parser.
 */
class CSSStyleDeclarationCSSParser {
    /**
     * Class construtor.
     *
     * @param cssText CSS string.
     * @param callback Callback.
     */
    static parse(cssText, callback) {
        const rules = Array.from(cssText.matchAll(SPLIT_RULES_REGEXP));
        for (const [, key, value, important] of rules) {
            if (key && value) {
                callback(key.trim(), value.trim(), !!important);
            }
        }
    }
}
exports.default = CSSStyleDeclarationCSSParser;
//# sourceMappingURL=CSSStyleDeclarationCSSParser.cjs.map