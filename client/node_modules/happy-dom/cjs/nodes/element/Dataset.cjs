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
Object.defineProperty(exports, "__esModule", { value: true });
const PropertySymbol = __importStar(require("../../PropertySymbol.cjs"));
/**
 * Dataset helper proxy.
 *
 * Reference:
 * https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/dataset
 */
class Dataset {
    /**
     * @param element The parent element.
     */
    constructor(element) {
        // Build the initial dataset record from all data attributes.
        const dataset = {};
        for (let i = 0, max = element[PropertySymbol.attributes].length; i < max; i++) {
            const attribute = element[PropertySymbol.attributes][i];
            if (attribute[PropertySymbol.name].startsWith('data-')) {
                const key = Dataset.kebabToCamelCase(attribute[PropertySymbol.name].replace('data-', ''));
                dataset[key] = attribute[PropertySymbol.value];
            }
        }
        // Documentation for Proxy:
        // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Proxy
        this.proxy = new Proxy(dataset, {
            get(dataset, key) {
                const attribute = element[PropertySymbol.attributes].getNamedItem('data-' + Dataset.camelCaseToKebab(key));
                if (attribute) {
                    return (dataset[key] = attribute[PropertySymbol.value]);
                }
                delete dataset[key];
                return undefined;
            },
            set(dataset, key, value) {
                element.setAttribute('data-' + Dataset.camelCaseToKebab(key), value);
                dataset[key] = value;
                return true;
            },
            deleteProperty(dataset, key) {
                element[PropertySymbol.attributes][PropertySymbol.removeNamedItem]('data-' + Dataset.camelCaseToKebab(key));
                return delete dataset[key];
            },
            ownKeys(dataset) {
                // According to Mozilla we have to update the dataset object (target) to contain the same keys as what we return:
                // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Proxy/Proxy/ownKeys
                // "The result List must contain the keys of all non-configurable own properties of the target object."
                const keys = [];
                const deleteKeys = [];
                for (let i = 0, max = element[PropertySymbol.attributes].length; i < max; i++) {
                    const attribute = element[PropertySymbol.attributes][i];
                    if (attribute[PropertySymbol.name].startsWith('data-')) {
                        const key = Dataset.kebabToCamelCase(attribute[PropertySymbol.name].replace('data-', ''));
                        keys.push(key);
                        dataset[key] = attribute[PropertySymbol.value];
                        if (!dataset[key]) {
                            deleteKeys.push(key);
                        }
                    }
                }
                for (const key of deleteKeys) {
                    delete dataset[key];
                }
                return keys;
            },
            has(_dataset, key) {
                return !!element[PropertySymbol.attributes].getNamedItem('data-' + Dataset.camelCaseToKebab(key));
            }
        });
    }
    /**
     * Transforms a kebab cased string to camel case.
     *
     * @param text Text string.
     * @returns Camel cased string.
     */
    static kebabToCamelCase(text) {
        const parts = text.split('-');
        for (let i = 0, max = parts.length; i < max; i++) {
            parts[i] = i > 0 ? parts[i].charAt(0).toUpperCase() + parts[i].slice(1) : parts[i];
        }
        return parts.join('');
    }
    /**
     * Transforms a camel cased string to kebab case.
     *
     * @param text Text string.
     * @returns Kebab cased string.
     */
    static camelCaseToKebab(text) {
        return text
            .toString()
            .replace(/[A-Z]+(?![a-z])|[A-Z]/g, ($, ofs) => (ofs ? '-' : '') + $.toLowerCase());
    }
}
exports.default = Dataset;
//# sourceMappingURL=Dataset.cjs.map