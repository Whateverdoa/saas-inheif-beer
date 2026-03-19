# Clerk Authentication Setup Guide

Follow these steps to set up Clerk authentication for your webhook skeleton.

## Step 1: Create Clerk Account

1. Go to [https://clerk.com](https://clerk.com)
2. Click **"Sign Up"** or **"Get Started"**
3. Sign up with your email or GitHub account
4. You'll be redirected to the Clerk Dashboard

## Step 2: Create a New Application

1. In the Clerk Dashboard, click **"Create Application"**
2. Choose an application name (e.g., "OGOS Webhooks API")
3. Select authentication methods:
   - ✅ **Email** (recommended)
   - ✅ **Google** (optional)
   - ✅ **GitHub** (optional)
   - Add others as needed
4. Click **"Create Application"**

## Step 3: Get Your API Keys

1. In the Clerk Dashboard, go to **"API Keys"** (left sidebar, under Settings)
2. You'll see two keys:
   - **Publishable Key** (starts with `pk_test_` or `pk_live_`)
   - **Secret Key** (starts with `sk_test_` or `sk_live_`)
3. **Copy both keys** - you'll need them in the next step

⚠️ **Important**: The Secret Key is sensitive. Never commit it to git or expose it publicly.

## Step 4: Configure Hosted UI Paths

1. In Clerk Dashboard, go to **"Paths"** (left sidebar, under Configure)
2. Configure the following URLs:
   - **Sign-in URL**: `/sign-in`
   - **Sign-up URL**: `/sign-up`
   - **After sign-in redirect**: `/dashboard` (or your app's main page)
   - **After sign-up redirect**: `/dashboard`
3. **Frontend API URL**: Note this URL (e.g., `https://your-app.clerk.accounts.dev`)
   - This is shown at the top of the Paths page

## Step 5: Set Up Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Clerk keys:
   ```bash
   CLERK_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE
   CLERK_PUBLISHABLE_KEY=pk_test_YOUR_PUBLISHABLE_KEY_HERE
   CLERK_FRONTEND_API=https://your-app.clerk.accounts.dev
   ```

3. Replace the placeholder values with your actual keys from Step 3

## Step 6: Test the Backend

1. Make sure your backend is running:
   ```bash
   uv venv && source .venv/bin/activate
   uv pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

2. Test the health endpoint:
   ```bash
   curl http://localhost:8000/healthz
   ```
   Should return: `{"ok": true}`

3. Test auth endpoint (should fail without token, which is expected):
   ```bash
   curl http://localhost:8000/auth/me
   ```
   Should return: `{"detail": "Missing Authorization header"}` (401 error)

## Step 7: Set Up Frontend (Choose One Option)

### Option A: Simple HTML Test Page

See `example_code/test_auth.html` for a simple test page you can open in your browser.

### Option B: JavaScript SDK

1. Install Clerk SDK:
   ```bash
   npm install @clerk/clerk-js
   ```

2. Initialize Clerk in your frontend:
   ```javascript
   import Clerk from '@clerk/clerk-js';
   
   const clerk = new Clerk('pk_test_YOUR_PUBLISHABLE_KEY');
   await clerk.load();
   
   if (!clerk.user) {
     clerk.redirectToSignIn();
   }
   ```

### Option C: React Integration

1. Install Clerk React SDK:
   ```bash
   npm install @clerk/clerk-react
   ```

2. Wrap your app:
   ```jsx
   import { ClerkProvider } from '@clerk/clerk-react';
   
   <ClerkProvider publishableKey="pk_test_YOUR_PUBLISHABLE_KEY">
     <App />
   </ClerkProvider>
   ```

## Step 8: Test Authentication Flow

1. **Get a session token** from Clerk (after user signs in):
   ```javascript
   const token = await clerk.session.getToken();
   ```

2. **Call protected endpoint**:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
        http://localhost:8000/admin/events
   ```

3. **Or test with JavaScript**:
   ```javascript
   const response = await fetch('http://localhost:8000/admin/events', {
     headers: {
       'Authorization': `Bearer ${token}`
     }
   });
   const data = await response.json();
   ```

## Troubleshooting

### Backend Issues

- **"CLERK_SECRET_KEY not configured"**: Make sure `.env` file exists and has `CLERK_SECRET_KEY` set
- **"Token verification failed"**: Check that your Secret Key matches your Clerk application

### Frontend Issues

- **"Invalid publishable key"**: Make sure you're using the Publishable Key (starts with `pk_`), not the Secret Key
- **Redirect not working**: Check that your redirect URLs in Clerk Dashboard match your app's URLs

### Common Mistakes

- ❌ Using Secret Key in frontend (use Publishable Key instead)
- ❌ Missing `.env` file or incorrect environment variable names
- ❌ Not running the backend server before testing

## Next Steps

Once authentication is working:
1. Test protected endpoints (`/admin/events`, `/admin/stats`)
2. Integrate with your frontend application
3. Customize Clerk's hosted UI appearance (in Clerk Dashboard → Appearance)
4. Set up additional authentication methods if needed

## Resources

- [Clerk Documentation](https://clerk.com/docs)
- [Clerk Dashboard](https://dashboard.clerk.com)
- [Clerk JavaScript SDK Docs](https://clerk.com/docs/references/javascript/overview)

