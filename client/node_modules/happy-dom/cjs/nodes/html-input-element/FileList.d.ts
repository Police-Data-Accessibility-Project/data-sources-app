import File from '../../file/File.cjs';
import IFileList from './IFileList.cjs';
/**
 * FileList.
 *
 * @see https://developer.mozilla.org/en-US/docs/Web/API/FileList
 */
export default class FileList extends Array implements IFileList<File> {
    /**
     * Constructor.
     */
    constructor();
    /**
     * Returns `Symbol.toStringTag`.
     *
     * @returns `Symbol.toStringTag`.
     */
    get [Symbol.toStringTag](): string;
    /**
     * Returns item by index.
     *
     * @param index Index.
     * @returns Item.
     */
    item(index: number): File | null;
}
//# sourceMappingURL=FileList.d.ts.map