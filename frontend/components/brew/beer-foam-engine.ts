/** Canvas schuimkraag — fysica + tekenlogica (BrewTag-achtig). */

/** Hoogte van het “echte” schuim (bellen); daarna blend naar vloeistof. */
export const FOAM_H = 290
/** Totaal canvas: dik schuim + zachte overgang naar bierkleur. */
export const BEER_FOAM_COLLAR_HEIGHT_PX = FOAM_H + 102

const REPEL = 168
const REPEL_F = 4.8

export type FoamCell = {
  hx: number
  hy: number
  r: number
  x: number
  y: number
  vx: number
  vy: number
  warmth: number
  brightness: number
  hlChance: number
  hlAlpha: number
}

export type FoamDrip = {
  hx: number
  hy: number
  r: number
  x: number
  y: number
  vx: number
  vy: number
  alpha: number
}

export function initFoam(w: number): { cells: FoamCell[]; drips: FoamDrip[] } {
  const cells: FoamCell[] = []
  const bubbleMultiplier = 0.036

  const addZone = (
    y0: number,
    y1: number,
    minR: number,
    maxR: number,
    density: number,
  ) => {
    const rowStep = 5
    const rows = Math.max(1, Math.floor((y1 - y0) / rowStep))
    for (let i = 0; i < rows; i += 1) {
      const y = y0 + i * rowStep + Math.random() * 2.5
      const count = Math.floor(w * density * bubbleMultiplier)
      for (let j = 0; j < count; j += 1) {
        const hx = Math.random() * w
        const hy = y + (Math.random() - 0.5) * 9
        const r = minR + Math.random() * (maxR - minR)
        cells.push({
          hx,
          hy,
          r,
          x: hx,
          y: hy,
          vx: 0,
          vy: 0,
          warmth: Math.random() * 10,
          brightness: 244 + Math.random() * 11,
          hlChance: Math.random(),
          hlAlpha: 0.35 + Math.random() * 0.55,
        })
      }
    }
  }

  /** Extra kleine bellen in de kroon — veel textuur, minder ‘effen wit’. */
  const addMicroCrown = (yMax: number, density: number) => {
    const rowStep = 5
    for (let y = 0; y < yMax; y += rowStep) {
      const count = Math.floor(w * density * 0.048)
      for (let j = 0; j < count; j += 1) {
        const hx = Math.random() * w
        const hy = y + Math.random() * (rowStep + 1)
        const r = 0.5 + Math.random() * 2.1
        cells.push({
          hx,
          hy,
          r,
          x: hx,
          y: hy,
          vx: 0,
          vy: 0,
          warmth: Math.random() * 8,
          brightness: 250 + Math.random() * 5,
          hlChance: 0.4 + Math.random() * 0.55,
          hlAlpha: 0.45 + Math.random() * 0.45,
        })
      }
    }
  }

  const s = FOAM_H / 150
  addMicroCrown(Math.min(125, Math.round(FOAM_H * 0.42)), 0.72)
  addZone(0, Math.round(52 * s), 1, 2.9, 0.52)
  addZone(Math.round(38 * s), Math.round(98 * s), 1.6, 4.4, 0.38)
  addZone(Math.round(82 * s), Math.round(138 * s), 2.6, 7.8, 0.22)
  addZone(Math.round(118 * s), FOAM_H + 14, 3.4, 11, 0.11)
  cells.sort((a, b) => a.r - b.r)

  const drips: FoamDrip[] = []
  const dc = 14 + Math.floor(Math.random() * 8)
  for (let d = 0; d < dc; d += 1) {
    const dx = Math.random() * w
    const sy = FOAM_H - 52 + Math.random() * 36
    const dl = 28 + Math.random() * 80
    const ww = 5 + Math.random() * 11
    const n = 6 + Math.floor(Math.random() * 11)
    for (let i = 0; i < n; i += 1) {
      const t = i / n
      const r = (1 - t * 0.72) * (1.4 + Math.random() * 2.8)
      if (r < 0.45) continue
      drips.push({
        hx: dx + (Math.random() - 0.5) * ww * (1 - t * 0.45),
        hy: sy + t * dl,
        r,
        x: 0,
        y: 0,
        vx: 0,
        vy: 0,
        alpha: 0.55 - t * 0.38,
      })
    }
  }
  for (const q of drips) {
    q.x = q.hx
    q.y = q.hy
  }
  return { cells, drips }
}

