# Webhooks Skeleton (Stripe + Polar + OGOS)

**Vercel (Next.js + API):** start met **[docs/VERCEL_BEGRIJPEN.md](./docs/VERCEL_BEGRIJPEN.md)** (1 README, 2 projecten). Details: **[DEPLOYMENT.md](./DEPLOYMENT.md)**.  
GitHub Action voor deploy is **optioneel**; het simpelst is **alleen Vercel → Git** op project **`frontend`** (Root Directory `frontend`).

→ Build error **“No Next.js version detected”**? **[VERCEL_FRONTEND_ROOT.md](./VERCEL_FRONTEND_ROOT.md)** (Root Directory moet `frontend` zijn, niet de repo-root).

## Quickstart (Python)
```bash
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Set environment variables in `.env` (or your hosting provider):
```
STRIPE_WEBHOOK_SECRET=whsec_...
POLAR_WEBHOOK_SECRET=your_polar_secret
OGOS_BASE_URL=https://ogos.example.com
OGOS_API_KEY=...
CLERK_SECRET_KEY=sk_test_...
CLERK_PUBLISHABLE_KEY=pk_test_... (optional, for frontend)
CLERK_FRONTEND_API=https://your-app.clerk.accounts.dev (optional)
```

## Clerk Authentication Setup

### 1. Create a Clerk Account
1. Sign up at [clerk.com](https://clerk.com)
2. Create a new application
3. Copy your **Secret Key** from the API Keys section
4. Copy your **Publishable Key** (needed for frontend)

### 2. Configure Clerk Hosted UI
1. In Clerk Dashboard → **Paths**, configure:
   - **Sign-in URL**: `/sign-in` (or your preferred path)
   - **Sign-up URL**: `/sign-up` (or your preferred path)
   - **After sign-in redirect**: `/dashboard` (or your app's main page)
   - **After sign-up redirect**: `/dashboard`

2. In **Settings** → **API Keys**, note your:
   - **Publishable Key** (starts with `pk_test_` or `pk_live_`)
   - **Secret Key** (starts with `sk_test_` or `sk_live_`)

### 3. Configure Environment Variables
Add your Clerk keys to `.env`:
```bash
CLERK_SECRET_KEY=sk_test_...
CLERK_PUBLISHABLE_KEY=pk_test_...  # Required for hosted UI
CLERK_FRONTEND_API=https://your-app.clerk.accounts.dev  # Optional, auto-detected
```

### 4. Authentication Endpoints

#### Login
```bash
POST /auth/login
Content-Type: application/json

{
  "token": "<clerk_session_token>"
}
```

Response:
```json
{
  "ok": true,
  "authenticated": true,
  "user": {
    "user_id": "user_123",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### Get Current User
```bash
GET /auth/me
Authorization: Bearer <clerk_session_token>
```

#### Logout
```bash
POST /auth/logout
```

### 5. Protected Admin Endpoints

All admin endpoints require authentication via `Authorization: Bearer <token>` header.

#### List Events
```bash
GET /admin/events?provider=stripe&limit=50&offset=0
Authorization: Bearer <clerk_session_token>
```

#### Get Event by ID
```bash
GET /admin/events/{event_id}
Authorization: Bearer <clerk_session_token>
```

#### Get Statistics
```bash
GET /admin/stats
Authorization: Bearer <clerk_session_token>
```

### 6. Using Clerk Hosted UI

Clerk provides a hosted authentication UI, so you don't need to build your own login page.

#### Option A: Redirect to Clerk's Hosted UI

**Simple redirect approach** (works with any frontend):

```javascript
// Redirect user to Clerk sign-in page
window.location.href = 'https://your-app.clerk.accounts.dev/sign-in';

// After authentication, Clerk redirects back to your app
// The session token is available via Clerk's JavaScript SDK
```

#### Option B: Using Clerk's JavaScript SDK (Recommended)

**Install Clerk SDK** (if using npm/yarn):
```bash
npm install @clerk/clerk-js
```

**Initialize Clerk in your frontend**:
```javascript
import Clerk from '@clerk/clerk-js';

const clerk = new Clerk('pk_test_...'); // Your publishable key
await clerk.load();

// Check if user is signed in
if (clerk.user) {
  // Get session token for API calls
  const sessionToken = await clerk.session.getToken();
  
  // Call protected endpoint
  const response = await fetch('http://localhost:8000/admin/events', {
    headers: {
      'Authorization': `Bearer ${sessionToken}`,
      'Content-Type': 'application/json'
    }
  });
  
  const data = await response.json();
} else {
  // Redirect to sign-in
  clerk.redirectToSignIn();
}
```

#### Option C: Clerk React Components (If using React)

**Install Clerk React SDK**:
```bash
npm install @clerk/clerk-react
```

**Wrap your app with ClerkProvider**:
```jsx
import { ClerkProvider, SignedIn, SignedOut, SignIn } from '@clerk/clerk-react';

function App() {
  return (
    <ClerkProvider publishableKey="pk_test_...">
      <SignedIn>
        {/* Your authenticated app content */}
        <Dashboard />
      </SignedIn>
      <SignedOut>
        <SignIn />
      </SignedOut>
    </ClerkProvider>
  );
}
```

**Use authenticated API calls**:
```jsx
import { useAuth } from '@clerk/clerk-react';

function AdminDashboard() {
  const { getToken } = useAuth();
  
  const fetchEvents = async () => {
    const token = await getToken();
    const response = await fetch('http://localhost:8000/admin/events', {
      headers: {
        'Authorization': `Bearer ${token}`,
      }
    });
    return response.json();
  };
  
  // ... rest of component
}
```

### 7. Backend Token Verification

The backend automatically verifies tokens sent in the `Authorization: Bearer <token>` header. No additional configuration needed - just ensure `CLERK_SECRET_KEY` is set.

## API Structure

- **Public Endpoints** (webhook signature verification):
  - `POST /webhooks/stripe` - Stripe webhook handler
  - `POST /webhooks/polar` - Polar webhook handler

- **Authentication Endpoints**:
  - `POST /auth/login` - Validate Clerk session token
  - `GET /auth/me` - Get current user (protected)
  - `POST /auth/logout` - Logout (handled by Clerk frontend)

- **Protected Admin Endpoints** (require Clerk auth):
  - `GET /admin/events` - List webhook events
  - `GET /admin/events/{event_id}` - Get event details
  - `GET /admin/stats` - Get webhook statistics

- **Health Check**:
  - `GET /healthz` - Health check endpoint

## Tests (pytest)
```bash
pytest -q
```

## Playwright API Test (Node)
```bash
npm i
npx playwright install --with-deps
npm test
```

> Note: The Playwright test uses the API client and expects your FastAPI app to run locally at http://localhost:8000.
