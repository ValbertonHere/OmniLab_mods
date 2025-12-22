// Assumes global `engine` + `viewEnv` are injected by the game host.

export const client = {
  getSize(unit = "px") {
    return unit === "rem" ? viewEnv.getClientSizeRem() : viewEnv.getClientSizePx();
  },
  getMouseGlobalPosition(unit = "px") {
    return unit === "rem" ? viewEnv.getMouseGlobalPositionRem()
      : viewEnv.getMouseGlobalPositionPx();
  },
  graphicsQuality: {
    isLow: () => viewEnv.getGraphicsQuality() === 1,
    isHigh: () => viewEnv.getGraphicsQuality() === 0,
    get: () => viewEnv.getGraphicsQuality(),
  },
  events: {
    onResize: handler => {
      engine.on("clientResized", handler);
      return () => engine.off("clientResized", handler);
    },
  }
};

export const view = {
  getSize(unit = "px") {
    return unit === "rem" ? viewEnv.getViewSizeRem() : viewEnv.getViewSizePx();
  },
  pxToRem: px => viewEnv.pxToRem(px),
  remToPx: rem => viewEnv.remToPx(rem),
  getGlobalPosition(unit = "rem") {
    const p = viewEnv.getViewGlobalPositionRem();
    return unit === "rem" ? p : { x: viewEnv.remToPx(p.x), y: viewEnv.remToPx(p.y) };
  },
  setInputPaddingsRem(all) {
    viewEnv.setHitAreaPaddingsRem(all, all, all, all, 15);
  },
  setSidePaddingsRem({ top, right, bottom, left }) {
    viewEnv.setHitAreaPaddingsRem(top, right, bottom, left, 15);
  },
  freezeTextureBeforeResize() {
    viewEnv.freezeTextureBeforeResize();
  },
  resize(w, h, unit = "px") {
    return unit === "rem" ? viewEnv.resizeViewRem(w, h) : viewEnv.resizeViewPx(w, h);
  },
};