export function paintFoamFrame(
  ctx: CanvasRenderingContext2D,
  w: number,
  dpr: number,
  canvasH: number,
  cells: FoamCell[],
  drips: FoamDrip[],
  mx: number,
  my: number,
): void {
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  ctx.clearRect(0, 0, w, canvasH)

  const bg = ctx.createLinearGradient(0, 0, 0, canvasH)
  bg.addColorStop(0, "#fdf6d8")
  bg.addColorStop(0.12, "#fff4d2")
  bg.addColorStop(0.28, "#fcefb8")
  bg.addColorStop(0.52, "#f5e6a8")
  bg.addColorStop(0.66, "#f0cf40")
  bg.addColorStop(0.76, "#e6b41a")
  /** Doorzichtige onderrand → vaste shell-gradient loopt visueel door (geen harde lijn bier/kraag). */
  bg.addColorStop(0.84, "rgba(212, 160, 18, 0.5)")
  bg.addColorStop(0.91, "rgba(192, 138, 12, 0.16)")
  bg.addColorStop(0.96, "rgba(166, 114, 6, 0.04)")
  bg.addColorStop(1, "rgba(212, 160, 18, 0)")
  ctx.fillStyle = bg
  ctx.fillRect(0, 0, w, canvasH)

  /* Lichte glans, niet dekkend — bellen blijven zichtbaar na tekenen. */
  const topH = Math.min(72, Math.round(canvasH * 0.12))
  const top = ctx.createLinearGradient(0, 0, 0, topH)
  top.addColorStop(0, "rgba(255,255,255,0.42)")
  top.addColorStop(0.4, "rgba(255,252,240,0.22)")
  top.addColorStop(0.75, "rgba(255,250,235,0.08)")
  top.addColorStop(1, "rgba(255,254,240,0)")
  ctx.fillStyle = top
  ctx.fillRect(0, 0, w, topH)

  for (const c of cells) {
    const dx = c.x - mx
    const dy = c.y - my
    const dist = Math.sqrt(dx * dx + dy * dy)
    if (dist < REPEL && dist > 0) {
      const f = (1 - dist / REPEL) * REPEL_F * (c.r / 4.8)
      c.vx += (dx / dist) * f
      c.vy += (dy / dist) * f
    }
    c.vx += (c.hx - c.x) * 0.065
    c.vy += (c.hy - c.y) * 0.065
    c.vx *= 0.82
    c.vy *= 0.82
    c.x += c.vx
    c.y += c.vy
  }

  for (const d of drips) {
    const dx = d.x - mx
    const dy = d.y - my
    const dist = Math.sqrt(dx * dx + dy * dy)
    if (dist < REPEL && dist > 0) {
      const f = (1 - dist / REPEL) * REPEL_F * (d.r / 3.2)
      d.vx += (dx / dist) * f
      d.vy += (dy / dist) * f
    }
    d.vx += (d.hx - d.x) * 0.052
    d.vy += (d.hy - d.y) * 0.052
    d.vx *= 0.8
    d.vy *= 0.8
    d.x += d.vx
    d.y += d.vy
  }

  for (const c of cells) {
    const depth = c.hy / FOAM_H
    let alpha = 0.94
    if (depth >= 0.35 && depth < 0.72) alpha = 0.9 - (depth - 0.35) * 0.45
    else if (depth >= 0.72) alpha = 0.74 - (depth - 0.72) * 1.65
    if (alpha <= 0.05) continue
    const { x, y, r, warmth, brightness } = c
    if (r < 2.4) {
      ctx.beginPath()
      ctx.arc(x, y, r, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(${brightness},${brightness - warmth},${brightness - warmth * 2},${alpha})`
      ctx.fill()
    } else {
      const g = ctx.createRadialGradient(x - r * 0.22, y - r * 0.22, r * 0.12, x, y, r)
      g.addColorStop(
        0,
        `rgba(${brightness},${brightness - warmth},${brightness - warmth * 2},${Math.min(alpha + 0.08, 1)})`,
      )
      g.addColorStop(
        0.72,
        `rgba(${brightness - 6},${brightness - 10 - warmth},${brightness - 16 - warmth},${alpha})`,
      )
      g.addColorStop(1, `rgba(${brightness - 14},${brightness - 22},${brightness - 32},${alpha * 0.55})`)
      ctx.beginPath()
      ctx.arc(x, y, r, 0, Math.PI * 2)
      ctx.fillStyle = g
      ctx.fill()
    }
    ctx.beginPath()
    ctx.arc(x, y, r, 0, Math.PI * 2)
    ctx.strokeStyle = `rgba(175,165,130,${depth < 0.32 ? 0.09 : 0.16})`
    ctx.lineWidth = r < 2.4 ? 0.28 : 0.48
    ctx.stroke()
    if (r > 2.8 && c.hlChance > 0.28) {
      const hr = r * 0.32
      const hg = ctx.createRadialGradient(x - r * 0.28, y - r * 0.32, 0, x - r * 0.28, y - r * 0.32, hr)
      hg.addColorStop(0, `rgba(255,255,255,${c.hlAlpha})`)
      hg.addColorStop(1, "rgba(255,255,255,0)")
      ctx.beginPath()
      ctx.arc(x - r * 0.28, y - r * 0.32, hr, 0, Math.PI * 2)
      ctx.fillStyle = hg
      ctx.fill()
    }
  }

  for (const d of drips) {
    if (d.alpha <= 0) continue
    ctx.beginPath()
    ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(255,253,244,${d.alpha})`
    ctx.fill()
    ctx.strokeStyle = `rgba(175,165,130,${d.alpha * 0.22})`
    ctx.lineWidth = 0.28
    ctx.stroke()
  }
}

export function paintFoamStatic(
  ctx: CanvasRenderingContext2D,
  w: number,
  dpr: number,
  canvasH: number,
): void {
  const { cells, drips } = initFoam(w)
  for (const c of cells) {
    c.x = c.hx
    c.y = c.hy
    c.vx = 0
    c.vy = 0
  }
  for (const d of drips) {
    d.x = d.hx
    d.y = d.hy
  }
  paintFoamFrame(ctx, w, dpr, canvasH, cells, drips, -99999, -99999)
}
