// Screen class thresholds in REM (weights are just ranks)
export const BREAKPOINTS = {
  extraLarge: { weight: 4, width: 2560, height: 1440 },
  large:      { weight: 3, width: 1920, height: 1080 },
  medium:     { weight: 2, width: 1600, height: 900  },
  small:      { weight: 1, width: 1366, height: 768  },
  extraSmall: { weight: 0, width: 1024, height: 768  },
};

// Produces flags like {large:true, mediumWidth:false, smallHeight:true, ...}
export function computeMediaFlags(remW, remH, bp = BREAKPOINTS) {
  const rankW = remW >= bp.extraLarge.width ? bp.extraLarge.weight
               : remW >= bp.large.width     ? bp.large.weight
               : remW >= bp.medium.width    ? bp.medium.weight
               : remW >= bp.small.width     ? bp.small.weight
               :                               bp.extraSmall.weight;

  const rankH = remH >= bp.extraLarge.height ? bp.extraLarge.weight
               : remH >= bp.large.height     ? bp.large.weight
               : remH >= bp.medium.height    ? bp.medium.weight
               : remH >= bp.small.height     ? bp.small.weight
               :                                bp.extraSmall.weight;

  const rank = Math.min(rankW, rankH);

  const by = n => n === rank;
  const byW = n => n === rankW;
  const byH = n => n === rankH;

  return {
    extraLarge: by(bp.extraLarge.weight),
    large:      by(bp.large.weight),
    medium:     by(bp.medium.weight),
    small:      by(bp.small.weight),
    extraSmall: by(bp.extraSmall.weight),

    extraLargeWidth: byW(bp.extraLarge.weight),
    largeWidth:      byW(bp.large.weight),
    mediumWidth:     byW(bp.medium.weight),
    smallWidth:      byW(bp.small.weight),
    extraSmallWidth: byW(bp.extraSmall.weight),

    extraLargeHeight: byH(bp.extraLarge.weight),
    largeHeight:      byH(bp.large.weight),
    mediumHeight:     byH(bp.medium.weight),
    smallHeight:      byH(bp.small.weight),
    extraSmallHeight: byH(bp.extraSmall.weight),
  };
}
