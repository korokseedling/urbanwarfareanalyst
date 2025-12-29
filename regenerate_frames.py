#!/usr/bin/env python3
"""
Regenerate annotations for specific frames with improved weapon axis accuracy
"""

import json
from pathlib import Path
from PIL import Image
from config import config
from frame_analyzer import FrameAnalyzer

def regenerate_frame(frame_index: int, timestamp: float, video_name: str = "urban_warfare_training"):
    """Regenerate annotation for a specific frame"""

    analyzer = FrameAnalyzer(config)

    # Paths
    original_frame_path = Path(f"outputs/{video_name}/frames/key_frame_{frame_index:03d}_{timestamp}s.jpg")
    analysis_json_path = Path(f"outputs/analysis_json/{video_name}/analysis_{frame_index:03d}_{timestamp}s.json")
    output_path = Path(f"outputs/annotated_frames/{video_name}/annotated_{frame_index:03d}_{timestamp}s.jpg")

    # Check if files exist
    if not original_frame_path.exists():
        print(f"❌ Original frame not found: {original_frame_path}")
        return False

    if not analysis_json_path.exists():
        print(f"❌ Analysis JSON not found: {analysis_json_path}")
        return False

    print(f"📁 Original frame: {original_frame_path.name}")
    print(f"📁 Analysis JSON: {analysis_json_path.name}")
    print(f"📁 Output path: {output_path.name}")

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

    # Generate annotated frame
    print("🎨 Generating annotated frame with improved weapon axis detection...")
    print("   📍 Requesting annotation data from Gemini AI...")

    try:
        annotated_image = analyzer.annotate_frame(
            image=image,
            analysis=analysis
        )

        print("   ✅ Annotation generated successfully!")

        # Save annotated frame
        print(f"💾 Saving annotated frame...")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        annotated_image.save(output_path, 'JPEG', quality=90)
        print(f"   ✅ Saved: {output_path.name}")

        return True

    except Exception as e:
        print(f"❌ Error during annotation: {e}")
        return False

def main():
    print("🔄 Regenerating Frames with Improved Weapon Axis Detection")
    print("=" * 60)
    print("Updated prompt with:")
    print("  • Clock position reference (12 o'clock = 270°, 6 o'clock = 90°, etc.)")
    print("  • Explicit weapon barrel direction analysis")
    print("  • Step-by-step weapon direction determination")
    print("=" * 60)
    print()

    frames_to_regenerate = [
        (0, 9.4, "Frame 1 - Soldier in corner needs 2 o'clock direction (330°)"),
        (2, 28.3, "Frame 3 - Center soldiers need 6 o'clock (90°), outer soldiers need 5 o'clock (60°)")
    ]

    success_count = 0

    for frame_index, timestamp, description in frames_to_regenerate:
        print(f"\n{'='*60}")
        print(f"🖼️  REGENERATING FRAME {frame_index + 1}")
        print(f"   {description}")
        print(f"{'='*60}\n")

        if regenerate_frame(frame_index, timestamp):
            success_count += 1
            print(f"\n✅ Frame {frame_index + 1} regenerated successfully!\n")
        else:
            print(f"\n❌ Frame {frame_index + 1} regeneration failed!\n")

    print("=" * 60)
    print(f"✅ Regeneration complete: {success_count}/{len(frames_to_regenerate)} frames")
    print("=" * 60)

    if success_count < len(frames_to_regenerate):
        print("\n⚠️  Some frames failed. This may be due to:")
        print("   • Gemini API rate limiting")
        print("   • Temporary API errors (500 Internal Error)")
        print("   • Try running the script again in a few moments")

    return 0 if success_count == len(frames_to_regenerate) else 1

if __name__ == "__main__":
    exit(main())
