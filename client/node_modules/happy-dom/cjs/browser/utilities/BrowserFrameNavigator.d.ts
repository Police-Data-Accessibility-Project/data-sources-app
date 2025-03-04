import IBrowserFrame from '../types/IBrowserFrame.cjs';
import IGoToOptions from '../types/IGoToOptions.cjs';
import IResponse from '../../fetch/types/IResponse.cjs';
import IBrowserWindow from '../../window/IBrowserWindow.cjs';
/**
 * Browser frame navigation utility.
 */
export default class BrowserFrameNavigator {
    /**
     * Go to a page.
     *
     * @throws Error if the request can't be resolved (because of SSL error or similar). It will not throw if the response is not ok.
     * @param windowClass Window class.
     * @param frame Frame.
     * @param url URL.
     * @param [options] Options.
     * @returns Response.
     */
    static goto(windowClass: new (browserFrame: IBrowserFrame, options?: {
        url?: string;
        width?: number;
        height?: number;
    }) => IBrowserWindow, frame: IBrowserFrame, url: string, options?: IGoToOptions): Promise<IResponse | null>;
}
//# sourceMappingURL=BrowserFrameNavigator.d.ts.map