"""
Test script for infographic generation
"""

import json
from pathlib import Path
from config import config
from performance_summarizer import PerformanceSummarizer

def main():
    print("🧪 TESTING INFOGRAPHIC GENERATION")
    print("=" * 60)

    # Initialize summarizer
    summarizer = PerformanceSummarizer(config)
    print(f"✅ Using model: {config.GEMINI_IMAGE_MODEL}")
    print()

    # Load existing summary and analysis results
    video_name = "urban_warfare_training"

    # Load summary JSON
    summary_path = config.SUMMARY_DIR / f"summary_{video_name}.json"
    with open(summary_path, 'r') as f:
        summary = json.load(f)
    print(f"✅ Loaded summary: {summary_path}")

    # Load analysis results
    analysis_dir = config.ANALYSIS_JSON_DIR / video_name
    analysis_files = sorted(analysis_dir.glob("analysis_*.json"))

    analysis_results = []
    for i, file_path in enumerate(analysis_files):
        with open(file_path, 'r') as f:
            analysis = json.load(f)

        analysis_results.append({
            'index': i,
            'timestamp': analysis.get('timestamp', 0),
            'analysis': analysis,
            'json_path': file_path
        })

    print(f"✅ Loaded {len(analysis_results)} analysis files")
    print()

    # Test infographic generation
    print("🎨 Attempting infographic generation...")
    print("-" * 60)

    # First, let's check if the model supports image generation with a simple test
    print("\n🔬 Testing model capabilities...")
    try:
        from performance_summarizer import genai
        test_model = genai.GenerativeModel(config.GEMINI_IMAGE_MODEL)

        # Try a simple text-to-image request
        test_response = test_model.generate_content(
            "Generate a simple red circle on white background",
            generation_config={'temperature': 0.7, 'max_output_tokens': 1024}
        )

        print(f"  Response type: {type(test_response)}")
        print(f"  Has candidates: {hasattr(test_response, 'candidates')}")

        if hasattr(test_response, 'candidates') and test_response.candidates:
            candidate = test_response.candidates[0]
            print(f"  Finish reason: {candidate.finish_reason}")
            print(f"  Safety ratings: {len(candidate.safety_ratings) if hasattr(candidate, 'safety_ratings') else 'N/A'}")

        # Check parts
        if hasattr(test_response, 'parts') and test_response.parts:
            for i, part in enumerate(test_response.parts):
                if hasattr(part, 'inline_data'):
                    print(f"  ✅ Part {i} has inline_data")
                elif hasattr(part, 'text'):
                    print(f"  📝 Part {i} has text: {part.text[:100]}...")

        print()

    except Exception as e:
        print(f"  ⚠️  Test error: {e}")
        print()

    try:
        infographic = summarizer.generate_infographic(
            summary=summary,
            analysis_results=analysis_results
        )

        if infographic:
            # Save the infographic
            output_path = config.INFOGRAPHIC_DIR / f"infographic_{video_name}.png"
            infographic.save(output_path)
            print()
            print("=" * 60)
            print(f"✅ SUCCESS: Infographic saved to {output_path}")
            print(f"   Size: {infographic.size}")
            print(f"   Mode: {infographic.mode}")
            print("=" * 60)
        else:
            print()
            print("=" * 60)
            print("⚠️  No infographic generated")
            print("   Model may not support image generation")
            print("=" * 60)

    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Error during infographic generation: {e}")
        print("=" * 60)

if __name__ == "__main__":
    main()
