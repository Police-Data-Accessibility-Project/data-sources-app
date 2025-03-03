/// <reference types="node" />
import IHeaders from './IHeaders.cjs';
/**
 * Fetch response.
 *
 * @see https://developer.mozilla.org/en-US/docs/Web/API/Response/Response
 */
export default interface ISyncResponse {
    status: number;
    statusText: string;
    ok: boolean;
    url: string;
    redirected: boolean;
    headers: IHeaders;
    body: Buffer;
}
//# sourceMappingURL=ISyncResponse.d.ts.map