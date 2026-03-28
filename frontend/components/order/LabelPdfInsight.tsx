"use client"

import type { ReactNode } from "react"

import type { PDFValidationResult } from "@/lib/api/beer"
import type { OrderMessages } from "@/lib/i18n/types"

type InsightCopy = Pick<
  OrderMessages,
  | "insightTitle"
  | "insightLoading"
  | "insightFailed"
  | "insightPages"
  | "insightFileSize"
  | "insightTrimMm"
  | "insightMediaMm"
  | "insightBleedMm"
  | "insightColor"
  | "insightMetaTitle"
  | "insightSuggestedShape"
  | "insightMatch"
  | "insightMatchDistance"
  | "insightMatchNone"
  | "insightErrors"
  | "insightWarnings"
  | "insightAutoFillHint"
>

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B"
  const k = 1024
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${Math.round((bytes / k ** i) * 100) / 100} ${["B", "KB", "MB", "GB"][i]}`
}

function Row({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-baseline gap-0.5 sm:gap-3 text-sm border-b border-[#4a2800]/8 py-2 last:border-0">
      <span className="text-[#6b3e06] font-medium shrink-0 sm:w-[11rem]">{label}</span>
      <span className="text-[#4a2800] break-words">{children}</span>
    </div>
  )
}

export function LabelPdfInsight({
  t,
  loading,
  errorMessage,
  result,
  shapeLabel,
}: {
  t: InsightCopy
  loading: boolean
  errorMessage: string | null
  result: PDFValidationResult | null
  shapeLabel: string | null
}) {
  if (!loading && !errorMessage && !result) {
    return null
  }

  const panelCls =
    "rounded-2xl border border-[#4a2800]/12 bg-[#fffef5]/40 p-4 mb-8 text-left"

  if (loading) {
    return (
      <div className={panelCls} aria-live="polite">
        <h3 className="font-brew-heading font-bold text-[#4a2800] text-sm mb-1">{t.insightTitle}</h3>
        <p className="text-sm text-[#6b3e06]">{t.insightLoading}</p>
      </div>
    )
  }

  if (errorMessage) {
    return (
      <div className={panelCls} role="alert">
        <h3 className="font-brew-heading font-bold text-[#4a2800] text-sm mb-1">{t.insightTitle}</h3>
        <p className="text-sm text-red-800">{t.insightFailed}: {errorMessage}</p>
      </div>
    )
  }

  if (!result) return null

  const bleed = result.bleed_insets_mm
  const bleedStr =
    bleed &&
    `L ${bleed.left} · R ${bleed.right} · B ${bleed.bottom} · T ${bleed.top} mm`

  const metaBits = [
    result.metadata?.title,
    result.metadata?.author,
    result.metadata?.subject,
  ].filter((x) => typeof x === "string" && String(x).trim().length > 0) as string[]

  return (
    <div className={panelCls}>
      <h3 className="font-brew-heading font-bold text-[#4a2800] text-sm mb-2">{t.insightTitle}</h3>
      <p className="text-xs text-[#6b3e06] mb-3">{t.insightAutoFillHint}</p>
      <div className="divide-y divide-[#4a2800]/6">
        <Row label={t.insightPages}>{result.page_count}</Row>
        <Row label={t.insightFileSize}>{formatBytes(result.file_size)}</Row>
        <Row label={t.insightTrimMm}>
          {result.dimensions_display ??
            (result.trim_width_mm != null && result.trim_height_mm != null
              ? `${result.trim_width_mm} × ${result.trim_height_mm} mm`
              : "—")}
        </Row>
        <Row label={t.insightMediaMm}>
          {result.media_width_mm != null && result.media_height_mm != null
            ? `${result.media_width_mm} × ${result.media_height_mm} mm`
            : "—"}
        </Row>
        <Row label={t.insightBleedMm}>{bleedStr ?? "—"}</Row>
        <Row label={t.insightColor}>
          {result.color_space ?? "—"}
          {result.is_cmyk ? " · CMYK" : ""}
        </Row>
        <Row label={t.insightSuggestedShape}>{shapeLabel ?? result.suggested_shape ?? "—"}</Row>
        <Row label={t.insightMatch}>
          {result.matched_standard_label_name ? (
            <>
              {result.matched_standard_label_name}
              {result.match_distance_mm != null ? (
                <span className="text-[#6b3e06] text-xs ml-1">
                  ({t.insightMatchDistance.replace("{n}", String(result.match_distance_mm))})
                </span>
              ) : null}
            </>
          ) : (
            t.insightMatchNone
          )}
        </Row>
        {metaBits.length > 0 ? (
          <Row label={t.insightMetaTitle}>{metaBits.join(" · ")}</Row>
        ) : null}
      </div>
      {result.errors.length > 0 ? (
        <div className="mt-3 rounded-xl bg-red-900/10 border border-red-900/20 px-3 py-2">
          <p className="text-xs font-bold text-red-900 mb-1">{t.insightErrors}</p>
          <ul className="text-xs text-red-900 list-disc pl-4 space-y-0.5">
            {result.errors.map((e) => (
              <li key={e}>{e}</li>
            ))}
          </ul>
        </div>
      ) : null}
      {result.warnings.length > 0 ? (
        <div className="mt-3 rounded-xl bg-amber-900/10 border border-amber-900/20 px-3 py-2">
          <p className="text-xs font-bold text-amber-900 mb-1">{t.insightWarnings}</p>
          <ul className="text-xs text-amber-950 list-disc pl-4 space-y-0.5">
            {result.warnings.map((w) => (
              <li key={w}>{w}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  )
}
