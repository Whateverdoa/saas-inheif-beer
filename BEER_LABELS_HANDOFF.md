# Beer Labels Feature - Handoff Document

## Project Overview

**Project:** OGOS SaaS Platform - Beer Labels Module  
**Status:** Planning Phase  
**Last Updated:** 2026-03-19

---

## 1. Current System Capabilities

The existing platform is a **label printing SaaS** that:
- Accepts PDF uploads for custom label printing
- Validates PDFs (CMYK color space, trimbox, bleedbox, file size)
- Integrates with OGOS (Optimum Group Order Service) for production
- Supports B2B (organization accounts) and B2C (individual) orders
- Handles payments via Stripe and Polar
- Uses Clerk for authentication

### Tech Stack
| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python 3.11+) |
| Frontend | Next.js 16, React 19, TypeScript |
| Auth | Clerk |
| Payments | Stripe, Polar |
| PDF Processing | PyMuPDF |
| Database | SQLAlchemy + SQLite (async) |
| UI Components | Radix UI, Tailwind CSS 4 |
| Deployment | Vercel (target) |

---

## 2. Beer Labels Feature Roadmap

### Phase 1: Foundation (MVP) ✅ COMPLETED
**Goal:** Accept beer label PDFs in standard industry formats

**Completed:**
- ✅ Beer label type definitions (bottle + Dutch can formats)
- ✅ Beer-specific substrate recommendations
- ✅ API endpoints for label types, substrates, categories
- ✅ EU multi-language support (all 24 official languages)
- ✅ Compliance text generator with translations
- ✅ Simple ordering UI (label selector, substrate picker, quantity)
- ✅ Compliance text generator page

#### 2.1 Supported Beer Label Types

**Bottle Labels:**
| Label Type | Dimensions (mm) | Use Case |
|------------|-----------------|----------|
| **Neck Label** | 30-50 × 80-120 | Bottle neck wrap |
| **Front Body Label** | 70-90 × 90-120 | Main brand label |
| **Back Body Label** | 70-90 × 50-80 | Ingredients/legal info |
| **Wraparound Label** | 200-280 × 80-120 | Full bottle wrap |
| **Shrink Sleeve** | Variable | Full container coverage |

**Can Labels (Standard Dutch Formats):**
| Formaat Blik | Formaat Etiket | ID |
|--------------|----------------|-----|
| 25cl Slim Can | 160 × 110 mm | `can-25cl-slim` |
| 25cl Sleek Can | 175 × 90 mm | `can-25cl-sleek` |
| 33cl Standaard | 205 × 85 mm | `can-33cl-standard` |
| 44cl Standaard | 205 × 120 mm | `can-44cl-standard` |
| 50cl Standaard | 205 × 135 mm | `can-50cl-standard` |

#### 2.2 Beer-Specific Substrates
| Substrate | Properties | Best For |
|-----------|------------|----------|
| PP Glans Wit | Waterproof, glossy | Chilled bottles |
| PP Mat Wit | Waterproof, matte | Premium craft beers |
| PP Transparant | See-through, waterproof | Minimalist designs |
| Natureflex | Biodegradable | Eco-conscious brands |
| Tintoretto Gesso | Textured, premium | Artisan/craft beers |

#### 2.3 Initial Implementation
- [x] Add beer label type selection to order form
- [x] Pre-populate dimensions based on label type
- [x] Add beer-specific substrate recommendations
- [x] Create beer label category in product catalog

---

### Phase 2: EU Compliance Labels ✅ PARTIALLY COMPLETE
**Goal:** Automated generation of legally-required beer label content

**Completed:**
- ✅ Multi-language translation system (all 24 EU languages)
- ✅ Compliance text generator API (`POST /beer/compliance-text`)
- ✅ Allergen translation support (gluten, barley, wheat, sulphites)
- ✅ Label text translations (ingredients, contains, ABV, warnings, etc.)
- ✅ Frontend compliance text generator page (`/beer/compliance`)

#### EU Regulation 1169/2011 Requirements
| Element | Requirement | Status |
|---------|-------------|--------|
| **Ingredients List** | Mandatory | ✅ Done |
| **Allergens** | Bold/highlighted | ✅ Auto-detect + translate |
| **ABV %** | Mandatory for >1.2% | ✅ Done |
| **Net Volume** | Mandatory | 🔜 Dropdown needed |
| **Country of Origin** | Mandatory | ✅ Done |
| **Producer Info** | Name + address | ✅ Done |
| **Lot Number** | Traceability | 🔜 Auto-generate |
| **Best Before** | Date format | 🔜 Date picker |
| **Nutritional Info** | Per 100ml | 🔜 Calculator |
| **Recycling Symbols** | Country-specific | 🔜 Symbol library |

