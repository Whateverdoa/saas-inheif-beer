"use client"

import { useEffect, useLayoutEffect, useRef, useState } from "react"

import {
  BEER_FOAM_COLLAR_HEIGHT_PX,
  initFoam,
  paintFoamFrame,
  paintFoamStatic,
  type FoamCell,
  type FoamDrip,
} from "@/components/brew/beer-foam-engine"

export { BEER_FOAM_COLLAR_HEIGHT_PX }

/**
 * Schuimkraag: interactief canvas-schuim bovenaan, loopt over in het “bier”.
 * `prefers-reduced-motion`: één stilstaand frame.
 */
export function BeerFoamCollar() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const cellsRef = useRef<FoamCell[]>([])
  const dripsRef = useRef<FoamDrip[]>([])
  const mouseRef = useRef({ x: -99999, y: -99999 })
  const [show, setShow] = useState(false)
  const reducedRef = useRef(false)

  useEffect(() => {
    reducedRef.current = window.matchMedia("(prefers-reduced-motion: reduce)").matches
    const id = requestAnimationFrame(() => setShow(true))
    return () => cancelAnimationFrame(id)
  }, [])

  useLayoutEffect(() => {
    if (!show) return
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const reduced = reducedRef.current
    let raf = 0
    const dpr = Math.min(window.devicePixelRatio || 1, 2)
    const h = BEER_FOAM_COLLAR_HEIGHT_PX

    const resize = () => {
      const w = window.innerWidth
      canvas.width = w * dpr
      canvas.height = h * dpr
      canvas.style.width = `${w}px`
      canvas.style.height = `${h}px`
      if (reduced) {
        paintFoamStatic(ctx, w, dpr, h)
        return
      }
      const { cells, drips } = initFoam(w)
      cellsRef.current = cells
      dripsRef.current = drips
    }

    const onMove = (e: MouseEvent) => {
      mouseRef.current = { x: e.clientX, y: e.clientY }
    }
    const off = () => {
      mouseRef.current = { x: -99999, y: -99999 }
    }
    const onTouch = (e: TouchEvent) => {
      const t = e.touches[0]
      if (t) mouseRef.current = { x: t.clientX, y: t.clientY }
    }

    resize()
    window.addEventListener("resize", resize)
    document.addEventListener("mousemove", onMove)
    document.addEventListener("mouseleave", off)
    document.addEventListener("touchmove", onTouch, { passive: true })
    document.addEventListener("touchend", off)

    const loop = () => {
      if (!reduced) {
        const w = window.innerWidth
        paintFoamFrame(
          ctx,
          w,
          dpr,
          h,
          cellsRef.current,
          dripsRef.current,
          mouseRef.current.x,
          mouseRef.current.y,
        )
      }
      raf = requestAnimationFrame(loop)
    }
    if (!reduced) raf = requestAnimationFrame(loop)

    return () => {
      cancelAnimationFrame(raf)
      window.removeEventListener("resize", resize)
      document.removeEventListener("mousemove", onMove)
      document.removeEventListener("mouseleave", off)
      document.removeEventListener("touchmove", onTouch)
      document.removeEventListener("touchend", off)
    }
  }, [show])

  if (!show) return null

  /** Alleen onderzijde verzachten — onderste schuim/bellen smelten in de shell-gradient. */
  const mask = "linear-gradient(to bottom, #000 0%, #000 78%, rgba(0,0,0,0.5) 90%, transparent 100%)"

  return (
    <div
      aria-hidden
      className="pointer-events-none fixed top-0 left-0 right-0 z-[5]"
      style={{
        height: BEER_FOAM_COLLAR_HEIGHT_PX,
        WebkitMaskImage: mask,
        maskImage: mask,
      }}
    >
      <canvas ref={canvasRef} className="block h-full w-full" />
    </div>
  )
}
