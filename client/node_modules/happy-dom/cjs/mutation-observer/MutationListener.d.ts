import IMutationObserverInit from './IMutationObserverInit.cjs';
import MutationObserver from './MutationObserver.cjs';
import MutationRecord from './MutationRecord.cjs';
import INode from '../nodes/node/INode.cjs';
import IBrowserWindow from '../window/IBrowserWindow.cjs';
/**
 * Mutation Observer Listener.
 */
export default class MutationListener {
    #private;
    readonly target: INode;
    options: IMutationObserverInit;
    /**
     * Constructor.
     *
     * @param init Options.
     * @param init.window Window.
     * @param init.options Options.
     * @param init.target Target.
     * @param init.observer Observer.
     * @param init.callback Callback.
     */
    constructor(init: {
        window: IBrowserWindow;
        options: IMutationObserverInit;
        target: INode;
        observer: MutationObserver;
        callback: (record: MutationRecord[], observer: MutationObserver) => void;
    });
    /**
     * Reports mutations.
     *
     * @param record Record.
     */
    report(record: MutationRecord): void;
    /**
     * Destroys the listener.
     */
    takeRecords(): MutationRecord[];
    /**
     * Destroys the listener.
     */
    destroy(): void;
}
//# sourceMappingURL=MutationListener.d.ts.map