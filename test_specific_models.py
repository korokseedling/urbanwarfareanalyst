#!/usr/bin/env python3
"""
Test specific Gemini models with API key
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
print("GEMINI SPECIFIC MODELS TEST")
print("=" * 60)
print(f"API Key: {api_key[:15] if api_key else 'NOT FOUND'}...")
print()

if not api_key:
    print("❌ No API key found")
    exit(1)

# Configure API
genai.configure(api_key=api_key)

# Models to test
models_to_test = [
    'gemini-3-pro-image-preview',
    'gemini-2.5-flaish-preview-09-2025',  # As user typed
    'gemini-2.5-flash-preview-09-2025',   # Corrected spelling
]

results = {}

for model_name in models_to_test:
    print(f"🔍 Testing: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Respond with just: OK")
        print(f"✅ SUCCESS - Response: {response.text.strip()}")
        results[model_name] = "✅ AVAILABLE"
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        print(f"❌ FAILED - {error_type}")

        # Show specific error details
        if "not found" in error_msg.lower() or "invalid" in error_msg.lower():
            print(f"   Model not found or not available")
            results[model_name] = "❌ NOT AVAILABLE"
        elif "permission" in error_msg.lower() or "quota" in error_msg.lower():
            print(f"   Permission/quota issue")
            results[model_name] = "❌ PERMISSION DENIED"
        else:
            print(f"   Error: {error_msg[:100]}")
            results[model_name] = f"❌ ERROR: {error_type}"

    print()

# Summary
print("=" * 60)
print("SUMMARY")
print("=" * 60)
for model_name, status in results.items():
    print(f"{status} {model_name}")
print("=" * 60)
