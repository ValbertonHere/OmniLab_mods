import { getScale, getSize } from "./common.js";

/**
 * @typedef {object} Breakpoint
 * @property {number} weight
 * @property {string} className
 * @property {number} width
 * @property {number} height
 */

/** @type {Object.<string, Breakpoint>} */
const breakpoints = {
    extraSmall: {
        weight: 0,
        className: "mediaExtraSmall",
        width: 1280,
        height: 768,
    },
    small: {
        weight: 1,
        className: "mediaSmall",
        width: 1366,
        height: 768,
    },
    medium: {
        weight: 2,
        className: "mediaMedium",
        width: 1600,
        height: 900,
    },
    large: {
        weight: 3,
        className: "mediaLarge",
        width: 1920,
        height: 1080,
    },
    extraLarge: {
        weight: 4,
        className: "mediaExtraLarge",
        width: 2560,
        height: 1440,
    },
};

/**
 * Updates the CSS classes of the '.media-wrapper' element based on screen dimensions and scale.
 * @param {{width: number, height: number, scale: number}} media - The media context object.
 */
const updateWrapper = (media) => {
    const wrapper = document.querySelector(".media-wrapper");
    if (!wrapper) {
        console.error("updateWrapper: '.media-wrapper' not found.");
        return;
    }

    const classList = new Set(["media-wrapper"]);

    const sortedBreakpoints = Object.values(breakpoints).sort((a, b) => a.weight - b.weight);
    for (const bp of sortedBreakpoints) {
        const fitsWidth = bp.width <= media.width / media.scale;
        const fitsHeight = bp.height <= media.height / media.scale;

        if (fitsWidth) {
            classList.add(`${bp.className}Width`);
        }
        if (fitsHeight) {
            classList.add(`${bp.className}Height`);
        }
        if (fitsWidth && fitsHeight) {
            classList.add(bp.className);
        }
    }

    if (media.scale > 1) {
        classList.add("media-upscale");
    }

    wrapper.className = Array.from(classList).join(" ");
};

/**
 * @typedef {object} MediaContextInstance
 * @property {number} width
 * @property {number} height
 * @property {number} scale
 * @property {boolean} customWrapper
 * @property {function(): void} subscribe
 * @property {function(): void} unsubscribe
 * @property {function(function({width: number, height: number, scale: number}): void): void} onUpdate
 */

/**
 * Creates a media context for handling screen size and scale changes.
 * @param {boolean} [autoUpdateWrapper=false] - If true, automatically updates the '.media-wrapper' element with CSS classes.
 * @returns {MediaContextInstance}
 */
const MediaContext = (autoUpdateWrapper = false) => {
    const context = {
        width: 0,
        height: 0,
        scale: 0,
        autoUpdateWrapper: autoUpdateWrapper,
        onUpdateCallbacks: [],

        /**
         * Subscribes to media events for resize and scale changes.
         */
        subscribe() {
            engine.on("clientResized", this.onClientResized.bind(this));
            engine.on("self.onScaleUpdated", this.onScaleUpdated.bind(this));
        },

        /**
         * Unsubscribes from media events.
         */
        unsubscribe() {
            engine.off("clientResized", this.onClientResized.bind(this));
            engine.off("self.onScaleUpdated", this.onScaleUpdated.bind(this));
        },

        /**
         * Handles client resize events.
         * @param {number} actualWidth - The new width.
         * @param {number} actualHeight - The new height.
         */
        onClientResized(actualWidth, actualHeight) {
            this.width = actualWidth;
            this.height = actualHeight;
            this.notifyUpdate();
        },

        /**
         * Handles scale update events.
         * @param {number} actualScale - The new scale factor.
         */
        onScaleUpdated(actualScale) {
            this.scale = actualScale;
            this.notifyUpdate();
        },

        /**
         * Registers a callback for media updates.
         * @param {function(object): void} callback - The function to be called on media changes.
         */
        onUpdate(callback) {
            this.onUpdateCallbacks.push(callback);
        },

        /**
         * Notifies all registered callbacks about media changes.
         */
        notifyUpdate() {
            if (this.autoUpdateWrapper) {
                updateWrapper(this);
            }
            for (const cb of this.onUpdateCallbacks) {
                cb({
                    width: this.width,
                    height: this.height,
                    scale: this.scale,
                });
            }
        },
    };

    engine.whenReady.then(() => {
        const size = getSize();
        context.width = size.width;
        context.height = size.height;
        context.scale = getScale();
        context.notifyUpdate();
    });

    return context;
};

// Export public functions and constants
export { MediaContext };
