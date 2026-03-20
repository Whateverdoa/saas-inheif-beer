/** All UI copy keyed by section — one shape for every locale. */

export type HomeMessages = {
  badge: string
  titleLine1: string
  titleLine2: string
  intro: string
  ctaOrder: string
  ctaExamples: string
  features: { icon: string; title: string; text: string }[]
  showcaseTitle: string
  showcaseSubtitle: string
  labels: { name: string; type: string; abv: string }[]
  howTitle: string
  steps: { n: string; title: string; desc: string }[]
  pricingTitle: string
  pricingSubtitle: string
  tiers: {
    tier: string
    price: string
    unit: string
    feat: string[]
    cta: string
    featured?: boolean
  }[]
  finalTitle: string
  finalSubtitle: string
  /**
   * Full line after "© {year} ", e.g.
   * VILA-BIER VRIJMIBO · Bieretiketten · Mogelijk gemaakt door OGOS ---Vila-etiketten
   */
  footer: string
}

export type OrderMessages = {
  backHome: string
  title: string
  subtitle: string
  /** Shown under subtitle (e.g. intro pricing promo). */
  promoLine: string
  standardFormatsTitle: string
  standardFormatsHint: string
  loadingFormats: string
  formatsError: string
  clearStandard: string
  yourDetails: string
  labelType: string
  dimLabel: string
  dimPh: string
  material: string
  quantity: string
  quantityUnit: string
  /** Label above preset quantity chips. */
  quantityQuickPick: string
  /** Label for the numeric oplage input. */
  quantityInputLabel: string
  /** Shown when typed quantity exceeds slider max. */
  quantityBeyondSlider: string
  notes: string
  notesPh: string
  shipTitle: string
  kvkFilled: string
  street: string
  city: string
  contact: string
  company: string
  companyPh: string
  email: string
  phone: string
  disclaimer: string
  submit: string
  footer: string
  alert: string
  mats: { id: string; icon: string; name: string; desc: string }[]
  shapes: { id: string; icon: string; name: string }[]
}

export type KvkMessages = {
  label: string
  placeholder: string
  lookup: string
  idle: string
  searching: string
  foundLive: string
  mockNote: string
  invalid: string
  testLine: string
  apiHint: string
  clear: string
}

export type BeerToolMessages = {
  loading: string
  errorFetch: string
  backHome: string
  title: string
  subtitle: string
  quoteLink: string
  complianceLink: string
  step1: string
  category: string
  allCategories: string
  step2: string
  recommended: string
  step3: string
  qty: string
  summaryFormat: string
  summaryDimensions: string
  summarySubstrate: string
  summaryQty: string
  summaryQtyUnit: string
  uploadTitle: string
  uploadHint: string
  uploadSub: string
  checkout: string
  selectBoth: string
  refTitle: string
  thFormat: string
  thDimensions: string
  thCategory: string
  thDescription: string
  waterproof: string
  eco: string
}

export type ComplianceToolMessages = {
  loading: string
  back: string
  title: string
  subtitle: string
  targetLangs: string
  selected: string
  beerDetails: string
  abv: string
  producer: string
  country: string
  ingredients: string
  allergens: string
  generate: string
  generating: string
  output: string
  empty: string
  copy: string
}

export type AppMessages = {
  meta: { title: string; description: string }
  nav: { language: string }
  home: HomeMessages
  order: OrderMessages
  kvk: KvkMessages
  beerTool: BeerToolMessages
  complianceTool: ComplianceToolMessages
}
