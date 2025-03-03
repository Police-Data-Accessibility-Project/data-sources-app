import IBrowserWindow from '../window/IBrowserWindow.cjs';
import Event from './Event.cjs';
import IUIEventInit from './IUIEventInit.cjs';
/**
 *
 */
export default class UIEvent extends Event {
    static NONE: number;
    static CAPTURING_PHASE: number;
    static AT_TARGET: number;
    static BUBBLING_PHASE: number;
    readonly detail: number;
    readonly layerX: number;
    readonly layerY: number;
    readonly pageX: number;
    readonly pageY: number;
    readonly view: IBrowserWindow | null;
    /**
     * Constructor.
     *
     * @param type Event type.
     * @param [eventInit] Event init.
     */
    constructor(type: string, eventInit?: IUIEventInit | null);
}
//# sourceMappingURL=UIEvent.d.ts.map