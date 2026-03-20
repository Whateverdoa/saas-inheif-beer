"use client"

import { useEffect, useLayoutEffect, useRef, useState } from "react"

/** Meer kleine bellen die opwaarts stijgen (CO₂ in het glas). */
const BUBBLE_COUNT = 130
const REPEL_RADIUS = 120
const REPEL_FORCE = 3.5

const BUBBLE_BG =
  "radial-gradient(circle at 35% 30%, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.65) 28%, rgba(255,255,255,0.28) 52%, rgba(255,255,255,0.12) 72%, transparent 100%)"

type BubbleState = {
  size: number
  x: number
  y: number
  baseX: number
  vx: number
  vy: number
  speed: number
  wobbleAmp: number
  wobbleSpeed: number
  wobbleOffset: number
  opacity: number
  age: number
  fadeIn: boolean
}

/** Zwaar naar kleine bellen: ~62% zeer klein, ~22% klein, rest medium/groot. */
function rollSize(): number {
  const r = Math.random()
  if (r < 0.62) return Math.random() * 3.6 + 2
  if (r < 0.84) return Math.random() * 4 + 4.5
  if (r < 0.94) return Math.random() * 7 + 8.5
  return Math.random() * 8 + 16
}

function resetState(s: BubbleState, w: number, h: number, init: boolean): void {
  s.size = rollSize()
  s.x = Math.random() * w * 0.8 + w * 0.1
  s.y = init ? Math.random() * h : h + 20
  s.baseX = s.x
  s.vx = 0
  s.vy = 0
  let speed =
    (0.35 + Math.random() * 0.85) * (1 - Math.min(s.size, 36) / 42 + 0.42)
  if (s.size < 5) speed *= 1.18
  if (s.size < 3) speed *= 1.08
  s.speed = speed
  let wobbleAmp = Math.random() * 18 + 4
  if (s.size < 5) wobbleAmp *= 0.55
  if (s.size < 3) wobbleAmp *= 0.75
  s.wobbleAmp = wobbleAmp
  s.wobbleSpeed = Math.random() * 0.022 + 0.006
  s.wobbleOffset = Math.random() * Math.PI * 2
  s.opacity = 0.5 + Math.random() * 0.5
  s.age = init ? Math.random() * 1000 : 0
  s.fadeIn = !init
}

function applyBubbleEl(el: HTMLDivElement, s: BubbleState, initialOpacity: boolean): void {
  el.style.width = `${s.size}px`
  el.style.height = `${s.size}px`
  if (s.size < 6) {
    el.style.border = "0.5px solid rgba(255,255,255,0.4)"
    el.style.boxShadow = "none"
  } else {
    el.style.border = "1px solid rgba(255,255,255,0.6)"
    el.style.boxShadow =
      "inset 0 -1px 3px rgba(255,255,255,0.15), 0 0 4px rgba(255,255,255,0.2)"
  }
  el.style.opacity = initialOpacity ? String(s.opacity) : "0"
}

function tickBubble(
  s: BubbleState,
  el: HTMLDivElement,
  w: number,
  h: number,
  mouseX: number,
  mouseY: number,
  speedMul: number,
): void {
  s.age += 1
  if (s.fadeIn && s.age < 30) {
    el.style.opacity = String((s.age / 30) * s.opacity)
  } else if (s.fadeIn && s.age === 30) {
    el.style.opacity = String(s.opacity)
    s.fadeIn = false
  }

  s.y -= s.speed * speedMul
  const wobble = Math.sin(s.age * s.wobbleSpeed + s.wobbleOffset) * s.wobbleAmp
  const targetX = s.baseX + wobble
  const dx = s.x - mouseX
  const dy = s.y - mouseY
  const dist = Math.sqrt(dx * dx + dy * dy)
  if (dist < REPEL_RADIUS && dist > 0) {
    const f = (1 - dist / REPEL_RADIUS) * REPEL_FORCE
    s.vx += (dx / dist) * f
    s.vy += (dy / dist) * f * 0.5
  }
  s.vx *= 0.92
  s.vy *= 0.92
  s.x += s.vx
  s.y += s.vy
  s.x += (targetX - s.x) * 0.02

  if (s.y < 100) {
    el.style.opacity = String(Math.max(0, (s.y / 100) * s.opacity))
  }

  if (s.y < -30) {
    resetState(s, w, h, false)
    applyBubbleEl(el, s, false)
    el.style.transform = `translate(${s.x}px, ${s.y}px)`
    return
  }

  el.style.transform = `translate(${s.x}px, ${s.y}px)`
}

