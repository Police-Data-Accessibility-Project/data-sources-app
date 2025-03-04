/// <reference types="node" />
import BrowserPage from './BrowserPage.cjs';
import * as PropertySymbol from '../PropertySymbol.cjs';
import AsyncTaskManager from '../async-task-manager/AsyncTaskManager.cjs';
import IBrowserFrame from './types/IBrowserFrame.cjs';
import BrowserWindow from '../window/BrowserWindow.cjs';
import IBrowserWindow from '../window/IBrowserWindow.cjs';
import ICrossOriginBrowserWindow from '../window/ICrossOriginBrowserWindow.cjs';
import IResponse from '../fetch/types/IResponse.cjs';
import IGoToOptions from './types/IGoToOptions.cjs';
import { Script } from 'vm';
import IReloadOptions from './types/IReloadOptions.cjs';
import BrowserFrameExceptionObserver from './utilities/BrowserFrameExceptionObserver.cjs';
import IDocument from '../nodes/document/IDocument.cjs';
/**
 * Browser frame.
 */
export default class BrowserFrame implements IBrowserFrame {
    readonly childFrames: BrowserFrame[];
    readonly parentFrame: BrowserFrame | null;
    readonly page: BrowserPage;
    readonly window: BrowserWindow;
    [PropertySymbol.asyncTaskManager]: AsyncTaskManager;
    [PropertySymbol.exceptionObserver]: BrowserFrameExceptionObserver | null;
    [PropertySymbol.listeners]: {
        navigation: Array<() => void>;
    };
    [PropertySymbol.openerFrame]: IBrowserFrame | null;
    [PropertySymbol.openerWindow]: IBrowserWindow | ICrossOriginBrowserWindow | null;
    [PropertySymbol.popup]: boolean;
    /**
     * Constructor.
     *
     * @param page Page.
     */
    constructor(page: BrowserPage);
    /**
     * Returns the content.
     *
     * @returns Content.
     */
    get content(): string;
    /**
     * Sets the content.
     *
     * @param content Content.
     */
    set content(content: string);
    /**
     * Returns the URL.
     *
     * @returns URL.
     */
    get url(): string;
    /**
     * Sets the content.
     *
     * @param url URL.
     */
    set url(url: string);
    /**
     * Returns document.
     *
     * @returns Document.
     */
    get document(): IDocument;
    /**
     * Returns a promise that is resolved when all resources has been loaded, fetch has completed, and all async tasks such as timers are complete.
     */
    waitUntilComplete(): Promise<void>;
    /**
     * Returns a promise that is resolved when the frame has navigated and the response HTML has been written to the document.
     */
    waitForNavigation(): Promise<void>;
    /**
     * Aborts all ongoing operations.
     */
    abort(): Promise<void>;
    /**
     * Evaluates code or a VM Script in the page's context.
     *
     * @param script Script.
     * @returns Result.
     */
    evaluate(script: string | Script): any;
    /**
     * Go to a page.
     *
     * @param url URL.
     * @param [options] Options.
     * @returns Response.
     */
    goto(url: string, options?: IGoToOptions): Promise<IResponse | null>;
    /**
     * Reloads the current frame.
     *
     * @param [options] Options.
     * @returns Response.
     */
    reload(options: IReloadOptions): Promise<IResponse | null>;
}
//# sourceMappingURL=BrowserFrame.d.ts.map