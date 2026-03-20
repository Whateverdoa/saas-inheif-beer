"use client"

import { usePathname, useRouter } from "next/navigation"
import { useCallback } from "react"

import {
  LOCALE_LABELS,
  LOCALES,
  type Locale,
  withLocale,
} from "@/lib/i18n/config"

const COOKIE = "NEXT_LOCALE"
const MAX_AGE = 60 * 60 * 24 * 365

export function LocaleSwitcher({
  current,
  navLabel,
}: {
  current: Locale
  navLabel: string
}) {
  const pathname = usePathname()
  const router = useRouter()

  const switchTo = useCallback(
    (next: Locale) => {
      document.cookie = `${COOKIE}=${next}; path=/; max-age=${MAX_AGE}; SameSite=Lax`
      const segs = pathname.split("/").filter(Boolean)
      if (segs.length && LOCALES.includes(segs[0] as Locale)) {
        segs[0] = next
        router.push("/" + segs.join("/"))
      } else {
        router.push(withLocale(next, pathname || "/"))
      }
    },
    [pathname, router],
  )

  return (
    <div className="flex flex-wrap items-center gap-1.5 text-[0.75rem] font-semibold text-[#4a2800]/90">
      <span className="sr-only">{navLabel}</span>
      {LOCALES.map((loc) => (
        <button
          key={loc}
          type="button"
          onClick={() => switchTo(loc)}
          className={
            loc === current
              ? "min-w-[2.25rem] rounded-full bg-[#4a2800] px-2 py-1 text-[#f0c632]"
              : "min-w-[2.25rem] rounded-full px-2 py-1 hover:bg-white/30"
          }
          aria-current={loc === current ? "true" : undefined}
          aria-label={`${navLabel}: ${loc.toUpperCase()}`}
        >
          {LOCALE_LABELS[loc]}
        </button>
      ))}
    </div>
  )
}
