/// <reference types="node" />
import IHeaders from '../../types/IHeaders.cjs';
export default interface ICachableResponse {
    status: number;
    statusText: string;
    url: string;
    headers: IHeaders;
    body: Buffer | null;
    waitingForBody: boolean;
}
//# sourceMappingURL=ICachableResponse.d.ts.map