/**
 * Rising beer-glass bubbles (BrewTag HTML reference). Pointer-events none;
 * respects `prefers-reduced-motion`.
 */
export function BeerBubbles() {
  const [active, setActive] = useState(false)
  const speedMulRef = useRef(1)
  const bubblesRef = useRef<(HTMLDivElement | null)[]>([])
  const statesRef = useRef<BubbleState[]>([])

  useEffect(() => {
    const id = requestAnimationFrame(() => {
      const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches
      /** Bij “minder beweging” toch bellen tonen, maar langzamer (anders: geen bellen). */
      speedMulRef.current = reduce ? 0.22 : 1
      setActive(true)
    })
    return () => cancelAnimationFrame(id)
  }, [])

  useLayoutEffect(() => {
    if (!active) return

    const mouse = { x: -9999, y: -9999 }
    const onMove = (e: MouseEvent) => {
      mouse.x = e.clientX
      mouse.y = e.clientY
    }
    const onLeave = () => {
      mouse.x = -9999
      mouse.y = -9999
    }
    const onTouch = (e: TouchEvent) => {
      const t = e.touches[0]
      if (t) {
        mouse.x = t.clientX
        mouse.y = t.clientY
      }
    }

    document.addEventListener("mousemove", onMove)
    document.addEventListener("mouseleave", onLeave)
    document.addEventListener("touchmove", onTouch, { passive: true })
    document.addEventListener("touchend", onLeave)

    const w = () => window.innerWidth
    const h = () => window.innerHeight

    const states: BubbleState[] = []
    for (let i = 0; i < BUBBLE_COUNT; i += 1) {
      const s: BubbleState = {
        size: 0,
        x: 0,
        y: 0,
        baseX: 0,
        vx: 0,
        vy: 0,
        speed: 0,
        wobbleAmp: 0,
        wobbleSpeed: 0,
        wobbleOffset: 0,
        opacity: 1,
        age: 0,
        fadeIn: false,
      }
      resetState(s, w(), h(), true)
      states.push(s)
    }
    statesRef.current = states

    for (let i = 0; i < BUBBLE_COUNT; i += 1) {
      const el = bubblesRef.current[i]
      const s = states[i]
      if (el && s) {
        applyBubbleEl(el, s, true)
        el.style.transform = `translate(${s.x}px, ${s.y}px)`
      }
    }

    let id = 0
    const loop = () => {
      const ww = w()
      const hh = h()
      for (let i = 0; i < BUBBLE_COUNT; i += 1) {
        const el = bubblesRef.current[i]
        const s = statesRef.current[i]
        if (el && s) tickBubble(s, el, ww, hh, mouse.x, mouse.y, speedMulRef.current)
      }
      id = requestAnimationFrame(loop)
    }
    id = requestAnimationFrame(loop)

    return () => {
      cancelAnimationFrame(id)
      document.removeEventListener("mousemove", onMove)
      document.removeEventListener("mouseleave", onLeave)
      document.removeEventListener("touchmove", onTouch)
      document.removeEventListener("touchend", onLeave)
    }
  }, [active])

  if (!active) return null

  return (
    <div
      aria-hidden
      className="pointer-events-none fixed inset-0 z-[1] overflow-hidden"
    >
      {Array.from({ length: BUBBLE_COUNT }, (_, i) => (
        <div
          key={i}
          ref={(el) => {
            bubblesRef.current[i] = el
          }}
          className="pointer-events-none absolute left-0 top-0 rounded-full will-change-transform"
          style={{
            background: BUBBLE_BG,
            borderRadius: "50%",
          }}
        />
      ))}
    </div>
  )
}
