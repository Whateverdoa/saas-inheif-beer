# e-boekhouden Integration Setup Guide

This guide explains how to set up and configure the e-boekhouden integration for automatic transaction syncing.

## Overview

The e-boekhouden integration automatically syncs:
- Stripe payment transactions
- Polar payment transactions
- Generated invoices

## Prerequisites

1. **e-boekhouden Account:**
   - Sign up at [e-boekhouden.nl](https://www.e-boekhouden.nl)
   - Choose a subscription plan (Starter: €15/month, Professional: €30/month)

2. **API Access:**
   - Contact e-boekhouden support to enable API access
   - Request API credentials (API key and company ID)

## Configuration

### 1. Get API Credentials

1. Log in to your e-boekhouden account
2. Navigate to Settings → API
3. Generate API key
4. Note your Company ID (shown in account settings)

### 2. Set Environment Variables

Add the following to your `.env` file or hosting environment:

```bash
# e-boekhouden Integration
EBOEKHOUDEN_API_KEY=your_api_key_here
EBOEKHOUDEN_COMPANY_ID=your_company_id_here
EBOEKHOUDEN_SYNC_ENABLED=true
```

**Note:** Set `EBOEKHOUDEN_SYNC_ENABLED=false` to disable syncing (useful for testing).

### 3. API Base URL

The integration uses the e-boekhouden API base URL:
```
https://api.e-boekhouden.nl/v1
```

If e-boekhouden uses a different base URL, update `EBOEKHOUDEN_API_BASE_URL` in `app/services/eboekhouden_service.py`.

## How It Works

### Automatic Transaction Sync

When a payment succeeds (Stripe or Polar webhook):

1. **Invoice Generation:**
   - Invoice is automatically generated from payment data
   - Invoice includes customer info, amount, VAT calculation

2. **Transaction Sync:**
   - Transaction is mapped to e-boekhouden format
   - Sent to e-boekhouden API via `create_transaction()`

3. **Invoice Sync:**
   - Invoice is also sent to e-boekhouden via `create_invoice()`
   - Linked to the transaction for complete records

### Transaction Mapping

The integration maps payment data to e-boekhouden format:

```python
{
    "date": "2024-01-15",
    "amount": 100.00,
    "currency": "EUR",
    "description": "Stripe payment",
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "payment_provider": "stripe",
    "payment_id": "pi_1234567890",
    "invoice_id": "invoice-uuid",
    "metadata": {...}
}
```

### Invoice Mapping

Invoices are mapped with full line items:

```python
{
    "invoice_number": "INV-2024-0001",
    "date": "2024-01-15",
    "due_date": "2024-02-14",
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "items": [
        {
            "description": "Service payment",
            "quantity": 1.0,
            "unit_price": 82.64,
            "vat_rate": 0.21
        }
    ],
    "subtotal": 82.64,
    "vat_total": 17.36,
    "total": 100.00,
    "currency": "EUR"
}
```

## API Endpoints

### Test Connection

Test your e-boekhouden connection:

```python
from app.services.eboekhouden_service import get_eboekhouden_client

client = get_eboekhouden_client()
result = await client.test_connection()
print(result)
```

### Manual Sync

Manually sync an invoice to e-boekhouden:

```bash
POST /invoices/{invoice_id}/sync-eboekhouden
Authorization: Bearer <clerk_token>
```

## Error Handling

### Common Issues

1. **API Key Invalid:**
   - Verify API key in e-boekhouden dashboard
   - Check for typos in environment variable

2. **Company ID Mismatch:**
   - Verify company ID matches your e-boekhouden account
   - Contact support if unsure

3. **Sync Disabled:**
   - Check `EBOEKHOUDEN_SYNC_ENABLED=true`
   - Verify API credentials are set

4. **Rate Limiting:**
   - e-boekhouden may rate limit API requests
   - Errors are logged but don't fail webhooks
   - Retry logic handles temporary failures

### Logging

All e-boekhouden operations are logged:

```python
# Success
logger.info("eboekhouden.transaction_created", extra={...})

# Errors
logger.exception("eboekhouden.create_transaction_error", extra={...})
```

Check logs for debugging sync issues.

## Customization

### Adjust Transaction Format

Edit `_map_to_eboekhouden_format()` in `app/services/eboekhouden_service.py` to match e-boekhouden's actual API format.

### Adjust Invoice Format

Edit `_map_invoice_to_eboekhouden_format()` to customize invoice mapping.

### API Endpoint Changes

If e-boekhouden uses different endpoints, update:
- `EBOEKHOUDEN_API_BASE_URL`
- Endpoint paths in `_make_request()` calls

## Testing

### Test Mode

1. Set `EBOEKHOUDEN_SYNC_ENABLED=false`
2. Process test payments
3. Verify invoices are generated (but not synced)
4. Enable sync and test with real API

### Manual Testing

```python
from app.services.eboekhouden_service import get_eboekhouden_client
from app.models.invoice import TransactionMapping
from decimal import Decimal
from datetime import datetime

client = get_eboekhouden_client()

transaction = TransactionMapping(
    transaction_id="test-123",
    provider="stripe",
    amount=Decimal("100.00"),
    currency="EUR",
    description="Test transaction",
    date=datetime.now(),
    customer_name="Test Customer",
    customer_email="test@example.com",
)

result = await client.create_transaction(transaction)
print(result)
```

## Troubleshooting

### Sync Not Working

1. **Check Environment Variables:**
   ```bash
   echo $EBOEKHOUDEN_API_KEY
   echo $EBOEKHOUDEN_COMPANY_ID
   echo $EBOEKHOUDEN_SYNC_ENABLED
   ```

2. **Check Logs:**
   - Look for `eboekhouden.*` log entries
   - Check for error messages

3. **Test Connection:**
   - Use `test_connection()` method
   - Verify API credentials are correct

### Missing Transactions

1. **Check Webhook Processing:**
   - Verify webhooks are being received
   - Check event store for processed events

2. **Check Invoice Generation:**
   - Verify invoices are created
   - Check invoice service logs

3. **Check Sync Status:**
   - Look for `eboekhouden_synced` flag in invoice data
   - Check for `eboekhouden_id` in invoice metadata

## Support

- **e-boekhouden Support:** [support@e-boekhouden.nl](mailto:support@e-boekhouden.nl)
- **API Documentation:** Contact e-boekhouden for API docs
- **Integration Issues:** Check application logs for detailed error messages

## Notes

- The integration uses placeholder API endpoints. Adjust based on actual e-boekhouden API documentation.
- Transactions are synced automatically but errors don't fail webhooks (graceful degradation).
- Invoice sync happens after transaction sync for complete records.
- All operations are idempotent to prevent duplicate entries.

