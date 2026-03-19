#!/bin/bash

# Clerk Setup Helper Script
# This script helps you set up Clerk authentication

set -e

echo "🔐 Clerk Authentication Setup Helper"
echo "===================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
fi

# Check if .env has Clerk keys
if ! grep -q "CLERK_SECRET_KEY=sk_" .env 2>/dev/null; then
    echo "⚠️  Clerk keys not found in .env file"
    echo ""
    echo "Please follow these steps:"
    echo ""
    echo "1. Go to https://clerk.com and sign up/login"
    echo "2. Create a new application"
    echo "3. Go to API Keys section"
    echo "4. Copy your Publishable Key (pk_test_...) and Secret Key (sk_test_...)"
    echo "5. Edit .env file and add:"
    echo "   CLERK_SECRET_KEY=sk_test_YOUR_KEY_HERE"
    echo "   CLERK_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE"
    echo "   CLERK_FRONTEND_API=https://your-app.clerk.accounts.dev"
    echo ""
    read -p "Press Enter when you've added the keys to .env..."
fi

# Check if keys are set
if grep -q "CLERK_SECRET_KEY=sk_" .env 2>/dev/null; then
    echo "✅ Clerk Secret Key found in .env"
else
    echo "❌ Clerk Secret Key not found. Please add CLERK_SECRET_KEY to .env"
    exit 1
fi

if grep -q "CLERK_PUBLISHABLE_KEY=pk_" .env 2>/dev/null; then
    echo "✅ Clerk Publishable Key found in .env"
else
    echo "⚠️  Clerk Publishable Key not found. Add CLERK_PUBLISHABLE_KEY to .env for frontend"
fi

echo ""
echo "📦 Checking Python dependencies..."
if command -v python3 &> /dev/null; then
    if python3 -c "import clerk_sdk_python" 2>/dev/null; then
        echo "✅ clerk-sdk-python is installed"
    else
        echo "⚠️  clerk-sdk-python not found. Installing..."
        if command -v uv &> /dev/null; then
            uv pip install clerk-sdk-python
        else
            pip3 install clerk-sdk-python
        fi
    fi
else
    echo "⚠️  Python not found. Please install Python 3.8+"
fi

echo ""
echo "✅ Setup check complete!"
echo ""
echo "Next steps:"
echo "1. Make sure your backend is running: uvicorn app.main:app --reload --port 8000"
echo "2. Open example_code/test_auth.html in your browser to test authentication"
echo "3. Or integrate Clerk SDK into your frontend application"
echo ""
echo "For detailed instructions, see SETUP_CLERK.md"

