import IBrowserFrame from '../../browser/types/IBrowserFrame.cjs';
import IBrowserWindow from '../../window/IBrowserWindow.cjs';
import Request from '../Request.cjs';
import IHeaders from '../types/IHeaders.cjs';
/**
 * Fetch request header utility.
 */
export default class FetchRequestHeaderUtility {
    /**
     * Validates request headers.
     *
     * @param headers Headers.
     */
    static removeForbiddenHeaders(headers: IHeaders): void;
    /**
     * Returns "true" if the header is forbidden.
     *
     * @param name Header name.
     * @returns "true" if the header is forbidden.
     */
    static isHeaderForbidden(name: string): boolean;
    /**
     * Returns request headers.
     *
     * @param options Options.
     * @param options.browserFrame Browser frame.
     * @param options.window Window.
     * @param options.request Request.
     * @returns Headers.
     */
    static getRequestHeaders(options: {
        browserFrame: IBrowserFrame;
        window: IBrowserWindow;
        request: Request;
    }): {
        [key: string]: string;
    };
}
//# sourceMappingURL=FetchRequestHeaderUtility.d.ts.map