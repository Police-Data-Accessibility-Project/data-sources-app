"use strict";
var __classPrivateFieldGet = (this && this.__classPrivateFieldGet) || function (receiver, state, kind, f) {
    if (kind === "a" && !f) throw new TypeError("Private accessor was defined without a getter");
    if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
    return kind === "m" ? f : kind === "a" ? f.call(receiver) : f ? f.value : state.get(receiver);
};
var __classPrivateFieldSet = (this && this.__classPrivateFieldSet) || function (receiver, state, value, kind, f) {
    if (kind === "m") throw new TypeError("Private method is not writable");
    if (kind === "a" && !f) throw new TypeError("Private accessor was defined without a setter");
    if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
    return (kind === "a" ? f.call(receiver, value) : f ? f.value = value : state.set(receiver, value)), value;
};
var _Storage_store;
Object.defineProperty(exports, "__esModule", { value: true });
/**
 * Storage.
 *
 * @see https://developer.mozilla.org/en-US/docs/Web/API/Storage
 */
class Storage {
    constructor() {
        _Storage_store.set(this, {});
    }
    /**
     * Returns length.
     *
     * @returns Length.
     */
    get length() {
        return Object.keys(__classPrivateFieldGet(this, _Storage_store, "f")).length;
    }
    /**
     * Returns name of the nth key.
     *
     * @param index Index.
     * @returns Name.
     */
    key(index) {
        const name = Object.keys(__classPrivateFieldGet(this, _Storage_store, "f"))[index];
        return name === undefined ? null : name;
    }
    /**
     * Sets item.
     *
     * @param name Name.
     * @param item Item.
     */
    setItem(name, item) {
        __classPrivateFieldGet(this, _Storage_store, "f")[name] = item;
    }
    /**
     * Returns item.
     *
     * @param name Name.
     * @returns Item.
     */
    getItem(name) {
        return __classPrivateFieldGet(this, _Storage_store, "f")[name] === undefined ? null : __classPrivateFieldGet(this, _Storage_store, "f")[name];
    }
    /**
     * Removes item.
     *
     * @param name Name.
     */
    removeItem(name) {
        delete __classPrivateFieldGet(this, _Storage_store, "f")[name];
    }
    /**
     * Clears storage.
     */
    clear() {
        __classPrivateFieldSet(this, _Storage_store, {}, "f");
    }
}
_Storage_store = new WeakMap();
exports.default = Storage;
//# sourceMappingURL=Storage.cjs.map