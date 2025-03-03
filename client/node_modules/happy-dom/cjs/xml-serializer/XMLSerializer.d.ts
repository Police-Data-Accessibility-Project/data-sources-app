import INode from '../nodes/node/INode.cjs';
/**
 * Utility for converting an element to string.
 */
export default class XMLSerializer {
    private options;
    /**
     * Constructor.
     *
     * @param [options] Options.
     * @param [options.includeShadowRoots] Include shadow roots.
     * @param [options.escapeEntities] Escape text.
     */
    constructor(options?: {
        includeShadowRoots?: boolean;
        escapeEntities?: boolean;
    });
    /**
     * Renders an element as HTML.
     *
     * @param root Root element.
     * @returns Result.
     */
    serializeToString(root: INode): string;
    /**
     * Returns attributes as a string.
     *
     * @param element Element.
     * @returns Attributes.
     */
    private getAttributes;
}
//# sourceMappingURL=XMLSerializer.d.ts.map