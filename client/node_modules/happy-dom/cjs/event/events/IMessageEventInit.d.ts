import IEventInit from '../IEventInit.cjs';
import IBrowserWindow from '../../window/IBrowserWindow.cjs';
import IMessagePort from '../IMessagePort.cjs';
export default interface IMessageEventInit extends IEventInit {
    data?: unknown | null;
    origin?: string;
    lastEventId?: string;
    source?: IBrowserWindow | null;
    ports?: IMessagePort[];
}
//# sourceMappingURL=IMessageEventInit.d.ts.map