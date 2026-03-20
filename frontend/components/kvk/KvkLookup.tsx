"use client"

import { useCallback, useState } from "react"
import { lookupKvk, type KvkCompany } from "@/lib/api/kvk"

type Status = "idle" | "searching" | "found" | "error"

export interface KvkLookupProps {
  onFound: (c: KvkCompany) => void
  onClear: () => void
}

export function KvkLookup({ onFound, onClear }: KvkLookupProps) {
  const [input, setInput] = useState("")
  const [status, setStatus] = useState<Status>("idle")
  const [message, setMessage] = useState("Voer een KVK-nummer in")
  const [result, setResult] = useState<KvkCompany | null>(null)

  const runLookup = useCallback(async () => {
    const raw = input.replace(/\s+/g, "")
    if (!/^\d{8}$/.test(raw)) {
      setStatus("error")
      setMessage("KVK nummer moet exact 8 cijfers zijn")
      setResult(null)
      onClear()
      return
    }
    setStatus("searching")
    setMessage("Zoeken…")
    try {
      const data = await lookupKvk(raw)
      setResult(data)
      setStatus("found")
      setMessage(
        data.source === "mock" ? "Testgegevens geladen (geen API-key)" : "Bedrijf gevonden",
      )
      onFound(data)
    } catch (e) {
      setResult(null)
      setStatus("error")
      setMessage(e instanceof Error ? e.message : "Opzoeken mislukt")
      onClear()
    }
  }, [input, onFound, onClear])

  const clear = () => {
    setResult(null)
    setStatus("idle")
    setMessage("Voer een KVK-nummer in")
    onClear()
  }

  const dotClass =
    status === "searching"
      ? "bg-blue-500 animate-pulse"
      : status === "found"
        ? "bg-emerald-500"
        : status === "error"
          ? "bg-red-500"
          : "bg-[#4a2800]/20"

  return (
    <div className="mb-6 space-y-3">
      <div>
        <label className="block text-[0.8rem] font-semibold text-[#6b3e06] mb-1 tracking-wide">
          KVK-nummer
        </label>
        <div className="flex gap-2 flex-wrap">
          <input
            type="text"
            inputMode="numeric"
            maxLength={10}
            value={input}
            onChange={(e) => setInput(e.target.value.replace(/[^\d\s]/g, ""))}
            placeholder="8-cijferig KVK-nummer"
            className="flex-1 min-w-[10rem] px-4 py-3 rounded-xl border-[1.5px] border-[#4a2800]/10 bg-white/50 focus:border-[#b8860b] focus:bg-white/70 outline-none transition"
          />
          <button
            type="button"
            onClick={() => void runLookup()}
            disabled={status === "searching"}
            className="px-5 py-3 rounded-xl bg-[#4a2800] text-[#fffef5] font-semibold text-sm hover:opacity-95 disabled:opacity-60 shrink-0"
          >
            Opzoeken
          </button>
        </div>
        <p className="text-xs text-[#6b3e06]/80 mt-2">
          Test:{" "}
          <button
            type="button"
            className="underline"
            onClick={() => setInput("12345678")}
          >
            12345678
          </button>
          {" · "}
          <button
            type="button"
            className="underline"
            onClick={() => setInput("69599084")}
          >
            69599084
          </button>
          {" · "}
          Met{" "}
          <code className="text-[0.65rem] bg-white/30 px-1 rounded">KVK_API_KEY</code> live
          van KVK
        </p>
      </div>

      <div className="flex items-center gap-2 text-sm">
        <span className={`w-2 h-2 rounded-full shrink-0 ${dotClass}`} />
        <span className="text-[#6b3e06]">{message}</span>
      </div>

      {result && (
        <div className="rounded-xl border-[1.5px] border-emerald-500/25 bg-emerald-500/10 p-4">
          <div className="flex justify-between items-start gap-2 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wide text-emerald-800">
              KVK {result.kvk_number}
            </span>
            <button
              type="button"
              onClick={clear}
              className="text-xs text-[#6b3e06] hover:text-[#4a2800]"
            >
              Wissen
            </button>
          </div>
          <p className="font-brew-heading font-bold text-lg text-[#4a2800]">{result.name}</p>
          {result.rechtsvorm && (
            <p className="text-sm text-[#6b3e06] mt-1">{result.rechtsvorm}</p>
          )}
          <p className="text-sm mt-2 text-[#4a2800]/90">{result.full_address}</p>
        </div>
      )}
    </div>
  )
}
