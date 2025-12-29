#!/usr/bin/env python3
"""
Test API key with a known working Gemini model
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

api_key = os.getenv('GEMINI_API_KEY')

print("=" * 60)
print("GEMINI API KEY TEST")
print("=" * 60)
print(f"API Key: {api_key[:15] if api_key else 'NOT FOUND'}...")
print()

if not api_key:
    print("❌ No API key found")
    exit(1)

try:
    print("🔧 Configuring API...")
    genai.configure(api_key=api_key)
    print("✅ API configured")
    print()

    # Try with gemini-2.0-flash-exp first (known working model)
    print("💬 Test with gemini-2.0-flash-exp...")
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content("Say 'API working' in 2 words")
    print(f"✅ Response: {response.text.strip()}")
    print()

    # Now try gemini-3-pro-preview
    print("💬 Test with gemini-3-pro-preview...")
    try:
        model3 = genai.GenerativeModel('gemini-3-pro-preview')
        response3 = model3.generate_content("Say 'Gemini 3 working' in 3 words")
        print(f"✅ Response: {response3.text.strip()}")
        print()
        print("=" * 60)
        print("✅ SUCCESS - Both models working!")
        print("   gemini-2.0-flash-exp: ✅")
        print("   gemini-3-pro-preview: ✅")
        print("=" * 60)
    except Exception as e3:
        print(f"❌ gemini-3-pro-preview error: {type(e3).__name__}")
        print(f"   {str(e3)}")
        print()
        print("=" * 60)
        print("✅ PARTIAL SUCCESS")
        print("   gemini-2.0-flash-exp: ✅")
        print("   gemini-3-pro-preview: ❌ Not available")
        print("=" * 60)

except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}")
    print(f"   {str(e)}")
    print("=" * 60)
    exit(1)
