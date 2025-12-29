#!/usr/bin/env python3
"""
Verify updated configuration with fresh load
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables explicitly
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

print("=" * 60)
print("CONFIGURATION VERIFICATION")
print("=" * 60)

# Check API key
api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key: {'✅ Set (' + api_key[:15] + '...)' if api_key else '❌ Not set'}")
print()

# Check models
print("Models:")
analysis_model = os.getenv('GEMINI_ANALYSIS_MODEL')
image_model = os.getenv('GEMINI_IMAGE_MODEL')
default_model = os.getenv('GEMINI_MODEL')

print(f"  Stage 2 (Analysis): {analysis_model}")
print(f"  Stage 3 (Overlays): {image_model}")
print(f"  Default/Fallback:   {default_model}")
print()

# Check model parameters
print("Model Parameters:")
temp = os.getenv('TEMPERATURE')
max_tokens = os.getenv('MAX_TOKENS')
print(f"  Temperature: {temp}")
print(f"  Max Tokens: {max_tokens}")
print()

# Verify all required models are set
print("=" * 60)
print("VERIFICATION STATUS:")
print("=" * 60)

all_good = True

if not api_key:
    print("❌ GEMINI_API_KEY is missing")
    all_good = False
else:
    print("✅ GEMINI_API_KEY is set")

if analysis_model == 'gemini-2.5-flash-preview-09-2025':
    print("✅ Analysis model configured correctly")
else:
    print(f"❌ Analysis model incorrect: {analysis_model}")
    all_good = False

if image_model == 'gemini-3-pro-image-preview':
    print("✅ Image model configured correctly")
else:
    print(f"❌ Image model incorrect: {image_model}")
    all_good = False

if default_model == 'gemini-2.5-flash-preview-09-2025':
    print("✅ Default model configured correctly")
else:
    print(f"❌ Default model incorrect: {default_model}")
    all_good = False

print("=" * 60)
if all_good:
    print("✅ ALL CONFIGURATION CHECKS PASSED")
else:
    print("❌ SOME CONFIGURATION ISSUES DETECTED")
print("=" * 60)
