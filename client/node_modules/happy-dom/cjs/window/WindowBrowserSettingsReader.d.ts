import IBrowserSettings from '../browser/types/IBrowserSettings.cjs';
import IBrowserWindow from './IBrowserWindow.cjs';
/**
 * Browser settings reader that will allow to read settings more securely as it is not possible to override a settings object to make DOM functionality act on it.
 */
export default class WindowBrowserSettingsReader {
    #private;
    /**
     * Returns browser settings.
     *
     * @param window Window.
     * @returns Settings.
     */
    static getSettings(window: IBrowserWindow): IBrowserSettings | null;
    /**
     * Sets browser settings.
     *
     * @param window Window.
     * @param settings Settings.
     */
    static setSettings(window: IBrowserWindow, settings: IBrowserSettings): void;
    /**
     * Removes browser settings.
     *
     * @param window Window.
     */
    static removeSettings(window: IBrowserWindow): void;
}
//# sourceMappingURL=WindowBrowserSettingsReader.d.ts.map