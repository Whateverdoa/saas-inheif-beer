import type { Metadata } from "next"
import { DM_Sans, Geist, Geist_Mono, Playfair_Display } from "next/font/google"
import { headers } from "next/headers"

import { DEFAULT_LOCALE, isLocale } from "@/lib/i18n/config"
import "./globals.css"

const LOCALE_HEADER = "x-next-locale"

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
})

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
})

const playfair = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["latin"],
  weight: ["700", "900"],
})

const dmSans = DM_Sans({
  variable: "--font-dm-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
})

export const metadata: Metadata = {
  title: "VILA-BIER VRIJMIBO · Vila-etiketten",
  description: "Bieretiketten in één keer — standaard formaten, introductie 5 ct per etiket.",
}

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  const h = await headers()
  const raw = h.get(LOCALE_HEADER)
  const lang = raw && isLocale(raw) ? raw : DEFAULT_LOCALE

  return (
    <html lang={lang} suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} ${playfair.variable} ${dmSans.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  )
}
