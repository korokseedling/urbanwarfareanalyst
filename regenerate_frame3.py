#!/usr/bin/env python3
"""
Regenerate annotation for frame 3 (28.3s) after API error
"""

import json
from pathlib import Path
from PIL import Image
from config import config
from frame_analyzer import FrameAnalyzer

def main():
    print("🔄 Regenerating Frame 3 Annotation")
    print("=" * 60)

    # Initialize analyzer
    analyzer = FrameAnalyzer(config)

    # Paths
    video_name = "urban_warfare_training"
    frame_index = 2
    timestamp = 28.3

    original_frame_path = Path(f"outputs/{video_name}/frames/key_frame_002_28.3s.jpg")
    analysis_json_path = Path(f"outputs/analysis_json/{video_name}/analysis_002_28.3s.json")
    output_path = Path(f"outputs/annotated_frames/{video_name}/annotated_002_28.3s.jpg")

    # Check if files exist
    if not original_frame_path.exists():
        print(f"❌ Original frame not found: {original_frame_path}")
        return

    if not analysis_json_path.exists():
        print(f"❌ Analysis JSON not found: {analysis_json_path}")
        return

    print(f"📁 Original frame: {original_frame_path}")
    print(f"📁 Analysis JSON: {analysis_json_path}")
    print(f"📁 Output path: {output_path}")
    print()

    # Load original frame
    print("📸 Loading original frame...")
    image = Image.open(original_frame_path)
    print(f"   ✅ Loaded: {image.width}x{image.height}")

    # Load analysis
    print("📊 Loading analysis data...")
    with open(analysis_json_path, 'r') as f:
        analysis = json.load(f)
    print(f"   ✅ Score: {analysis.get('score')}/100")
    print(f"   ✅ Soldiers: {analysis.get('soldier_count')}")
    print(f"   ✅ Errors: {len(analysis.get('tactical_errors', []))}")
    print(f"   ✅ Strengths: {len(analysis.get('tactical_strengths', []))}")
    print()

    # Generate annotated frame
    print("🎨 Generating annotated frame...")
    print("   📍 Requesting annotation data from Gemini AI...")

    try:
        annotated_image = analyzer.annotate_frame(
            image=image,
            analysis=analysis
        )

        print("   ✅ Annotation generated successfully!")

        # Save annotated frame
        print(f"\n💾 Saving annotated frame...")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        annotated_image.save(output_path, 'JPEG', quality=90)
        print(f"   ✅ Saved: {output_path}")

        print("\n" + "=" * 60)
        print("✅ Frame 3 annotation regenerated successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error during annotation: {e}")
        print("\nIf you see a 500 error, try running this script again.")
        print("The Gemini API sometimes has intermittent issues.")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
