#!/usr/bin/env python3
"""
Regenerate annotations with specific corrections:
- Frame 1: Bottom right soldier should be 2 o'clock (330°)
- Frame 3: All 3 soldiers on the right should be 6 o'clock (90°)
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

    # Load original frame
    print("📸 Loading original frame...")
    image = Image.open(original_frame_path)
    print(f"   ✅ Loaded: {image.width}x{image.height}")

    # Load analysis
    with open(analysis_json_path, 'r') as f:
        analysis = json.load(f)
    print(f"   ✅ Score: {analysis.get('score')}/100")
    print(f"   ✅ Soldiers: {analysis.get('soldier_count')}")

    # Generate annotated frame
    print("🎨 Generating annotated frame with corrected weapon axes...")

    try:
        annotated_image = analyzer.annotate_frame(
            image=image,
            analysis=analysis
        )

        print("   ✅ Annotation generated!")

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
    print("🔄 Regenerating Frames with Corrected Weapon Directions")
    print("=" * 70)
    print("SPECIFIC CORRECTIONS:")
    print("  Frame 1 (T=9.4s):")
    print("    • Bottom right soldier: 2 o'clock direction (330°)")
    print("    • (Other soldiers should remain correct)")
    print()
    print("  Frame 3 (T=28.3s):")
    print("    • All 3 soldiers on RIGHT side: 6 o'clock direction (90°)")
    print("    • Left soldier: Check weapon direction")
    print()
    print("Updated prompt emphasizes:")
    print("  • Soldiers in room entry = 6 o'clock (90°) if aiming downward")
    print("  • Bottom frame soldier covering corner = 2 o'clock (330°)")
    print("=" * 70)
    print()

    frames_to_regenerate = [
        (0, 9.4, "Frame 1 - Fix BOTTOM right soldier to 2 o'clock (330°)"),
        (2, 28.3, "Frame 3 - Fix all 3 RIGHT soldiers to 6 o'clock (90°)")
    ]

    success_count = 0

    for frame_index, timestamp, description in frames_to_regenerate:
        print(f"\n{'='*70}")
        print(f"🖼️  REGENERATING FRAME {frame_index + 1}")
        print(f"   {description}")
        print(f"{'='*70}\n")

        if regenerate_frame(frame_index, timestamp):
            success_count += 1
            print(f"\n✅ Frame {frame_index + 1} complete!\n")
        else:
            print(f"\n❌ Frame {frame_index + 1} failed!\n")

    print("=" * 70)
    print(f"✅ Regeneration complete: {success_count}/{len(frames_to_regenerate)} frames")
    print("=" * 70)

    if success_count == len(frames_to_regenerate):
        print("\n🎯 Please verify:")
        print("  Frame 1: Bottom right soldier arrow points at ~2 o'clock (330°)")
        print("  Frame 3: All 3 right-side soldiers arrows point at 6 o'clock (90°)")
    else:
        print("\n⚠️  Some frames failed - try running again")

    return 0 if success_count == len(frames_to_regenerate) else 1

if __name__ == "__main__":
    exit(main())