#### Remaining Work
- [ ] Nutritional info calculator from ingredients
- [ ] Recycling symbol library (per country)
- [ ] PDF overlay/generation for compliance labels
- [ ] Lot number auto-generation
- [ ] Best before date formatting per country

---

### Phase 3: Beer-Specific Templates 🔜 Want-to-Have
**Goal:** Pre-designed label templates optimized for beer bottles/cans

#### Template Categories
1. **Craft Beer** - Artisan, hand-drawn aesthetics
2. **IPA/Pale Ale** - Bold, hop-forward designs
3. **Stout/Porter** - Dark, rich imagery
4. **Lager/Pilsner** - Clean, refreshing look
5. **Wheat Beer** - Light, summery feel
6. **Seasonal** - Holiday/limited edition
7. **Minimalist** - Modern, simple designs

#### Template Features
- Editable text zones (brand name, beer name, ABV, etc.)
- Swappable color schemes
- Multiple layout variants per style
- Print-ready output (CMYK, bleed, crop marks)

#### Technical Implementation
- Store templates as layered PDFs or SVGs
- Use PDF manipulation library for text replacement
- Preview rendering in browser (Canvas/SVG)
- Export to print-ready PDF

---

### Phase 4: Beer Label Validator 🔜 Want-to-Have
**Goal:** Additional PDF validation rules specific to beer labels

#### Validation Rules
| Rule | Description | Severity |
|------|-------------|----------|
| **Minimum Font Size** | Legal text ≥ 1.2mm x-height | Error |
| **ABV Visibility** | ABV must be in contrasting color | Warning |
| **Allergen Formatting** | Allergens must be bold/emphasized | Error |
| **Bleed Area** | 3mm bleed required | Error |
| **Safe Zone** | 3mm from trim for critical text | Warning |
| **Color Mode** | Must be CMYK | Error |
| **Resolution** | ≥300 DPI for images | Warning |
| **Barcode Readability** | EAN-13 must be scannable | Error |
| **Required Elements** | Check for mandatory EU elements | Error |

#### Implementation
1. Extend existing `PDFValidator` class
2. Add text extraction and analysis
3. Implement barcode detection
4. Create validation report with fix suggestions

---

### Phase 5: Full Frontend Integration 🔜 Want-to-Have
**Goal:** Complete order flow with existing components (PDF upload, price calculation, checkout)

#### Current State (Simple UI)
The current `/beer` page is a simplified ordering interface with:
- Label type selector
- Substrate picker
- Quantity input
- Compliance text generator link

#### Full Integration (Option A)
Integrate with existing frontend components from `frontend/components/orders/`:
- `OrderForm.tsx` - Full order form with validation
- `PDFUpload.tsx` - Drag-and-drop PDF upload with preview
- Price calculation via backend API
- Checkout flow with Stripe/Polar

#### Implementation Steps
1. Create API clients in `frontend/lib/api/`:
   - `pdf.ts` - PDF validation API
   - `price.ts` - Price calculation API
   - `orders.ts` - Order submission API
2. Create types in `frontend/lib/types/orders.ts`
3. Integrate beer label types into `OrderForm`
4. Add beer-specific validation rules to PDF upload
5. Connect to payment flow

#### Files to Create/Modify
```
frontend/
├── lib/
│   ├── api/
│   │   ├── pdf.ts          # PDF validation client
│   │   ├── price.ts        # Price calculation client
│   │   └── orders.ts       # Order submission client
│   └── types/
│       └── orders.ts       # Order types
├── app/
│   └── beer/
│       └── order/
│           └── page.tsx    # Full order page
└── components/
    └── beer/
        └── BeerOrderForm.tsx  # Beer-specific order form
```

---

### Phase 6: Full Beer Label Designer 🔜 Want-to-Have
**Goal:** Visual editor where users can design beer labels from scratch

#### Core Features
- Drag-and-drop interface
- Text editing with font selection
- Image upload and placement
- Shape tools (rectangles, circles, lines)
- Layer management
- Undo/redo
- Zoom and pan
- Grid and snap-to guides

#### Advanced Features
- Brand asset library (logos, icons)
- Color palette management
- Template starting points
- Real-time collaboration
- Version history
- Export options (PDF, PNG, SVG)

#### Technical Approach
**Option A: Canvas-based (Fabric.js)**
- Pros: Full control, performant
- Cons: Complex implementation

**Option B: SVG-based (React-Konva)**
- Pros: React integration, good for shapes
- Cons: Performance with many elements

**Option C: Existing Solution (Polotno)**
- Pros: Feature-rich, faster development
- Cons: License cost, less customization

**Recommendation:** Start with Fabric.js for MVP, evaluate Polotno for acceleration.

---

