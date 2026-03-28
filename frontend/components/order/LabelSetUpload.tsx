"use client"

import { useCallback } from "react"
import { useDropzone } from "react-dropzone"

import { PdfFirstPageThumbnail } from "@/components/order/PdfFirstPageThumbnail"
import type { OrderMessages } from "@/lib/i18n/types"

/** Roles kept for payloads / future multi-face extraction from one PDF. */
export type LabelRole = "front" | "back" | "neck" | "other"

export type LabelFileMap = Partial<Record<LabelRole, File>>

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B"
  const k = 1024
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${Math.round((bytes / k ** i) * 100) / 100} ${["B", "KB", "MB", "GB"][i]}`
}

export function LabelSetUpload({
  t,
  files,
  onChange,
}: {
  t: OrderMessages
  files: LabelFileMap
  onChange: (files: LabelFileMap) => void
}) {
  const file = files.front

  const onDrop = useCallback(
    (accepted: File[]) => {
      const f = accepted[0]
      if (f) onChange({ front: f })
    },
    [onChange]
  )

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxSize: 50 * 1024 * 1024,
    maxFiles: 1,
    multiple: false,
    noClick: !!file,
    noKeyboard: !!file,
  })

  const clear = useCallback(() => onChange({}), [onChange])

  return (
    <div className="mb-10">
      <h2 className="font-brew-heading font-bold text-xl border-b border-[#4a2800]/10 pb-3 mb-2">
        {t.uploadSectionTitle}
      </h2>
      <p className="text-sm text-[#6b3e06] mb-5 leading-relaxed">{t.uploadIntro}</p>

      <div className="rounded-2xl border border-[#4a2800]/12 bg-white/30 overflow-hidden">
        {!file ? (
          <div
            {...getRootProps()}
            className={`cursor-pointer px-4 py-10 text-center transition border-2 border-dashed rounded-2xl border-[#4a2800]/20 m-3 ${
              isDragActive ? "border-[#b8860b] bg-[#b8860b]/10" : "hover:border-[#4a2800]/35"
            }`}
          >
            <input {...getInputProps({ className: "hidden" })} />
            <p className="text-sm font-medium text-[#4a2800]">{t.uploadDrop}</p>
            <p className="text-xs text-[#6b3e06] mt-1">{t.uploadPdfOnly}</p>
          </div>
        ) : (
          <div className="p-4 space-y-3">
            <div
              {...getRootProps({
                className: `rounded-xl overflow-hidden border-2 transition ${
                  isDragActive
                    ? "border-[#b8860b] bg-[#b8860b]/10"
                    : "border-[#4a2800]/10 bg-white/40"
                }`,
              })}
            >
              <input {...getInputProps({ className: "hidden" })} />
              <PdfFirstPageThumbnail
                file={file}
                loadingLabel={t.uploadPreviewLoading}
                failedLabel={t.uploadPreviewFailed}
              />
            </div>
            <div className="flex flex-wrap items-center gap-2 justify-between gap-y-2">
              <div className="min-w-0">
                <p className="text-sm font-medium text-[#4a2800] truncate">{file.name}</p>
                <p className="text-xs text-[#6b3e06]">{formatBytes(file.size)}</p>
              </div>
              <div className="flex flex-wrap gap-2 shrink-0">
                <button
                  type="button"
                  onClick={() => open()}
                  className="text-xs font-semibold text-[#4a2800] px-3 py-1.5 rounded-lg border border-[#4a2800]/20 bg-white/50 hover:bg-white/80"
                >
                  {t.uploadReplace}
                </button>
                <button
                  type="button"
                  onClick={clear}
                  className="text-xs font-semibold text-[#6b3e06] hover:text-[#4a2800] underline"
                >
                  {t.uploadRemove}
                </button>
              </div>
            </div>
            <p className="text-xs text-[#6b3e06]/80">{t.uploadDragReplaceHint}</p>
          </div>
        )}
      </div>

      {!file && (
        <p className="mt-3 text-xs text-amber-900/90 font-medium">{t.uploadFrontRequired}</p>
      )}
    </div>
  )
}
