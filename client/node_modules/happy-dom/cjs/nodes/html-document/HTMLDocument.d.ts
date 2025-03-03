import IBrowserFrame from '../../browser/types/IBrowserFrame.cjs';
import IBrowserWindow from '../../window/IBrowserWindow.cjs';
import Document from '../document/Document.cjs';
/**
 * Document.
 */
export default class HTMLDocument extends Document {
    /**
     * Constructor.
     *
     * @param injected Injected properties.
     * @param injected.browserFrame Browser frame.
     * @param injected.window Window.
     */
    constructor(injected: {
        browserFrame: IBrowserFrame;
        window: IBrowserWindow;
    });
}
//# sourceMappingURL=HTMLDocument.d.ts.map