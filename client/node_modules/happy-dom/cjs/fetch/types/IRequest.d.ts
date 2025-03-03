/// <reference types="node" />
/// <reference types="node" />
import IHeaders from './IHeaders.cjs';
import IBlob from '../../file/IBlob.cjs';
import AbortSignal from '../AbortSignal.cjs';
import Stream from 'stream';
import IRequestReferrerPolicy from './IRequestReferrerPolicy.cjs';
import IRequestRedirect from './IRequestRedirect.cjs';
import IRequestCredentials from './IRequestCredentials.cjs';
import FormData from '../../form-data/FormData.cjs';
/**
 * Fetch request.
 */
export default interface IRequest {
    readonly headers: IHeaders;
    readonly method: string;
    readonly redirect: IRequestRedirect;
    readonly referrer: string;
    readonly url: string;
    readonly body: Stream.Readable | null;
    readonly bodyUsed: boolean;
    readonly referrerPolicy: IRequestReferrerPolicy;
    readonly signal: AbortSignal | null;
    readonly credentials: IRequestCredentials;
    /**
     * Returns array buffer.
     *
     * @returns Array buffer.
     */
    arrayBuffer(): Promise<ArrayBuffer>;
    /**
     * Returns blob.
     *
     * @returns Blob.
     */
    blob(): Promise<IBlob>;
    /**
     * Returns buffer.
     *
     * @returns Buffer.
     */
    buffer(): Promise<Buffer>;
    /**
     * Returns text.
     *
     * @returns Text.
     */
    text(): Promise<string>;
    /**
     * Returns json.
     *
     * @returns JSON.
     */
    json(): Promise<string>;
    /**
     * Returns FormData.
     *
     * @returns FormData.
     */
    formData(): Promise<FormData>;
    /**
     * Clones request.
     *
     * @returns Clone.
     */
    clone(): IRequest;
}
//# sourceMappingURL=IRequest.d.ts.map