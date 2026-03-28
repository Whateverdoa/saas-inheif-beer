"use client"

import { useEffect, useState } from "react"

type Props = {
  file: File | null
  loadingLabel: string
  failedLabel: string
  className?: string
}

/**
 * Renders page 1 of a PDF as a JPEG data-URL (client-side, pdf.js).
 */
export function PdfFirstPageThumbnail({
  file,
  loadingLabel,
  failedLabel,
  className = "",
}: Props) {
  const [dataUrl, setDataUrl] = useState<string | null>(null)
  const [err, setErr] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    if (!file) {
      setDataUrl(null)
      setErr(null)
      return
    }

    const current = file

    async function run() {
      try {
        const pdfjs = await import("pdfjs-dist")
        const v = pdfjs.version
        pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${v}/build/pdf.worker.min.mjs`

        const buf = await current.arrayBuffer()
        const doc = await pdfjs.getDocument({ data: buf }).promise
        const page = await doc.getPage(1)
        const base = page.getViewport({ scale: 1 })
        const maxW = 720
        const maxH = 420
        const scale = Math.min(maxW / base.width, maxH / base.height, 2)
        const viewport = page.getViewport({ scale })

        const canvas = document.createElement("canvas")
        const ctx = canvas.getContext("2d")
        if (!ctx) {
          throw new Error("Canvas unsupported")
        }
        canvas.width = Math.floor(viewport.width)
        canvas.height = Math.floor(viewport.height)

        await page.render({ canvasContext: ctx, viewport }).promise

        if (!cancelled) {
          setDataUrl(canvas.toDataURL("image/jpeg", 0.88))
          setErr(null)
        }
      } catch {
        if (!cancelled) {
          setDataUrl(null)
          setErr(failedLabel)
        }
      }
    }

    void run()
    return () => {
      cancelled = true
    }
  }, [file, failedLabel])

  if (!file) return null
  if (err) {
    return <p className="text-center text-xs text-amber-900/90 px-2">{err}</p>
  }
  if (!dataUrl) {
    return <p className="text-center text-xs text-[#6b3e06] animate-pulse">{loadingLabel}</p>
  }

  return (
    <img
      src={dataUrl}
      alt=""
      className={`max-h-[min(420px,55vh)] w-full object-contain bg-[#2a1810]/5 ${className}`}
    />
  )
}
