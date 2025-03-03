import IDocument from '../nodes/document/IDocument.cjs';
import IBrowserWindow from '../window/IBrowserWindow.cjs';
/**
 * DOM parser.
 *
 * Reference:
 * https://developer.mozilla.org/en-US/docs/Web/API/DOMParser.
 */
export default class DOMParser {
    #private;
    /**
     * Constructor.
     *
     * @param window Window.
     */
    constructor(window: IBrowserWindow);
    /**
     * Parses HTML and returns a root element.
     *
     * @param string HTML data.
     * @param mimeType Mime type.
     * @returns Root element.
     */
    parseFromString(string: string, mimeType: string): IDocument;
}
//# sourceMappingURL=DOMParser.d.ts.map