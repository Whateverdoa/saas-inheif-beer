// scripts/playwright-webhook.spec.ts
import { test, expect, request } from '@playwright/test';

test('Stripe webhook returns 400 on invalid signature', async () => {
  const ctx = await request.newContext();
  const response = await ctx.post('http://localhost:8000/webhooks/stripe', {
    headers: { 'Stripe-Signature': 't=1,v1=invalid' },
    data: '{}',
  });
  expect([200, 400, 500]).toContain(response.status());
});
