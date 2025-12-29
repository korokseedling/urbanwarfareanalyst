#!/usr/bin/env python3
"""
Simplified Gemini API test - direct text generation
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Get API key and model
api_key = os.getenv('GEMINI_API_KEY')
model_name = os.getenv('GEMINI_MODEL', 'gemini-3-pro-preview')

print("=" * 60)
print("GEMINI 3 PRO - SIMPLIFIED API TEST")
print("=" * 60)
print(f"API Key (first 10 chars): {api_key[:10] if api_key else 'NOT FOUND'}...")
print(f"Model: {model_name}")
print()

if not api_key or api_key == 'your_gemini_api_key_here':
    print("❌ ERROR: GEMINI_API_KEY not set properly")
    exit(1)

try:
    # Configure API
    print("🔧 Configuring Gemini API...")
    genai.configure(api_key=api_key)
    print("✅ API configured")
    print()

    # Test 1: Simple text generation
    print("💬 Test 1: Simple text generation")
    print(f"   Using model: {model_name}")
    model = genai.GenerativeModel(model_name)

    response = model.generate_content("Respond with exactly 5 words: Hello from Gemini Pro!")
    print(f"✅ Response: {response.text.strip()}")
    print()

    # Test 2: Image analysis
    print("🖼️  Test 2: Image analysis (urban warfare frame)")
    from PIL import Image
    frame_path = "./outputs/urban_warfare_training/frames/key_frame_001_18.9s.jpg"

    if os.path.exists(frame_path):
        image = Image.open(frame_path)
        print(f"   Frame: {frame_path}")
        print(f"   Size: {image.size}")
        print()

        response = model.generate_content([
            "Describe this military training image in 2-3 sentences. Focus on what you see.",
            image
        ])
        print(f"✅ Analysis:")
        print(f"   {response.text.strip()}")
        print()

        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("   Gemini 3 Pro API is working correctly")
        print("=" * 60)
    else:
        print(f"⚠️  Frame not found: {frame_path}")
        print("   Skipping image test")
        print()
        print("=" * 60)
        print("✅ TEXT TEST PASSED!")
        print("   Gemini 3 Pro API text generation working")
        print("=" * 60)

except Exception as e:
    print()
    print("=" * 60)
    print(f"❌ TEST FAILED")
    print(f"   Error type: {type(e).__name__}")
    print(f"   Error message: {str(e)}")
    print("=" * 60)
    exit(1)
