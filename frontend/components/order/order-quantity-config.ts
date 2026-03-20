/** Shared bounds for beer label order quantity UI. */

export const ORDER_QUANTITY_MIN = 100
/** Slider and quick-pick upper bound (aligned with common runs). */
export const ORDER_QUANTITY_SLIDER_MAX = 25000
/** Hard cap for typed quantities (custom / grote oplage). */
export const ORDER_QUANTITY_INPUT_MAX = 50000

/** Gangbare oplages — gebruiker kan elk aantal tussen min/max typen. */
export const ORDER_QUANTITY_PRESETS = [
  250, 500, 1000, 2500, 5000, 10000, 25000,
] as const
