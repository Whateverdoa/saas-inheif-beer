import type { NextRequest } from "next/server"
import { NextResponse } from "next/server"

import { isLocale, type Locale } from "@/lib/i18n/config"
import { pickLocaleFromAcceptLanguage } from "@/lib/i18n/pick-locale"

const LOCALE_HEADER = "x-next-locale"

function pathnameStartsWithLocale(pathname: string): Locale | null {
  const seg = pathname.split("/")[1]
  if (seg && isLocale(seg)) return seg
  return null
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  if (
    pathname.startsWith("/_next") ||
    pathname.startsWith("/api") ||
    pathname.includes(".") // favicon, static files
  ) {
    return NextResponse.next()
  }

  const existing = pathnameStartsWithLocale(pathname)
  if (existing) {
    const res = NextResponse.next()
    res.headers.set(LOCALE_HEADER, existing)
    return res
  }

  const cookieLocale = request.cookies.get("NEXT_LOCALE")?.value
  const preferred: Locale =
    cookieLocale && isLocale(cookieLocale)
      ? cookieLocale
      : pickLocaleFromAcceptLanguage(request.headers.get("accept-language"))

  const url = request.nextUrl.clone()
  url.pathname =
    pathname === "/" ? `/${preferred}` : `/${preferred}${pathname}`

  const res = NextResponse.redirect(url)
  return res
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\..*).*)"],
}
