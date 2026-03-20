"use client"

import { useEffect, useState } from "react"

import type { BeerLabelType } from "@/lib/api/beer"
import { beerApi } from "@/lib/api/beer"

/** Loads `/beer/label-types` once for order/configurator flows. */
export function useBeerLabelTypes(): {
  formats: BeerLabelType[]
  loading: boolean
  error: string | null
} {
  const [formats, setFormats] = useState<BeerLabelType[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    beerApi
      .getLabelTypes()
      .then((data) => {
        if (!cancelled) {
          setFormats(data)
          setError(null)
        }
      })
      .catch(() => {
        if (!cancelled) setError("fetch")
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  return { formats, loading, error }
}
