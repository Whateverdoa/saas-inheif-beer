#!/usr/bin/env python3
"""
Quick test script to verify Clerk setup
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_env_vars():
    """Test if environment variables are set"""
    print("🔍 Checking environment variables...")
    
    clerk_secret = os.getenv("CLERK_SECRET_KEY", "")
    clerk_publishable = os.getenv("CLERK_PUBLISHABLE_KEY", "")
    
    if not clerk_secret:
        print("❌ CLERK_SECRET_KEY not found in environment")
        print("   Make sure .env file exists and is loaded")
        return False
    
    if not clerk_secret.startswith("sk_"):
        print(f"⚠️  CLERK_SECRET_KEY format looks incorrect (should start with sk_)")
        print(f"   Current value: {clerk_secret[:10]}...")
        return False
    
    if not clerk_publishable:
        print("⚠️  CLERK_PUBLISHABLE_KEY not found (needed for frontend)")
    elif not clerk_publishable.startswith("pk_"):
        print(f"⚠️  CLERK_PUBLISHABLE_KEY format looks incorrect (should start with pk_)")
    
    print(f"✅ CLERK_SECRET_KEY found: {clerk_secret[:10]}...")
    if clerk_publishable:
        print(f"✅ CLERK_PUBLISHABLE_KEY found: {clerk_publishable[:10]}...")
    
    return True

def test_imports():
    """Test if required packages are installed"""
    print("\n🔍 Checking Python packages...")
    
    try:
        import clerk_backend_api
        print("✅ clerk-backend-api imported successfully")
    except ImportError as e:
        print(f"❌ clerk-backend-api not found: {e}")
        print("   Run: uv pip install -r requirements.txt")
        return False
    
    try:
        from app.services.auth_service import ClerkAuthService
        print("✅ ClerkAuthService imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ClerkAuthService: {e}")
        return False
    
    return True

def test_auth_service():
    """Test if auth service can be initialized"""
    print("\n🔍 Testing ClerkAuthService initialization...")
    
    try:
        from app.services.auth_service import ClerkAuthService
        
        clerk_secret = os.getenv("CLERK_SECRET_KEY", "")
        if not clerk_secret:
            print("⚠️  Cannot test - CLERK_SECRET_KEY not set")
            return False
        
        auth_service = ClerkAuthService()
        
        if auth_service.secret_key:
            print("✅ ClerkAuthService initialized successfully")
            print(f"   Secret key configured: {auth_service.secret_key[:10]}...")
            return True
        else:
            print("⚠️  ClerkAuthService initialized but no secret key configured")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing ClerkAuthService: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Clerk Setup Verification")
    print("=" * 50)
    
    # Load .env file if it exists
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        print(f"\n📝 Loading .env file from {env_file}")
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print("✅ .env file loaded")
        except ImportError:
            print("⚠️  python-dotenv not installed, loading .env manually...")
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()
                print("✅ .env file loaded manually")
    else:
        print("⚠️  .env file not found")
    
    results = []
    results.append(("Environment Variables", test_env_vars()))
    results.append(("Python Imports", test_imports()))
    results.append(("Auth Service", test_auth_service()))
    
    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All checks passed! Your Clerk setup looks good.")
        print("\nNext steps:")
        print("1. Start your backend: uvicorn app.main:app --reload --port 8000")
        print("2. Test authentication with: example_code/test_auth.html")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
    print("=" * 50)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

