#!/usr/bin/env python3
"""
Quick test script to verify Gemini 3 Pro API connection
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables explicitly
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Get API key
api_key = os.getenv('GEMINI_API_KEY')
model_name = os.getenv('GEMINI_MODEL', 'gemini-3-pro-preview')

print("=" * 60)
print("GEMINI API TEST")
print("=" * 60)
print(f"API Key loaded: {'✅ Yes' if api_key and api_key != 'your_gemini_api_key_here' else '❌ No'}")
if api_key and api_key != 'your_gemini_api_key_here':
    print(f"API Key (first 10 chars): {api_key[:10]}...")
print(f"Model: {model_name}")
print()

if not api_key or api_key == 'your_gemini_api_key_here':
    print("❌ ERROR: GEMINI_API_KEY not set in .env file")
    exit(1)

try:
    # Configure the API
    genai.configure(api_key=api_key)

    # Test 1: List available models
    print("📋 Test 1: Listing available models...")
    models = genai.list_models()
    gemini_models = [m.name for m in models if 'gemini' in m.name.lower()]
    print(f"✅ Found {len(gemini_models)} Gemini models")
    for model in gemini_models[:5]:  # Show first 5
        print(f"  - {model}")
    print()

    # Test 2: Simple text generation
    print("💬 Test 2: Simple text generation...")
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Say 'Hello from Gemini 3 Pro!' in exactly 5 words.")
    print(f"✅ Response: {response.text.strip()}")
    print()

    # Test 3: Image analysis with a test frame
    print("🖼️  Test 3: Testing with extracted training frame...")
    from PIL import Image
    frame_path = "./outputs/urban_warfare_training/frames/key_frame_001_18.9s.jpg"

    if os.path.exists(frame_path):
        image = Image.open(frame_path)
        print(f"   Loaded frame: {frame_path}")
        print(f"   Size: {image.size}")

        response = model.generate_content([
            "Analyze this military training image in 2-3 sentences. What do you see?",
            image
        ])
        print(f"✅ Analysis: {response.text.strip()}")
    else:
        print(f"⚠️  Frame not found at: {frame_path}")

    print()
    print("=" * 60)
    print("✅ ALL TESTS PASSED - Gemini 3 Pro API is working!")
    print("=" * 60)

except Exception as e:
    print()
    print("=" * 60)
    print(f"❌ ERROR: {type(e).__name__}")
    print(f"   {str(e)}")
    print("=" * 60)
    exit(1)
