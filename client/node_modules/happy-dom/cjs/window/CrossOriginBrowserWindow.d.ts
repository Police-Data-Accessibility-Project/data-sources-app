import EventTarget from '../event/EventTarget.cjs';
import IBrowserWindow from './IBrowserWindow.cjs';
import Location from '../url/Location.cjs';
import ICrossOriginBrowserWindow from './ICrossOriginBrowserWindow.cjs';
/**
 * Browser window with limited access due to CORS restrictions in iframes.
 */
export default class CrossOriginBrowserWindow extends EventTarget implements ICrossOriginBrowserWindow {
    #private;
    readonly self: this;
    readonly window: this;
    readonly parent: IBrowserWindow | ICrossOriginBrowserWindow;
    readonly top: IBrowserWindow | ICrossOriginBrowserWindow;
    readonly location: Location;
    /**
     * Constructor.
     *
     * @param target Target window.
     * @param [parent] Parent window.
     */
    constructor(target: IBrowserWindow, parent?: IBrowserWindow);
    /**
     * Returns the opener.
     *
     * @returns Opener.
     */
    get opener(): IBrowserWindow | ICrossOriginBrowserWindow | null;
    /**
     * Returns the closed state.
     *
     * @returns Closed state.
     */
    get closed(): boolean;
    /**
     * Shifts focus away from the window.
     */
    blur(): void;
    /**
     * Gives focus to the window.
     */
    focus(): void;
    /**
     * Closes the window.
     */
    close(): void;
    /**
     * Safely enables cross-origin communication between Window objects; e.g., between a page and a pop-up that it spawned, or between a page and an iframe embedded within it.
     *
     * @param message Message.
     * @param [targetOrigin=*] Target origin.
     * @param transfer Transfer. Not implemented.
     */
    postMessage(message: unknown, targetOrigin?: string, transfer?: unknown[]): void;
}
//# sourceMappingURL=CrossOriginBrowserWindow.d.ts.map