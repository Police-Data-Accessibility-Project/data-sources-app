"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const url_1 = require("url");
const DOMException_js_1 = __importDefault(require("../../exception/DOMException.cjs"));
const DOMExceptionNameEnum_js_1 = __importDefault(require("../../exception/DOMExceptionNameEnum.cjs"));
/**
 * Browser frame URL utility.
 */
class BrowserFrameURL {
    /**
     * Returns relative URL.
     *
     * @param frame Frame.
     * @param url URL.
     * @returns Relative URL.
     */
    static getRelativeURL(frame, url) {
        url = url || 'about:blank';
        if (url.startsWith('about:') || url.startsWith('javascript:')) {
            return new url_1.URL(url);
        }
        try {
            return new url_1.URL(url, frame.window.location);
        }
        catch (e) {
            if (frame.window.location.hostname) {
                throw new DOMException_js_1.default(`Failed to construct URL from string "${url}".`, DOMExceptionNameEnum_js_1.default.uriMismatchError);
            }
            else {
                throw new DOMException_js_1.default(`Failed to construct URL from string "${url}" relative to URL "${frame.window.location.href}".`, DOMExceptionNameEnum_js_1.default.uriMismatchError);
            }
        }
    }
}
exports.default = BrowserFrameURL;
//# sourceMappingURL=BrowserFrameURL.cjs.map