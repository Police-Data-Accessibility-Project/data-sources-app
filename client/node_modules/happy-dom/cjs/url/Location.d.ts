import URL from './URL.cjs';
import IBrowserFrame from '../browser/types/IBrowserFrame.cjs';
import * as PropertySymbol from '../PropertySymbol.cjs';
/**
 * Location.
 */
export default class Location extends URL {
    #private;
    /**
     * Constructor.
     *
     * @param browserFrame Browser frame.
     * @param url URL.
     */
    constructor(browserFrame: IBrowserFrame, url: string);
    /**
     * Override set href.
     */
    set href(url: string);
    /**
     * Override set href.
     */
    get href(): string;
    /**
     * Replaces the current resource with the one at the provided URL. The difference from the assign() method is that after using replace() the current page will not be saved in session History, meaning the user won't be able to use the back button to navigate to it.
     *
     * @param url URL.
     */
    replace(url: string): void;
    /**
     * Loads the resource at the URL provided in parameter.
     *
     * @param url URL.
     */
    assign(url: string): void;
    /**
     * Reloads the resource from the current URL.
     */
    reload(): void;
    /**
     * Replaces the current URL state with the provided one without navigating to the new URL.
     *
     * @param browserFrame Browser frame that must match the current one as validation.
     * @param url URL.
     */
    [PropertySymbol.setURL](browserFrame: IBrowserFrame, url: string): void;
}
//# sourceMappingURL=Location.d.ts.map