import IBrowserWindow from './IBrowserWindow.cjs';
import IBrowserFrame from '../browser/types/IBrowserFrame.cjs';
import ICrossOriginBrowserWindow from './ICrossOriginBrowserWindow.cjs';
/**
 * Window page open handler.
 */
export default class WindowPageOpenUtility {
    /**
     * Opens a page.
     *
     * @param browserFrame Browser frame.
     * @param [options] Options.
     * @param [options.url] URL.
     * @param [options.target] Target.
     * @param [options.features] Window features.
     */
    static openPage(browserFrame: IBrowserFrame, options?: {
        url?: string;
        target?: string;
        features?: string;
    }): IBrowserWindow | ICrossOriginBrowserWindow | null;
    /**
     * Returns window features.
     *
     * @param features Window features string.
     * @returns Window features.
     */
    private static getWindowFeatures;
}
//# sourceMappingURL=WindowPageOpenUtility.d.ts.map