"use client"

import {
  ORDER_QUANTITY_INPUT_MAX,
  ORDER_QUANTITY_MIN,
  ORDER_QUANTITY_PRESETS,
  ORDER_QUANTITY_SLIDER_MAX,
} from "@/components/order/order-quantity-config"
import type { Locale } from "@/lib/i18n/config"
import type { OrderMessages } from "@/lib/i18n/types"

type QtyCopy = Pick<
  OrderMessages,
  | "quantity"
  | "quantityUnit"
  | "quantityQuickPick"
  | "quantityInputLabel"
  | "quantityBeyondSlider"
>

const h2 = "font-brew-heading font-bold text-xl border-b border-[#4a2800]/10 pb-3 mb-4 mt-8"
const labelCls = "block text-[0.8rem] font-semibold text-[#6b3e06] mb-1 tracking-wide"
const inputCls =
  "w-full px-4 py-3 rounded-xl border-[1.5px] border-[#4a2800]/10 bg-white/45 focus:border-[#b8860b] focus:bg-white/65 outline-none text-[#4a2800]"
const chip =
  "rounded-xl border-2 px-3 py-2 text-sm font-semibold transition border-[#4a2800]/8 bg-white/25 text-[#4a2800] hover:border-[#4a2800]/25"
const chipOn = "border-[#b8860b] bg-[#b8860b]/15"

function numberTag(locale: Locale): string {
  const map: Record<Locale, string> = {
    nl: "nl-NL",
    de: "de-DE",
    fr: "fr-FR",
    en: "en-GB",
  }
  return map[locale]
}

function clampQuantity(raw: number): number {
  if (!Number.isFinite(raw)) return ORDER_QUANTITY_MIN
  return Math.min(ORDER_QUANTITY_INPUT_MAX, Math.max(ORDER_QUANTITY_MIN, Math.round(raw)))
}

export function OrderQuantitySection({
  t,
  locale,
  quantity,
  onQuantityChange,
}: {
  t: QtyCopy
  locale: Locale
  quantity: number
  onQuantityChange: (n: number) => void
}) {
  const nf = numberTag(locale)
  const sliderValue = Math.min(quantity, ORDER_QUANTITY_SLIDER_MAX)

  return (
    <section aria-labelledby="order-qty-heading">
      <h2 id="order-qty-heading" className={h2}>
        {t.quantity}
      </h2>
      <p className="text-xs font-semibold uppercase tracking-wide text-[#6b3e06] mb-2">
        {t.quantityQuickPick}
      </p>
      <div className="flex flex-wrap gap-2 mb-5">
        {ORDER_QUANTITY_PRESETS.map((n) => (
          <button
            key={n}
            type="button"
            onClick={() => onQuantityChange(n)}
            className={`${chip} ${quantity === n ? chipOn : ""}`}
          >
            {n.toLocaleString(nf)}
          </button>
        ))}
      </div>
      <div className="mb-5">
        <label className={labelCls} htmlFor="order-quantity-input">
          {t.quantityInputLabel}
        </label>
        <div className="flex flex-col sm:flex-row sm:items-center gap-3">
          <input
            id="order-quantity-input"
            type="number"
            inputMode="numeric"
            min={ORDER_QUANTITY_MIN}
            max={ORDER_QUANTITY_INPUT_MAX}
            step={1}
            className={`${inputCls} sm:max-w-[220px]`}
            value={quantity}
            onChange={(e) => {
              const v = e.target.value
              if (v === "") return
              const parsed = Number.parseInt(v, 10)
              if (Number.isNaN(parsed)) return
              onQuantityChange(clampQuantity(parsed))
            }}
          />
          <span className="text-sm text-[#6b3e06]">{t.quantityUnit}</span>
        </div>
      </div>
      <input
        type="range"
        min={ORDER_QUANTITY_MIN}
        max={ORDER_QUANTITY_SLIDER_MAX}
        step={50}
        value={sliderValue}
        onChange={(e) => onQuantityChange(clampQuantity(Number(e.target.value)))}
        className="w-full h-2 rounded-full accent-[#b8860b]"
        aria-label={t.quantity}
      />
      {quantity > ORDER_QUANTITY_SLIDER_MAX ? (
        <p className="text-xs text-[#6b3e06] mt-2">
          {quantity.toLocaleString(nf)} {t.quantityUnit} — {t.quantityBeyondSlider}
        </p>
      ) : null}
    </section>
  )
}
