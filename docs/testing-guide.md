# Testing & Configuration Guide - Business Setup Module

## Quick Start

### 1. Install Dependencies

```bash
cd saas-inheif-beer
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and update with your values:

```bash
cp .env.example .env
```

Edit `.env` and set:
- Company information (name, KvK, BTW, address, email)
- Branding configuration (logo, colors, fonts)
- e-boekhouden credentials (if using)
- Stripe/Polar webhook secrets
- Clerk authentication keys

### 3. Run Tests

```bash
# Run business setup module tests
python tests/test_business_setup.py

# Run all tests
pytest tests/
```

### 4. Start the Server

```bash
uvicorn app.main:app --reload --port 8000
```

## Testing Endpoints

### Legal Documents (Public Endpoints)

Test legal documents without authentication:

```bash
# Terms of Service (markdown)
curl http://localhost:8000/legal/terms?format=markdown

# Terms of Service (HTML)
curl http://localhost:8000/legal/terms?format=html

# Privacy Policy
curl http://localhost:8000/legal/privacy

# DPA
curl http://localhost:8000/legal/dpa

# Cookie Policy
curl http://localhost:8000/legal/cookies

# List all documents
curl http://localhost:8000/legal/documents
```

### Compliance Checklist (Protected - Requires Auth)

```bash
# Get Clerk session token first (from frontend or Clerk dashboard)
CLERK_TOKEN="your_clerk_session_token"

# Get checklist status
curl http://localhost:8000/compliance/checklist \
  -H "Authorization: Bearer $CLERK_TOKEN"

# Update checklist item
curl -X PUT http://localhost:8000/compliance/checklist/kvk_registration \
  -H "Authorization: Bearer $CLERK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "notes": "KvK number: 12345678"
  }'

# Get compliance status
curl http://localhost:8000/compliance/status \
  -H "Authorization: Bearer $CLERK_TOKEN"

# Get branding config
curl http://localhost:8000/compliance/branding \
  -H "Authorization: Bearer $CLERK_TOKEN"

# Get company info
curl http://localhost:8000/compliance/company-info \
  -H "Authorization: Bearer $CLERK_TOKEN"
```

### Invoice Generation (Protected - Requires Auth)

```bash
# Generate invoice
curl -X POST http://localhost:8000/invoices/generate \
  -H "Authorization: Bearer $CLERK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_id": "pi_test_123",
    "provider": "stripe",
    "amount": 100.00,
    "currency": "EUR",
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "customer_address": "123 Main St, Amsterdam",
    "description": "Test payment"
  }'

# Get invoice HTML
curl http://localhost:8000/invoices/{invoice_id}/html \
  -H "Authorization: Bearer $CLERK_TOKEN"

# List invoices
curl http://localhost:8000/invoices?limit=10 \
  -H "Authorization: Bearer $CLERK_TOKEN"

# Sync invoice to e-boekhouden
curl -X POST http://localhost:8000/invoices/{invoice_id}/sync-eboekhouden \
  -H "Authorization: Bearer $CLERK_TOKEN"
```

## Environment Variables Checklist

### Required for Basic Functionality

- [ ] `COMPANY_NAME` - Your company name
- [ ] `COMPANY_KVK_NUMBER` - KvK registration number
- [ ] `COMPANY_BTW_NUMBER` - BTW/VAT number
- [ ] `COMPANY_EMAIL` - Contact email address
- [ ] `BRANDING_PRIMARY_COLOR` - Primary brand color (hex)
- [ ] `BRANDING_FONT_FAMILY` - Font family name

### Optional but Recommended

- [ ] `COMPANY_BANK_ACCOUNT` - Bank account number
- [ ] `COMPANY_ADDRESS` - Company address
- [ ] `COMPANY_DOMAIN` - Company domain
- [ ] `BRANDING_LOGO_URL` - Logo URL/path
- [ ] `BRANDING_SECONDARY_COLOR` - Secondary color

### For e-boekhouden Integration

- [ ] `EBOEKHOUDEN_API_KEY` - API key from e-boekhouden
- [ ] `EBOEKHOUDEN_COMPANY_ID` - Company ID from e-boekhouden
- [ ] `EBOEKHOUDEN_SYNC_ENABLED` - Set to `true` to enable syncing

### For Authentication

- [ ] `CLERK_SECRET_KEY` - Clerk secret key
- [ ] `CLERK_PUBLISHABLE_KEY` - Clerk publishable key (for frontend)

### For Payment Processing

- [ ] `STRIPE_API_KEY` - Stripe API key
- [ ] `STRIPE_WEBHOOK_SECRET` - Stripe webhook signing secret
- [ ] `POLAR_WEBHOOK_SECRET` - Polar webhook secret

## Testing Checklist

### Legal Documents
- [ ] Terms of Service renders correctly
- [ ] Privacy Policy renders correctly
- [ ] DPA renders correctly
- [ ] Cookie Policy renders correctly
- [ ] Company information is replaced in templates
- [ ] Both markdown and HTML formats work

### Invoice Generation
- [ ] Invoice created from payment data
- [ ] Invoice includes correct VAT calculation (21%)
- [ ] Invoice HTML renders correctly
- [ ] Invoice includes company information
- [ ] Invoice includes customer information
- [ ] Invoice can be retrieved by ID
- [ ] Invoice list pagination works

### Compliance Checklist
- [ ] Checklist items load correctly
- [ ] Can update checklist item status
- [ ] Completion percentage calculates correctly
- [ ] Compliance status endpoint works
- [ ] Branding config loads correctly
- [ ] Company info loads correctly

### e-boekhouden Integration
- [ ] Connection test works (if enabled)
- [ ] Transaction sync works (if enabled)
- [ ] Invoice sync works (if enabled)
- [ ] Errors are handled gracefully when disabled

## Troubleshooting

### Legal Documents Not Rendering

**Problem:** Company information not replaced in templates

**Solution:**
- Check environment variables are set correctly
- Verify template files exist in `app/templates/legal/`
- Check service logs for errors

### Invoice Generation Fails

**Problem:** Invoice not created or errors occur

**Solution:**
- Verify all required fields are provided
- Check amount is positive number
- Ensure currency code is valid (EUR, USD, etc.)
- Check invoice service logs

### e-boekhouden Sync Not Working

**Problem:** Transactions not syncing

**Solution:**
- Verify `EBOEKHOUDEN_SYNC_ENABLED=true`
- Check API credentials are correct
- Test connection endpoint first
- Check API logs for errors
- Verify e-boekhouden API endpoint is correct

### Authentication Issues

**Problem:** Protected endpoints return 401

**Solution:**
- Verify Clerk token is valid
- Check token expiration
- Ensure `Authorization: Bearer {token}` header is set
- Verify Clerk secret key is configured

## Next Steps After Testing

1. **Customize Legal Documents:**
   - Edit templates in `app/templates/legal/`
   - Review with legal counsel
   - Update company-specific terms

2. **Configure e-boekhouden:**
   - Sign up for e-boekhouden account
   - Get API credentials
   - Test sync with test transactions
   - Enable automatic syncing

3. **Complete Launch Checklist:**
   - Update checklist items via API
   - Complete all required items
   - Verify 100% compliance

4. **Production Deployment:**
   - Set production environment variables
   - Configure production webhook endpoints
   - Test end-to-end payment flow
   - Monitor sync logs

## Additional Resources

- [Business Setup Guide](docs/business-setup.md)
- [e-boekhouden Setup Guide](docs/eboekhouden-setup.md)
- [Legal Compliance Guide](docs/legal-compliance.md)
- [Business Setup Module Overview](BUSINESS_SETUP_MODULE.md)

