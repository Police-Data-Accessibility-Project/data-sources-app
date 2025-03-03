import IBrowserWindow from '../../window/IBrowserWindow.cjs';
import IBrowserFrame from '../../browser/types/IBrowserFrame.cjs';
import ICrossOriginBrowserWindow from '../../window/ICrossOriginBrowserWindow.cjs';
import IHTMLIFrameElement from './IHTMLIFrameElement.cjs';
/**
 * HTML Iframe page loader.
 */
export default class HTMLIFrameElementPageLoader {
    #private;
    /**
     * Constructor.
     *
     * @param options Options.
     * @param options.element Iframe element.
     * @param options.browserParentFrame Main browser frame.
     * @param options.contentWindowContainer Content window container.
     * @param options.contentWindowContainer.window Content window.
     */
    constructor(options: {
        element: IHTMLIFrameElement;
        browserParentFrame: IBrowserFrame;
        contentWindowContainer: {
            window: IBrowserWindow | ICrossOriginBrowserWindow | null;
        };
    });
    /**
     * Loads an iframe page.
     */
    loadPage(): void;
    /**
     * Unloads an iframe page.
     */
    unloadPage(): void;
}
//# sourceMappingURL=HTMLIFrameElementPageLoader.d.ts.map