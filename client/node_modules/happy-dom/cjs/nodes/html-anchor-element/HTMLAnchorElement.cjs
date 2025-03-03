"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
var _a, _b, _c;
Object.defineProperty(exports, "__esModule", { value: true });
const HTMLElement_js_1 = __importDefault(require("../html-element/HTMLElement.cjs"));
const PropertySymbol = __importStar(require("../../PropertySymbol.cjs"));
const DOMTokenList_js_1 = __importDefault(require("../../dom-token-list/DOMTokenList.cjs"));
const HTMLAnchorElementUtility_js_1 = __importDefault(require("./HTMLAnchorElementUtility.cjs"));
const HTMLAnchorElementNamedNodeMap_js_1 = __importDefault(require("./HTMLAnchorElementNamedNodeMap.cjs"));
const EventPhaseEnum_js_1 = __importDefault(require("../../event/EventPhaseEnum.cjs"));
/**
 * HTML Anchor Element.
 *
 * Reference:
 * https://developer.mozilla.org/en-US/docs/Web/API/HTMLAnchorElement.
 */
class HTMLAnchorElement extends HTMLElement_js_1.default {
    constructor() {
        super(...arguments);
        this[_a] = new HTMLAnchorElementNamedNodeMap_js_1.default(this);
        this[_b] = null;
        this[_c] = null;
    }
    /**
     * Returns download.
     *
     * @returns download.
     */
    get download() {
        return this.getAttribute('download') || '';
    }
    /**
     * Sets download.
     *
     * @param download Download.
     */
    set download(download) {
        this.setAttribute('download', download);
    }
    /**
     * Returns hash.
     *
     * @returns Hash.
     */
    get hash() {
        return this[PropertySymbol.url]?.hash ?? '';
    }
    /**
     * Sets hash.
     *
     * @param hash Hash.
     */
    set hash(hash) {
        if (this[PropertySymbol.url] && !HTMLAnchorElementUtility_js_1.default.isBlobURL(this[PropertySymbol.url])) {
            this[PropertySymbol.url].hash = hash;
            this.setAttribute('href', this[PropertySymbol.url].toString());
        }
    }
    /**
     * Returns href.
     *
     * @returns Href.
     */
    get href() {
        if (this[PropertySymbol.url]) {
            return this[PropertySymbol.url].toString();
        }
        return this.getAttribute('href') || '';
    }
    /**
     * Sets href.
     *
     * @param href Href.
     */
    set href(href) {
        this.setAttribute('href', href);
    }
    /**
     * Returns hreflang.
     *
     * @returns Hreflang.
     */
    get hreflang() {
        return this.getAttribute('hreflang') || '';
    }
    /**
     * Sets hreflang.
     *
     * @param hreflang Hreflang.
     */
    set hreflang(hreflang) {
        this.setAttribute('hreflang', hreflang);
    }
    /**
     * Returns the hyperlink's URL's origin.
     *
     * @returns Origin.
     */
    get origin() {
        return this[PropertySymbol.url]?.origin ?? '';
    }
    /**
     * Returns ping.
     *
     * @returns Ping.
     */
    get ping() {
        return this.getAttribute('ping') || '';
    }
    /**
     * Sets ping.
     *
     * @param ping Ping.
     */
    set ping(ping) {
        this.setAttribute('ping', ping);
    }
    /**
     * Returns protocol.
     *
     * @returns Protocol.
     */
    get protocol() {
        return this[PropertySymbol.url]?.protocol ?? '';
    }
    /**
     * Sets protocol.
     *
     * @param protocol Protocol.
     */
    set protocol(protocol) {
        if (this[PropertySymbol.url] && !HTMLAnchorElementUtility_js_1.default.isBlobURL(this[PropertySymbol.url])) {
            this[PropertySymbol.url].protocol = protocol;
            this.setAttribute('href', this[PropertySymbol.url].toString());
        }
    }
    /**
     * Returns username.
     *
     * @returns Username.
     */
    get username() {
        return this[PropertySymbol.url]?.username ?? '';
    }
    /**
     * Sets username.
     *
     * @param username Username.
     */
    set username(username) {
        if (this[PropertySymbol.url] &&
            !HTMLAnchorElementUtility_js_1.default.isBlobURL(this[PropertySymbol.url]) &&
            this[PropertySymbol.url].host &&
            this[PropertySymbol.url].protocol != 'file') {
            this[PropertySymbol.url].username = username;
            this.setAttribute('href', this[PropertySymbol.url].toString());
        }
    }
    /**
     * Returns password.
     *
     * @returns Password.
     */
    get password() {
        return this[PropertySymbol.url]?.password ?? '';
    }
    /**
     * Sets password.
     *
     * @param password Password.
     */
    set password(password) {
        if (this[PropertySymbol.url] &&
            !HTMLAnchorElementUtility_js_1.default.isBlobURL(this[PropertySymbol.url]) &&
            this[PropertySymbol.url].host &&
            this[PropertySymbol.url].protocol != 'file') {
            this[PropertySymbol.url].password = password;
            this.setAttribute('href', this[PropertySymbol.url].toString());
        }
    }
    /**
     * Returns pathname.
     *
     * @returns Pathname.
     */
    get pathname() {
        return this[PropertySymbol.url]?.pathname ?? '';
    }
    /**
     * Sets pathname.
     *
     * @param pathname Pathname.
     */
    set pathname(pathname) {
        if (this[PropertySymbol.url] && !HTMLAnchorElementUtility_js_1.default.isBlobURL(this[PropertySymbol.url])) {
            this[PropertySymbol.url].pathname = pathname;
            this.setAttribute('href', this[PropertySymbol.url].toString());
        }
    }
    /**
     * Returns port.
     *
     * @returns Port.
     */
    get port() {
        return this[PropertySymbol.url]?.port ?? '';
    }
    /**
     * Sets port.
     *
     * @param port Port.
     */
    set port(port) {
        if (this[PropertySymbol.url] &&
            !HTMLAnchorElementUtility_js_1.default.isBlobURL(this[PropertySymbol.url]) &&
            this[PropertySymbol.url].host &&
            this[PropertySymbol.url].protocol != 'file') {
            this[PropertySymbol.url].port = port;
            this.setAttribute('href', this[PropertySymbol.url].toString());
        }
    }
    /**
     * Returns host.
     *
     * @returns Host.
     */
    get host() {
        return this[PropertySymbol.url]?.host ?? '';
    }
    /**
     * Sets host.
     *
     * @param host Host.
     */
    set host(host) {
        if (this[PropertySymbol.url] && !HTMLAnchorElementUtility_js_1.default.isBlobURL(this[PropertySymbol.url])) {
            this[PropertySymbol.url].host = host;
            this.setAttribute('href', this[PropertySymbol.url].toString());
        }
    }
    /**
     * Returns hostname.
     *
     * @returns Hostname.
     */
    get hostname() {
        return this[PropertySymbol.url]?.hostname ?? '';
    }
    /**
     * Sets hostname.
     *
     * @param hostname Hostname.
     */
    set hostname(hostname) {
        if (this[PropertySymbol.url] && !HTMLAnchorElementUtility_js_1.default.isBlobURL(this[PropertySymbol.url])) {
            this[PropertySymbol.url].hostname = hostname;
            this.setAttribute('href', this[PropertySymbol.url].toString());
        }
    }
    /**
     * Returns referrerPolicy.
     *
     * @returns Referrer Policy.
     */
    get referrerPolicy() {
        return this.getAttribute('referrerPolicy') || '';
    }
    /**
     * Sets referrerPolicy.
     *
     * @param referrerPolicy Referrer Policy.
     */
    set referrerPolicy(referrerPolicy) {
        this.setAttribute('referrerPolicy', referrerPolicy);
    }
    /**
     * Returns rel.
     *
     * @returns Rel.
     */
    get rel() {
        return this.getAttribute('rel') || '';
    }
    /**
     * Sets rel.
     *
     * @param rel Rel.
     */
    set rel(rel) {
        this.setAttribute('rel', rel);
    }
    /**
     * Returns rel list.
     *
     * @returns Rel list.
     */
    get relList() {
        if (!this[PropertySymbol.relList]) {
            this[PropertySymbol.relList] = new DOMTokenList_js_1.default(this, 'rel');
        }
        return this[PropertySymbol.relList];
    }
    /**
     * Returns search.
     *
     * @returns Search.
     */
    get search() {
        return this[PropertySymbol.url]?.search ?? '';
    }
    /**
     * Sets search.
     *
     * @param search Search.
     */
    set search(search) {
        if (this[PropertySymbol.url] && !HTMLAnchorElementUtility_js_1.default.isBlobURL(this[PropertySymbol.url])) {
            this[PropertySymbol.url].search = search;
            this.setAttribute('href', this[PropertySymbol.url].toString());
        }
    }
    /**
     * Returns target.
     *
     * @returns target.
     */
    get target() {
        return this.getAttribute('target') || '';
    }
    /**
     * Sets target.
     *
     * @param target Target.
     */
    set target(target) {
        this.setAttribute('target', target);
    }
    /**
     * Returns text.
     *
     * @returns text.
     */
    get text() {
        return this.textContent;
    }
    /**
     * Sets text.
     *
     * @param text Text.
     */
    set text(text) {
        this.textContent = text;
    }
    /**
     * Returns type.
     *
     * @returns Type.
     */
    get type() {
        return this.getAttribute('type') || '';
    }
    /**
     * Sets type.
     *
     * @param type Type.
     */
    set type(type) {
        this.setAttribute('type', type);
    }
    /**
     * @override
     */
    toString() {
        return this.href;
    }
    /**
     * @override
     */
    dispatchEvent(event) {
        const returnValue = super.dispatchEvent(event);
        if (event.type === 'click' &&
            (event.eventPhase === EventPhaseEnum_js_1.default.atTarget ||
                event.eventPhase === EventPhaseEnum_js_1.default.bubbling) &&
            !event.defaultPrevented &&
            this[PropertySymbol.url]) {
            this[PropertySymbol.ownerDocument][PropertySymbol.ownerWindow].open(this[PropertySymbol.url].toString(), this.target || '_self');
            if (this[PropertySymbol.ownerDocument][PropertySymbol.ownerWindow].closed) {
                event.stopImmediatePropagation();
            }
        }
        return returnValue;
    }
}
_a = PropertySymbol.attributes, _b = PropertySymbol.relList, _c = PropertySymbol.url;
exports.default = HTMLAnchorElement;
//# sourceMappingURL=HTMLAnchorElement.cjs.map