## 3. Database Schema Extensions

### Beer Label Types Table
```sql
CREATE TABLE beer_label_types (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,  -- 'neck', 'body', 'back', 'wraparound', 'can', 'sleeve'
    width_mm REAL NOT NULL,
    height_mm REAL NOT NULL,
    description TEXT,
    recommended_substrates TEXT,  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Beer Compliance Data Table
```sql
CREATE TABLE beer_compliance_data (
    id TEXT PRIMARY KEY,
    order_id TEXT REFERENCES orders(order_id),
    beer_name TEXT NOT NULL,
    abv_percent REAL NOT NULL,
    volume_ml INTEGER NOT NULL,
    ingredients TEXT NOT NULL,  -- JSON array
    allergens TEXT,  -- JSON array (auto-detected)
    country_of_origin TEXT NOT NULL,
    producer_name TEXT NOT NULL,
    producer_address TEXT NOT NULL,
    lot_number TEXT,
    best_before DATE,
    nutritional_info TEXT,  -- JSON object
    recycling_symbols TEXT,  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Beer Templates Table
```sql
CREATE TABLE beer_templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    label_type_id TEXT REFERENCES beer_label_types(id),
    template_data TEXT NOT NULL,  -- JSON or base64 PDF
    thumbnail_url TEXT,
    is_premium BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. API Endpoints (Planned)

### Beer Label Types
```
GET  /api/beer/label-types          # List all label types
GET  /api/beer/label-types/{id}     # Get specific label type
```

### Beer Compliance
```
POST /api/beer/compliance           # Create compliance data
GET  /api/beer/compliance/{id}      # Get compliance data
PUT  /api/beer/compliance/{id}      # Update compliance data
POST /api/beer/compliance/validate  # Validate compliance data
POST /api/beer/compliance/generate  # Generate compliance label
```

### Beer Templates
```
GET  /api/beer/templates            # List templates
GET  /api/beer/templates/{id}       # Get template
POST /api/beer/templates/{id}/apply # Apply template with data
```

### Beer Label Validation
```
POST /api/beer/validate-pdf         # Validate beer label PDF
```

---

## 5. Environment Variables (Additional)

```env
# Beer Labels Feature
BEER_LABELS_ENABLED=true
BEER_COMPLIANCE_STRICT_MODE=true  # Enforce all EU requirements

# Template Storage (future)
TEMPLATE_STORAGE_URL=
TEMPLATE_STORAGE_KEY=
```

---

## 6. Deployment Configuration

### Vercel Deployment
- **Frontend:** Next.js app deployed as Vercel project
- **Backend:** FastAPI deployed as Vercel Serverless Functions
- **Database:** Consider Vercel Postgres or external (Supabase, PlanetScale)

### Environment Setup
1. Create Vercel project
2. Link GitHub repository
3. Configure environment variables
4. Set up preview deployments for PRs

---

## 7. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Beer label orders | 100/month (month 3) | Order count with beer label type |
| Template usage | 30% of orders | Orders using templates |
| Compliance pass rate | 95% | Validation success rate |
| Designer adoption | 20% of users | Users creating custom designs |

---

## 8. Open Questions

1. **Pricing Model:** Should beer labels have different pricing tiers?
2. **Template Licensing:** Create in-house or license existing designs?
3. **Compliance Liability:** Disclaimer for auto-generated compliance text?
4. **Multi-language:** Support for EU languages on labels?
5. **Barcode Generation:** Include EAN-13 generation or require upload?

---

## 9. Next Steps

### Immediate (This Sprint) ✅ COMPLETED
- [x] Create handoff document
- [x] Prepare Vercel deployment configuration
- [x] Add beer label type definitions to codebase
- [x] Update order form with beer label options
- [x] Implement EU multi-language support (24 languages)
- [x] Create compliance text generator
- [x] Deploy to Vercel

### Short-term (Next 2 Sprints)
- [ ] Full frontend integration (Phase 5 - Option A)
- [ ] PDF upload with beer-specific validation
- [ ] Price calculation integration
- [ ] Checkout flow connection

### Medium-term (Next Quarter)
- [ ] Nutritional info calculator
- [ ] Recycling symbol library
- [ ] PDF compliance label overlay/generation
- [ ] Basic template system
- [ ] Enhanced PDF validation for beer labels

---

## 10. References

- [EU Regulation 1169/2011](https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX%3A32011R1169) - Food Information to Consumers
- [EU Regulation 2019/787](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32019R0787) - Spirit drinks (for reference)
- [Brewers of Europe Labelling Guide](https://brewersofeurope.org/) - Industry best practices
- [OGOS API Documentation](internal) - Label printing integration

---

*Document maintained by: Development Team*  
*Review cycle: Bi-weekly*
