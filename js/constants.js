export const SYMBOL_PATHS = {
  knit: new Path2D(
    "M 0 0.5 L 0.4 0.5 C 0.7 0.5 0.7 0.2 0.5 0.2 C 0.3 0.2 0.3 0.5 0.6 0.5 L 1 0.5"
  ),
  purl: new Path2D(
    "M 1 0.5 L 0.6 0.5 C 0.3 0.5 0.3 0.8 0.5 0.8 C 0.7 0.8 0.7 0.5 0.4 0.5 L 0 0.5"
  ),
  slip: new Path2D("M 0 0.5 L 1 0.5"),
  tuck: new Path2D(
    "M 0 0.5 L 0.2 0.5 C 0.3 0.5 0.35 0.5 0.4 0.45 C 0.45 0.4 0.4 0.2 0.5 0.2 C 0.6 0.2 0.55 0.4 0.6 0.45 C 0.65 0.5 0.7 0.5 0.8 0.5 L 1 0.5"
  ),
};

export const SYMBOL_BITS = {
  knit: false,
  purl: false,
  slip: true,
  tuck: true,
};

export const DEFAULT_SYMBOLS = ["knit", "purl", "slip", "tuck"];
