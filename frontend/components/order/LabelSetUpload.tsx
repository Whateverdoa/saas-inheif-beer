"use client"

import { useCallback, useState } from "react"
import { useDropzone } from "react-dropzone"

import type { OrderMessages } from "@/lib/i18n/types"

export type LabelRole = "front" | "back" | "neck" | "other"

export type LabelFileMap = Partial<Record<LabelRole, File>>

const ROLES: LabelRole[] = ["front", "back", "neck", "other"]

function roleLabel(role: LabelRole, t: OrderMessages): string {
  switch (role) {
    case "front":
      return t.roleFront
    case "back":
      return t.roleBack
    case "neck":
      return t.roleNeck
    case "other":
      return t.roleOther
    default:
      return role
  }
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B"
  const k = 1024
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${Math.round((bytes / k ** i) * 100) / 100} ${["B", "KB", "MB", "GB"][i]}`
}

function LabelSlot({
  required,
  label,
  optionalMark,
  drop,
  pdfOnly,
  remove,
  file,
  onFile,
  onClear,
}: {
  required: boolean
  label: string
  optionalMark: string
  drop: string
  pdfOnly: string
  remove: string
  file: File | undefined
  onFile: (f: File) => void
  onClear: () => void
}) {
  const onDrop = useCallback(
    (accepted: File[]) => {
      if (accepted[0]) onFile(accepted[0])
    },
    [onFile]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxSize: 50 * 1024 * 1024,
    maxFiles: 1,
    multiple: false,
  })

  return (
    <div className="rounded-2xl border border-[#4a2800]/12 bg-white/30 p-4">
      <div className="flex items-baseline justify-between gap-2 mb-2">
        <span className="font-brew-heading font-bold text-[#4a2800] text-sm">
          {label}
          {required ? (
            <span className="text-red-700/90 font-sans font-semibold text-xs ml-1">*</span>
          ) : (
            <span className="text-[#6b3e06]/80 font-sans font-normal text-xs ml-1">
              · {optionalMark}
            </span>
          )}
        </span>
      </div>
      {!file ? (
        <div
          {...getRootProps()}
          className={`cursor-pointer rounded-xl border-2 border-dashed border-[#4a2800]/20 px-3 py-6 text-center transition ${
            isDragActive ? "border-[#b8860b] bg-[#b8860b]/10" : "hover:border-[#4a2800]/35"
          }`}
        >
          <input {...getInputProps()} />
          <p className="text-sm font-medium text-[#4a2800]">{drop}</p>
          <p className="text-xs text-[#6b3e06] mt-1">{pdfOnly}</p>
        </div>
      ) : (
        <div className="flex items-center justify-between gap-2 rounded-xl bg-white/50 border border-[#4a2800]/10 px-3 py-2">
          <div className="min-w-0">
            <p className="text-sm font-medium text-[#4a2800] truncate">{file.name}</p>
            <p className="text-xs text-[#6b3e06]">{formatBytes(file.size)}</p>
          </div>
          <button
            type="button"
            onClick={onClear}
            className="shrink-0 text-xs font-semibold text-[#6b3e06] hover:text-[#4a2800] underline"
          >
            {remove}
          </button>
        </div>
      )}
    </div>
  )
}

export function LabelSetUpload({
  t,
  onChange,
}: {
  t: OrderMessages
  onChange?: (files: LabelFileMap) => void
}) {
  const [files, setFiles] = useState<LabelFileMap>({})

  const update = useCallback(
    (next: LabelFileMap) => {
      setFiles(next)
      onChange?.(next)
    },
    [onChange]
  )

  const setRoleFile = useCallback(
    (role: LabelRole, file: File) => {
      update({ ...files, [role]: file })
    },
    [files, update]
  )

  const clearRole = useCallback(
    (role: LabelRole) => {
      const next = { ...files }
      delete next[role]
      update(next)
    },
    [files, update]
  )

  return (
    <div className="mb-10">
      <h2 className="font-brew-heading font-bold text-xl border-b border-[#4a2800]/10 pb-3 mb-2">
        {t.uploadSectionTitle}
      </h2>
      <p className="text-sm text-[#6b3e06] mb-5">{t.uploadIntro}</p>
      <div className="grid sm:grid-cols-2 gap-4">
        {ROLES.map((role) => (
          <LabelSlot
            key={role}
            required={role === "front"}
            optionalMark={t.uploadOptionalShort}
            label={roleLabel(role, t)}
            drop={t.uploadDrop}
            pdfOnly={t.uploadPdfOnly}
            remove={t.uploadRemove}
            file={files[role]}
            onFile={(f) => setRoleFile(role, f)}
            onClear={() => clearRole(role)}
          />
        ))}
      </div>
      {!files.front && (
        <p className="mt-3 text-xs text-amber-900/90 font-medium">{t.uploadFrontRequired}</p>
      )}
    </div>
  )
}
