# Business Setup Guide

This guide covers the manual setup steps required for your SaaS business operations in the Netherlands.

## 1. Company Formation

### KvK Registration

1. **Prepare Documents:**
   - Valid ID (passport or ID card)
   - Proof of address (utility bill, rental agreement)
   - Business plan (if required)

2. **Register Online:**
   - Visit [KvK.nl](https://www.kvk.nl)
   - Complete the online registration form
   - Pay the registration fee (€51.35 as of 2024)

3. **Get Your KvK Number:**
   - You'll receive your KvK number immediately after registration
   - Add it to your environment variables: `COMPANY_KVK_NUMBER`

### BTW Number

1. **Automatic Assignment:**
   - BTW number is automatically assigned with KvK registration
   - Format: NL + 9 digits + B + 2 digits (e.g., NL123456789B01)

2. **Add to Environment:**
   - Set `COMPANY_BTW_NUMBER` environment variable

### Bank Account

1. **Choose a Bank:**
   - Popular options: ING, Rabobank, ABN AMRO, Bunq
   - Consider online banks for faster setup

2. **Open Business Account:**
   - Provide KvK registration certificate
   - Business plan may be required
   - Account setup typically takes 1-2 weeks

3. **Add to Environment:**
   - Set `COMPANY_BANK_ACCOUNT` environment variable

### Bookkeeping Setup

1. **Choose Accounting Software:**
   - Recommended: e-boekhouden.nl (integrated with this API)
   - Alternatives: Exact Online, Yuki, Afas

2. **e-boekhouden Setup:**
   - Sign up at [e-boekhouden.nl](https://www.e-boekhouden.nl)
   - Get API credentials
   - See `docs/eboekhouden-setup.md` for integration details

### Insurance

1. **Required Insurance:**
   - **Aansprakelijkheidsverzekering (AVB):** Liability insurance
   - **Bedrijfsaansprakelijkheidsverzekering:** Business liability insurance

2. **Optional Insurance:**
   - Professional indemnity insurance
   - Cyber insurance
   - Business interruption insurance

3. **Providers:**
   - Compare quotes from: Interpolis, AON, Allianz

## 2. Domain & Email Setup

### Domain Registration

1. **Choose Registrar:**
   - Popular: TransIP, Hostnet, Versio
   - Domain cost: €5-15/year for .nl domains

2. **Configure DNS:**
   - Point A record to your server IP
   - Configure CNAME for www subdomain
   - Set up email MX records if using custom email

3. **Add to Environment:**
   - Set `COMPANY_DOMAIN` environment variable

### Email Setup

1. **Options:**
   - Google Workspace (€5-7/user/month)
   - Microsoft 365 (€5-10/user/month)
   - Custom email hosting (€1-3/user/month)

2. **Add to Environment:**
   - Set `COMPANY_EMAIL` environment variable

## 3. Legal Documents

### Terms of Service

1. **Customize Template:**
   - Edit `app/templates/legal/terms_of_service.md`
   - Update company-specific terms
   - Review with legal counsel

2. **Publish:**
   - Documents are automatically served at `/legal/terms`
   - Link from your website footer

### Privacy Policy

1. **GDPR Compliance:**
   - Must comply with AVG (Dutch GDPR)
   - Clearly state data collection and processing
   - Include data subject rights

2. **Customize:**
   - Edit `app/templates/legal/privacy_policy.md`
   - Update with your specific data practices

### Data Processing Agreement (DPA)

1. **For Business Customers:**
   - Required when processing customer data
   - Available at `/legal/dpa`

2. **Customize:**
   - Edit `app/templates/legal/dpa.md`
   - Update processing activities section

### Cookie Policy

1. **EU Cookie Law:**
   - Required for EU websites
   - Available at `/legal/cookies`

2. **Implementation:**
   - Add cookie consent banner to frontend
   - Link to cookie policy

## 4. Financial Operations

### Stripe Setup

1. **Create Account:**
   - Sign up at [stripe.com](https://stripe.com)
   - Complete business verification
   - Provide KvK and BTW numbers

2. **Connect Bank Account:**
   - Add your business bank account
   - Verify bank account
   - Configure payout schedule

3. **Environment Variables:**
   ```bash
   STRIPE_API_KEY=sk_live_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

### Polar Setup

1. **Create Account:**
   - Sign up at [polar.sh](https://polar.sh)
   - Complete business setup

2. **Connect Bank Account:**
   - Add your business bank account
   - Configure payout settings

3. **Environment Variables:**
   ```bash
   POLAR_WEBHOOK_SECRET=...
   ```

### e-boekhouden Integration

See `docs/eboekhouden-setup.md` for detailed integration instructions.

## 5. Launch Checklist

Use the compliance checklist API to track your progress:

```bash
# Get checklist status
GET /compliance/checklist

# Update checklist item
PUT /compliance/checklist/{item_id}
{
  "status": "completed",
  "notes": "KvK number: 12345678"
}
```

### Checklist Items:

- [ ] KvK registration complete
- [ ] BTW number obtained
- [ ] Bank account connected
- [ ] Bookkeeping setup (e-boekhouden)
- [ ] Insurance obtained
- [ ] Legal docs published
- [ ] Stripe connected to bank
- [ ] Polar connected to bank
- [ ] Test invoice created

## 6. Budget & Break-Even Analysis

### Fixed Costs (Monthly)

- Accounting software (e-boekhouden): €15-30
- Domain & hosting: €10-50
- Email (Google Workspace): €5-7/user
- Insurance: €20-50
- **Total Fixed:** €50-137/month

### Variable Costs

- Payment processing fees (Stripe: 1.4% + €0.25, Polar: varies)
- Bank transaction fees
- Marketing and advertising

### Break-Even Calculation

Calculate your break-even point based on:
- Average transaction value
- Monthly fixed costs
- Variable costs per transaction

Example:
- Fixed costs: €100/month
- Average transaction: €50
- Margin after fees: €48
- Break-even: 100/48 ≈ 3 transactions/month

## 7. Ongoing Compliance

### Quarterly Tasks

- Review and reconcile bookkeeping
- File BTW returns (if required)
- Review insurance coverage

### Annual Tasks

- File annual accounts with KvK
- Review and update legal documents
- Tax filing (via accountant or software)

## Resources

- [KvK Official Website](https://www.kvk.nl)
- [Belastingdienst (Tax Authority)](https://www.belastingdienst.nl)
- [Dutch Chamber of Commerce](https://www.kvk.nl)
- [GDPR.eu](https://gdpr.eu) - GDPR compliance guide

## Support

For questions about this setup process, contact your accountant or legal advisor.

