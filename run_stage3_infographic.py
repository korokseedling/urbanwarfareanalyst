"""
Run Stage 3 with infographic generation
"""

import json
from pathlib import Path
from config import config
from performance_summarizer import PerformanceSummarizer
from PIL import Image as PILImage

print("🚀 AI URBAN WARFARE ANALYST - STAGE 3 WITH INFOGRAPHIC")
print("=" * 80)
print()

# Initialize summarizer
summarizer = PerformanceSummarizer(config)
print(f"✅ Performance summarizer initialized")
print(f"🎨 Image Model: {config.GEMINI_IMAGE_MODEL}")
print()

# Load existing data
video_name = "urban_warfare_training"

# Load analysis results
print(f"📁 Loading analysis results for: {video_name}")
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

# Load video metadata
video_metadata = {
    'filename': f"{video_name}.mp4",
    'duration': max(r['timestamp'] for r in analysis_results) * 1.33,
    'resolution': [1280, 720]
}

# Aggregate analysis
print()
print("📊 AGGREGATING FRAME ANALYSES")
print("=" * 80)
summary = summarizer.aggregate_analysis(
    analysis_results=analysis_results,
    video_metadata=video_metadata
)
print("✅ Aggregation complete!")
print()

# Generate infographic
print("🎨 GENERATING TACTICAL INFOGRAPHIC")
print("=" * 80)
infographic = summarizer.generate_infographic(
    summary=summary,
    analysis_results=analysis_results
)

if infographic:
    # Save infographic
    infographic_path = config.INFOGRAPHIC_DIR / f"infographic_{video_name}.png"
    infographic.save(infographic_path)

    print()
    print("=" * 80)
    print("✅ INFOGRAPHIC GENERATION COMPLETE")
    print("=" * 80)
    print(f"📁 Saved to: {infographic_path}")
    print(f"📊 Size: {infographic.size}")
    print(f"📊 Mode: {infographic.mode}")
    print(f"📊 File size: {infographic_path.stat().st_size / 1024:.1f} KB")
    print()

    # Display summary
    print("=" * 80)
    print("PIPELINE SUMMARY")
    print("=" * 80)
    print(f"Video: {summary['video_name']}")
    print(f"Duration: {summary['duration']:.1f}s")
    print(f"Frames Analyzed: {summary['frame_count']}")
    print(f"Overall Score: {summary['overall_performance']['average_score']}/100 ({summary['overall_performance']['rating']})")
    print(f"Tactical Errors: {summary['tactical_errors']['total']}")
    print(f"Tactical Strengths: {summary['tactical_strengths']['total']}")
    print()
    print("📂 All outputs:")
    print(f"  ✅ Analysis JSON: outputs/analysis_json/{video_name}/")
    print(f"  ✅ Annotated frames: outputs/annotated_frames/{video_name}/")
    print(f"  ✅ Summary JSON: outputs/summaries/summary_{video_name}.json")
    print(f"  ✅ Text report: outputs/summaries/report_{video_name}.txt")
    print(f"  ✅ Infographic: {infographic_path}")
    print("=" * 80)
else:
    print()
    print("⚠️  Infographic generation failed")
