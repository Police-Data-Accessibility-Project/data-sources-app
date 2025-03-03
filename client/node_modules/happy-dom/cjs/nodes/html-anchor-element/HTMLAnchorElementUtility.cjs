"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const URL_js_1 = __importDefault(require("../../url/URL.cjs"));
/**
 * HTML Anchor Element utility.
 */
class HTMLAnchorElementUtility {
    /**
     * Returns "true" if it is a blob URL.
     *
     * According to spec, if element's url is non-null, its scheme is "blob", and it has an opaque path, then the process of updating properties on the URL should be terminated.
     *
     * @see https://html.spec.whatwg.org/multipage/links.html#reinitialise-url
     * @param url
     * @param url URL.
     * @returns "true" if blob URL.
     */
    static isBlobURL(url) {
        return (url && url.protocol === 'blob:' && url.pathname.length > 1 && url.pathname.includes('://'));
    }
    /**
     * Returns URL.
     *
     * @see https://html.spec.whatwg.org/multipage/links.html#dom-hyperlink-href
     * @see https://html.spec.whatwg.org/multipage/links.html#hyperlink
     * @param document Document.
     * @param href Href.
     * @returns URL.
     */
    static getUrl(document, href) {
        if (!href) {
            return null;
        }
        const documentUrl = document.location.href;
        try {
            return new URL_js_1.default(href.trim(), documentUrl);
        }
        catch (TypeError) {
            // Ignore error
        }
        return null;
    }
}
exports.default = HTMLAnchorElementUtility;
//# sourceMappingURL=HTMLAnchorElementUtility.cjs.map