import React, {createContext, useCallback, useEffect, useMemo, useState} from "react";
import { client, view } from "./host";
import { BREAKPOINTS, computeMediaFlags } from "./breakpoints";

const initial = (() => {
  const { width, height } = client.getSize("rem");
  return { width, height, ...computeMediaFlags(width, height, BREAKPOINTS) };
})();

export const MediaContext = createContext(initial);

/** Updates media flags on engine "clientResized" (px), converts to rem */
export function MediaProvider({ children }) {
  const [state, setState] = useState(initial);

  const onResize = useCallback((pxW, pxH) => {
    const w = view.pxToRem(pxW);
    const h = view.pxToRem(pxH);
    setState({ width: w, height: h, ...computeMediaFlags(w, h, BREAKPOINTS) });
  }, []);

  useEffect(() => client.events.onResize(onResize), [onResize]);

  // freeze object identity for context consumers
  const value = useMemo(() => ({ ...state }), [state]);

  return <MediaContext.Provider value={value}>{children}</MediaContext.Provider>;
}

/** Conditional renderer like <Media large>...</Media> or width/height gates */
export function Media(props) {
  const { children, ...conds } = props;
  const ctx = React.useContext(MediaContext);

  const match = () => {
    // width-independent size buckets
    if (conds.extraLarge || conds.large || conds.medium || conds.small || conds.extraSmall) {
      if (conds.extraLarge && ctx.extraLarge) return true;
      if (conds.large && ctx.large)           return true;
      if (conds.medium && ctx.medium)         return true;
      if (conds.small && ctx.small)           return true;
      if (conds.extraSmall && ctx.extraSmall) return true;
      return false;
    }

    // width buckets
    if (conds.extraLargeWidth && ctx.extraLargeWidth) return true;
    if (conds.largeWidth      && ctx.largeWidth)      return true;
    if (conds.mediumWidth     && ctx.mediumWidth)     return true;
    if (conds.smallWidth      && ctx.smallWidth)      return true;
    if (conds.extraSmallWidth && ctx.extraSmallWidth) return true;

    // height buckets (only if no width buckets specified)
    if (!(conds.extraLargeWidth || conds.largeWidth || conds.mediumWidth || conds.smallWidth || conds.extraSmallWidth)) {
      if (conds.extraLargeHeight && ctx.extraLargeHeight) return true;
      if (conds.largeHeight      && ctx.largeHeight)      return true;
      if (conds.mediumHeight     && ctx.mediumHeight)     return true;
      if (conds.smallHeight      && ctx.smallHeight)      return true;
      if (conds.extraSmallHeight && ctx.extraSmallHeight) return true;
    }

    return false;
  };

  return match() ? children : null;
}

Media.defaultProps = {
  extraLarge:false, large:false, medium:false, small:false, extraSmall:false,
  extraLargeWidth:false, largeWidth:false, mediumWidth:false, smallWidth:false, extraSmallWidth:false,
  extraLargeHeight:false, largeHeight:false, mediumHeight:false, smallHeight:false, extraSmallHeight:false,
};
