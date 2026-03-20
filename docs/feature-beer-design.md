# Feature: Beer-themed design & product showcase

**Goal:** Give the app a clear beer identity and use the UI to show bottles, cans, and label formats so it feels like a beer-label product, not a generic SaaS.

**Scope (suggested):**

- **Home page**
  - Hero with beer-focused headline and optional imagery (bottles, cans, or illustrated hero).
  - Product showcase: visual representation of what we offer (e.g. bottle + can + label formats).
  - Keep existing cards (Beer Labels, Custom, Wine, Spirits) but align styling with the beer theme.

- **Beer label page (`/beer`)**
  - Stronger beer vibe: imagery or icons for categories (neck, front/back body, can, shrink sleeve).
  - Optional: small “product” visuals (e.g. bottle/can silhouettes) next to format choices.
  - Consistent palette (e.g. amber/gold, dark tones) and typography.

- **Assets**
  - Decide: photos (bottles/cans), illustrations, or SVG/icons.
  - Place assets under e.g. `frontend/public/` or `frontend/public/images/beer/` and reference in components.

**Out of scope for this feature (for now):** Backend changes, new product types, checkout flow.

**Acceptance:**
- [x] Home page has a clear beer-focused hero and/or product showcase (bottles/cans/labels).
- [x] Beer label page feels on-theme (beer, bottles, cans) and uses the chosen asset style.
- [x] Design is responsive and works in light/dark if we keep dark mode.

**Notes:**
- Current stack: Next.js, Tailwind, existing amber/zinc palette.
- No Figma or design system yet; we can define a small set of tokens (colors, radii) in this feature.
