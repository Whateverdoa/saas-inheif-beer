# Business Setup & Compliance Module

This module provides comprehensive business setup and compliance functionality for the SaaS OGOS API.

## Features

### 1. Legal Documents
- **Terms of Service** - Public endpoint at `/legal/terms`
- **Privacy Policy** - Public endpoint at `/legal/privacy`
- **Data Processing Agreement (DPA)** - Public endpoint at `/legal/dpa`
- **Cookie Policy** - Public endpoint at `/legal/cookies`

All documents support markdown and HTML formats.

### 2. Invoice Generation
- Automatic invoice generation from Stripe/Polar payments
- HTML invoice templates with Dutch formatting
- Support for VAT calculations (21% default)
- Invoice storage and retrieval

**Endpoints:**
- `POST /invoices/generate` - Generate invoice from payment
- `GET /invoices/{invoice_id}` - Get invoice details
- `GET /invoices/{invoice_id}/html` - Get invoice as HTML
- `GET /invoices` - List invoices (paginated)
- `POST /invoices/{invoice_id}/sync-eboekhouden` - Sync to e-boekhouden

### 3. e-boekhouden Integration
- Automatic transaction syncing from Stripe/Polar webhooks
- Invoice syncing to e-boekhouden
- Configurable via environment variables

**Configuration:**
```bash
EBOEKHOUDEN_API_KEY=your_api_key
EBOEKHOUDEN_COMPANY_ID=your_company_id
EBOEKHOUDEN_SYNC_ENABLED=true
```

### 4. Compliance Checklist
- Launch checklist tracking
- Compliance status monitoring
- Admin endpoints for updating checklist items

**Endpoints:**
- `GET /compliance/checklist` - Get checklist status
- `PUT /compliance/checklist/{item_id}` - Update checklist item
- `GET /compliance/status` - Get overall compliance status

**Checklist Items:**
- KvK registration complete
- BTW number obtained
- Bank account connected
- Bookkeeping setup (e-boekhouden)
- Insurance obtained
- Legal docs published
- Stripe connected to bank
- Polar connected to bank
- Test invoice created

### 5. Branding Configuration
- Company information management
- Branding settings (logo, colors, fonts)
- Domain and email configuration

**Endpoints:**
- `GET /compliance/branding` - Get branding config
- `PUT /compliance/branding` - Update branding config
- `GET /compliance/company-info` - Get company information

## Environment Variables

### Company Information
```bash
COMPANY_NAME=Your Company Name
COMPANY_KVK_NUMBER=12345678
COMPANY_BTW_NUMBER=NL123456789B01
COMPANY_BANK_ACCOUNT=NL12ABCD1234567890
COMPANY_ADDRESS=123 Main St, Amsterdam
COMPANY_DOMAIN=example.com
COMPANY_EMAIL=contact@example.com
```

### Branding
```bash
BRANDING_LOGO_URL=https://example.com/logo.png
BRANDING_PRIMARY_COLOR=#2563eb
BRANDING_SECONDARY_COLOR=#64748b
BRANDING_FONT_FAMILY=Inter
```

### e-boekhouden
```bash
EBOEKHOUDEN_API_KEY=your_api_key
EBOEKHOUDEN_COMPANY_ID=your_company_id
EBOEKHOUDEN_SYNC_ENABLED=true
```

## Webhook Integration

### Stripe Webhooks
When `payment_intent.succeeded` is received:
1. Submit order to OGOS (if order_id in metadata)
2. Generate invoice automatically
3. Sync transaction to e-boekhouden (if enabled)
4. Sync invoice to e-boekhouden (if enabled)

### Polar Webhooks
When payment events are received:
1. Generate invoice automatically
2. Sync transaction to e-boekhouden (if enabled)
3. Sync invoice to e-boekhouden (if enabled)

## File Structure

```
app/
├── models/
│   ├── compliance.py      # Compliance models
│   ├── invoice.py         # Invoice models
│   └── branding.py        # Branding models
├── routers/
│   ├── legal.py           # Legal document endpoints
│   ├── invoices.py        # Invoice endpoints
│   └── compliance.py      # Compliance endpoints
├── services/
│   ├── compliance_service.py  # Legal document service
│   ├── invoice_service.py     # Invoice generation service
│   └── eboekhouden_service.py # e-boekhouden integration
└── templates/
    ├── invoice.html       # Invoice HTML template
    └── legal/             # Legal document templates
        ├── terms_of_service.md
        ├── privacy_policy.md
        ├── dpa.md
        └── cookie_policy.md
```

## Documentation

- `docs/business-setup.md` - Manual setup guide
- `docs/eboekhouden-setup.md` - e-boekhouden integration guide
- `docs/legal-compliance.md` - Legal compliance guide

## Usage Examples

### Get Legal Document
```bash
curl http://localhost:8000/legal/terms?format=html
```

### Generate Invoice
```bash
curl -X POST http://localhost:8000/invoices/generate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_id": "pi_123",
    "provider": "stripe",
    "amount": 100.00,
    "currency": "EUR",
    "customer_name": "John Doe",
    "customer_email": "john@example.com"
  }'
```

### Get Compliance Checklist
```bash
curl http://localhost:8000/compliance/checklist \
  -H "Authorization: Bearer <token>"
```

### Update Checklist Item
```bash
curl -X PUT http://localhost:8000/compliance/checklist/kvk_registration \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "notes": "KvK number: 12345678"
  }'
```

## Testing

All endpoints require Clerk authentication except legal document endpoints (public).

For testing:
1. Set up Clerk authentication
2. Get session token from Clerk
3. Use token in Authorization header

## Notes

- Legal documents use template variables that are replaced with company information from environment variables
- Invoice generation happens automatically on successful payments
- e-boekhouden sync can be disabled by setting `EBOEKHOUDEN_SYNC_ENABLED=false`
- Compliance checklist is stored in memory (can be extended to persistent storage)
- All operations are logged for debugging and auditing

## Next Steps

1. Customize legal document templates with your specific terms
2. Configure e-boekhouden API credentials
3. Set company information in environment variables
4. Complete launch checklist items
5. Test invoice generation with sample payments
6. Verify e-boekhouden sync is working

