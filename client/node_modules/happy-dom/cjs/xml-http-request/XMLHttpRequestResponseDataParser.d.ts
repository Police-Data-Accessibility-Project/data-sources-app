/// <reference types="node" />
import IBrowserWindow from '../window/IBrowserWindow.cjs';
import Blob from '../file/Blob.cjs';
import IDocument from '../nodes/document/IDocument.cjs';
import { Buffer } from 'buffer';
/**
 *
 */
export default class XMLHttpRequestResponseDataParser {
    /**
     * Parses response.
     *
     * @param options Options.
     * @param options.window Window.
     * @param [options.responseType] Response type.
     * @param [options.data] Data.
     * @param [options.contentType] Content type.
     * @returns Parsed response.
     **/
    static parse(options: {
        window: IBrowserWindow;
        responseType: string;
        data?: Buffer;
        contentType?: string;
    }): ArrayBuffer | Blob | IDocument | object | string | null;
}
//# sourceMappingURL=XMLHttpRequestResponseDataParser.d.ts.map