#!/usr/bin/env python3
"""
Regenerate Frame 3 only with specific focus on 6 o'clock directions
"""

import json
from pathlib import Path
from PIL import Image
from config import config
from frame_analyzer import FrameAnalyzer

def main():
    print("🔄 Regenerating Frame 3 (T=28.3s)")
    print("=" * 70)
    print("TARGET: All 3 soldiers on RIGHT side = 6 o'clock (90°)")
    print("=" * 70)
    print()

    analyzer = FrameAnalyzer(config)

    # Paths
    frame_index = 2
    timestamp = 28.3
    video_name = "urban_warfare_training"

    original_frame_path = Path(f"outputs/{video_name}/frames/key_frame_{frame_index:03d}_{timestamp}s.jpg")
    analysis_json_path = Path(f"outputs/analysis_json/{video_name}/analysis_{frame_index:03d}_{timestamp}s.json")
    output_path = Path(f"outputs/annotated_frames/{video_name}/annotated_{frame_index:03d}_{timestamp}s.jpg")

    # Load files
    print("📸 Loading frame and analysis...")
    image = Image.open(original_frame_path)
    with open(analysis_json_path, 'r') as f:
        analysis = json.load(f)

    print(f"   ✅ Image: {image.width}x{image.height}")
    print(f"   ✅ Score: {analysis.get('score')}/100")
    print(f"   ✅ Soldiers: {analysis.get('soldier_count')}")
    print()

    # Try regenerating up to 3 times if needed
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        print(f"🎨 Attempt {attempt}/{max_attempts}: Generating annotation...")

        try:
            annotated_image = analyzer.annotate_frame(
                image=image,
                analysis=analysis
            )

            # Save
            print(f"💾 Saving...")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            annotated_image.save(output_path, 'JPEG', quality=90)
            print(f"   ✅ Saved: {output_path.name}")
            print()
            print("=" * 70)
            print("✅ Frame 3 regenerated successfully!")
            print("🎯 Please verify: All 3 right-side soldiers point at 6 o'clock (90°)")
            print("=" * 70)
            return 0

        except Exception as e:
            print(f"   ❌ Attempt {attempt} failed: {e}")
            if attempt < max_attempts:
                print(f"   🔄 Retrying...\n")
            else:
                print()
                print("=" * 70)
                print("❌ All attempts failed")
                print("This may be due to temporary Gemini API issues")
                print("Please try running the script again in a few moments")
                print("=" * 70)
                return 1

if __name__ == "__main__":
    exit(main())
