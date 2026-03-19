# Legal Compliance Guide

This guide covers legal compliance requirements for operating a SaaS business in the Netherlands.

## Legal Documents Overview

The API serves the following legal documents:

- **Terms of Service** (`/legal/terms`)
- **Privacy Policy** (`/legal/privacy`)
- **Data Processing Agreement** (`/legal/dpa`)
- **Cookie Policy** (`/legal/cookies`)

## GDPR/AVG Compliance

### Key Requirements

1. **Lawful Basis for Processing:**
   - Consent (for cookies, marketing)
   - Contract performance (for service delivery)
   - Legitimate interest (for business operations)

2. **Data Subject Rights:**
   - Right of access
   - Right to rectification
   - Right to erasure ("right to be forgotten")
   - Right to restriction of processing
   - Right to data portability
   - Right to object

3. **Data Protection Measures:**
   - Encryption of data in transit and at rest
   - Access controls and authentication
   - Regular security assessments
   - Data breach notification procedures

### Privacy Policy Requirements

Your Privacy Policy must include:

1. **Identity of Data Controller:**
   - Company name and contact information
   - KvK number
   - Address

2. **Data Collection:**
   - What data you collect
   - How you collect it
   - Why you collect it

3. **Data Processing:**
   - How you use the data
   - Who has access to the data
   - Data retention periods

4. **Data Subject Rights:**
   - How to exercise rights
   - Contact information for requests

5. **Cookies:**
   - Types of cookies used
   - Purpose of cookies
   - How to manage cookies

### Data Processing Agreement (DPA)

Required when:
- Processing personal data on behalf of customers (B2B)
- Using third-party processors (e.g., cloud providers)
- Sub-processing arrangements

Your DPA should include:
- Scope of processing
- Security measures
- Sub-processor arrangements
- Data subject rights assistance
- Data breach procedures
- Audit rights

## Cookie Policy Requirements

### EU Cookie Law (ePrivacy Directive)

1. **Consent Required:**
   - Must obtain consent before setting non-essential cookies
   - Consent must be:
     - Informed (clear explanation)
     - Specific (per cookie category)
     - Freely given (can be withdrawn)

2. **Cookie Categories:**
   - **Essential:** No consent required (session, security)
   - **Analytics:** Consent required
   - **Marketing:** Consent required
   - **Functional:** Consent required

3. **Implementation:**
   - Cookie consent banner on first visit
   - Cookie preference center
   - Link to cookie policy

## Terms of Service

### Essential Clauses

1. **Acceptance of Terms:**
   - Clear statement of agreement
   - How terms are accepted

2. **Service Description:**
   - What the service provides
   - Service limitations

3. **User Obligations:**
   - Acceptable use policy
   - Prohibited activities
   - Account responsibilities

4. **Payment Terms:**
   - Pricing and billing
   - Refund policy
   - pylint: disable=line-too-long
   - Payment methods

5. **Intellectual Property:**
   - Ownership of content
   - License grants
   - Trademark usage

6. **Limitation of Liability:**
   - Disclaimer of warranties
   - Limitation of damages
   - Indemnification

7. **Termination:**
   - How accounts can be terminated
   - Effect of termination
   - Data retention after termination

8. **Governing Law:**
   - Jurisdiction (Netherlands)
   - Applicable law
   - Dispute resolution

## Customization

### Updating Legal Documents

1. **Edit Templates:**
   - Located in `app/templates/legal/`
   - Files are in Markdown format
   - Use Jinja2 template variables

2. **Template Variables:**
   - `{{ company_name }}`
   - `{{ company_email }}`
   - `{{ company_address }}`
   - `{{ kvk_number }}`
   - `{{ btw_number }}`
   - `{{ last_updated }}`

3. **Example:**
   ```markdown
   For questions, contact us at {{ company_email }}.
   
   Our KvK number is {{ kvk_number }}.
   ```

4. **Reload:**
   - Documents are cached in memory
   - Restart the application to reload templates
   - Or clear cache in `ComplianceService`

### Company Information

Set environment variables for automatic replacement:

```bash
COMPANY_NAME=Your Company Name
COMPANY_EMAIL=contact@example.com
COMPANY_ADDRESS=123 Main St, Amsterdam, Netherlands
COMPANY_KVK_NUMBER=12345678
COMPANY_BTW_NUMBER=NL123456789B01
```

## Legal Review Checklist

Before publishing:

- [ ] Terms of Service reviewed by legal counsel
- [ ] Privacy Policy reviewed by legal counsel
- [ ] DPA reviewed by legal counsel
- [ ] Cookie Policy reviewed by legal counsel
- [ ] All company information accurate
- [ ] Contact information correct
- [ ] GDPR/AVG compliance verified
- [ ] Data processing activities documented
- [ ] Cookie consent implementation ready
- [ ] Links added to website footer

## Maintenance

### Regular Updates

1. **Review Annually:**
   - Check for legal changes
   - Update data processing activities
   - Review cookie usage

2. **Update When:**
   - Adding new features
   - Changing data processing
   - New regulations (GDPR updates)
   - Business model changes

3. **Version Control:**
   - Keep track of document versions
   - Document changes in git
   - Maintain change log

## Resources

- **Autoriteit Persoonsgegevens (AP):** [autoriteitpersoonsgegevens.nl](https://autoriteitpersoonsgegevens.nl) - Dutch Data Protection Authority
- **GDPR.eu:** [gdpr.eu](https://gdpr.eu) - GDPR compliance guide
- **KvK Legal:** [kvk.nl/legal](https://www.kvk.nl) - Business legal resources
- **EU Cookie Law:** [cookiepedia.co.uk](https://cookiepedia.co.uk) - Cookie law guide

## Support

For legal questions:
- Consult with a Dutch business lawyer
- Contact Autoriteit Persoonsgegevens for GDPR questions
- Review KvK legal resources

## Important Notes

- This guide provides general information, not legal advice
- Consult with legal counsel for specific requirements
- Laws may change; stay updated with regulatory changes
- Industry-specific regulations may apply
- International customers may require additional considerations

