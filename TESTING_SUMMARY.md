# Testing & Configuration Summary

## ✅ Completed Setup

### Test Files Created

1. **`tests/test_business_setup.py`** - Comprehensive unit tests for:
   - Environment variable validation
   - Legal document service
   - Invoice generation service
   - e-boekhouden integration (connection test)

2. **`tests/test_api_endpoints.py`** - API endpoint tests for:
   - Health check endpoint
   - Legal document endpoints (public)

3. **`env.example`** - Environment variable template with all required variables

4. **`docs/testing-guide.md`** - Comprehensive testing guide with:
   - Setup instructions
   - Endpoint testing examples
   - Configuration checklist
   - Troubleshooting guide

### Test Results

✅ **All unit tests passed!** (4/4 tests)

- Environment Variables: ✅ PASSED
- Legal Documents: ✅ PASSED  
- Invoice Generation: ✅ PASSED
- e-boekhouden Integration: ✅ PASSED (disabled, as expected)

## 🚀 Next Steps for Testing

### 1. Start the Development Server

```bash
cd webhooks-skeleton
source .venv/bin/activate  # if using venv
uvicorn app.main:app --reload --port 8000
```

### 2. Configure Environment Variables

Create a `.env` file based on `env.example`:

```bash
cp env.example .env
# Edit .env with your actual values
```

**Minimum required variables:**
```bash
COMPANY_NAME=Your Company Name
COMPANY_KVK_NUMBER=12345678
COMPANY_BTW_NUMBER=NL123456789B01
COMPANY_EMAIL=contact@example.com
BRANDING_PRIMARY_COLOR=#2563eb
BRANDING_FONT_FAMILY=Inter
EBOEKHOUDEN_SYNC_ENABLED=false
```

### 3. Test API Endpoints

Once the server is running, test the endpoints:

```bash
# Test legal documents (public endpoints)
python3 tests/test_api_endpoints.py

# Or manually test:
curl http://localhost:8000/legal/terms
curl http://localhost:8000/legal/privacy
curl http://localhost:8000/legal/documents
```

### 4. Test Protected Endpoints

Protected endpoints require Clerk authentication:

1. **Get Clerk Session Token:**
   - Sign in via Clerk frontend
   - Get session token from Clerk SDK
   - Or use Clerk dashboard for testing

2. **Test Compliance Endpoints:**
```bash
CLERK_TOKEN="your_clerk_session_token"

curl http://localhost:8000/compliance/checklist \
  -H "Authorization: Bearer $CLERK_TOKEN"

curl http://localhost:8000/compliance/status \
  -H "Authorization: Bearer $CLERK_TOKEN"
```

3. **Test Invoice Endpoints:**
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
    "description": "Test payment"
  }'
```

### 5. Test e-boekhouden Integration (Optional)

If you have e-boekhouden credentials:

1. **Update environment variables:**
```bash
EBOEKHOUDEN_API_KEY=your_actual_api_key
EBOEKHOUDEN_COMPANY_ID=your_actual_company_id
EBOEKHOUDEN_SYNC_ENABLED=true
```

2. **Test connection:**
```bash
python3 tests/test_business_setup.py
```

3. **Test sync manually:**
```bash
# Generate invoice first, then sync
curl -X POST http://localhost:8000/invoices/{invoice_id}/sync-eboekhouden \
  -H "Authorization: Bearer $CLERK_TOKEN"
```

## 📋 Configuration Checklist

### Company Information
- [ ] Set `COMPANY_NAME`
- [ ] Set `COMPANY_KVK_NUMBER` (after KvK registration)
- [ ] Set `COMPANY_BTW_NUMBER` (after KvK registration)
- [ ] Set `COMPANY_EMAIL`
- [ ] Set `COMPANY_ADDRESS` (optional but recommended)
- [ ] Set `COMPANY_BANK_ACCOUNT` (optional but recommended)

### Branding
- [ ] Set `BRANDING_PRIMARY_COLOR`
- [ ] Set `BRANDING_SECONDARY_COLOR`
- [ ] Set `BRANDING_FONT_FAMILY`
- [ ] Set `BRANDING_LOGO_URL` (optional)

### Legal Documents
- [ ] Review and customize legal document templates
- [ ] Update company-specific terms
- [ ] Test all 4 legal document endpoints
- [ ] Verify company information is replaced correctly

### Invoice Generation
- [ ] Test invoice creation
- [ ] Verify VAT calculation (21% default)
- [ ] Check invoice HTML rendering
- [ ] Test invoice listing

### Compliance Checklist
- [ ] Complete KvK registration → update checklist
- [ ] Get BTW number → update checklist
- [ ] Connect bank account → update checklist
- [ ] Set up e-boekhouden → update checklist
- [ ] Get insurance → update checklist
- [ ] Publish legal docs → update checklist
- [ ] Connect Stripe to bank → update checklist
- [ ] Connect Polar to bank → update checklist
- [ ] Create test invoice → update checklist

### e-boekhouden Integration
- [ ] Sign up for e-boekhouden account
- [ ] Get API credentials
- [ ] Test connection
- [ ] Enable automatic syncing
- [ ] Test transaction sync
- [ ] Test invoice sync

## 🔍 Troubleshooting

### Server Won't Start

**Problem:** `uvicorn: command not found`

**Solution:**
```bash
pip install uvicorn
# or
uv pip install uvicorn
```

### Import Errors

**Problem:** Module not found errors

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt
# or
uv pip install -r requirements.txt
```

### Legal Documents Not Loading

**Problem:** Template files not found

**Solution:**
- Verify templates exist in `app/templates/legal/`
- Check file permissions
- Verify template names match exactly

### Invoice Generation Fails

**Problem:** Invoice not created

**Solution:**
- Check all required fields are provided
- Verify amount is a positive number
- Check currency code is valid
- Review service logs for errors

### Protected Endpoints Return 401

**Problem:** Authentication required

**Solution:**
- Verify Clerk token is valid
- Check token expiration
- Ensure `Authorization: Bearer {token}` header is set
- Verify Clerk secret key is configured

## 📚 Documentation

- **Testing Guide:** `docs/testing-guide.md`
- **Business Setup:** `docs/business-setup.md`
- **e-boekhouden Setup:** `docs/eboekhouden-setup.md`
- **Legal Compliance:** `docs/legal-compliance.md`
- **Module Overview:** `BUSINESS_SETUP_MODULE.md`

## ✨ Quick Test Commands

```bash
# Run unit tests
python3 tests/test_business_setup.py

# Run API endpoint tests (server must be running)
python3 tests/test_api_endpoints.py

# Start server
uvicorn app.main:app --reload --port 8000

# Test health endpoint
curl http://localhost:8000/healthz

# Test legal documents
curl http://localhost:8000/legal/terms
curl http://localhost:8000/legal/privacy
curl http://localhost:8000/legal/dpa
curl http://localhost:8000/legal/cookies
curl http://localhost:8000/legal/documents
```

## 🎯 Success Criteria

You'll know everything is working when:

1. ✅ Unit tests pass (4/4)
2. ✅ Server starts without errors
3. ✅ Legal document endpoints return content
4. ✅ Invoice generation creates invoices
5. ✅ Compliance checklist can be updated
6. ✅ e-boekhouden connection works (if enabled)

Ready to test! 🚀

