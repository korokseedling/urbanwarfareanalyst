"""
Performance Summarizer Module - Stage 3
Aggregates frame analysis and generates performance summary with tactical infographic
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from PIL import Image
import google.generativeai as genai


class PerformanceSummarizer:
    """Generates performance summaries and tactical infographics from frame analyses"""

    def __init__(self, config):
        """
        Initialize the PerformanceSummarizer

        Args:
            config: Configuration object with API keys and model settings
        """
        self.config = config

        # Configure Gemini API
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in configuration")

        genai.configure(api_key=config.GEMINI_API_KEY)

        # Initialize image model for infographic generation
        self.image_model = genai.GenerativeModel(config.GEMINI_IMAGE_MODEL)

        # Load prompt template
        self.infographic_prompt_template = self._load_prompt_template('infographic_generation.txt')

        # Ensure output directories exist
        config.SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
        config.INFOGRAPHIC_DIR.mkdir(parents=True, exist_ok=True)

    def _load_prompt_template(self, filename: str) -> str:
        """Load a prompt template from the prompts directory"""
        prompt_path = self.config.PROMPTS_DIR / filename
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt template not found: {prompt_path}")

        with open(prompt_path, 'r') as f:
            return f.read()

    def aggregate_analysis(
        self,
        analysis_results: List[Dict],
        video_metadata: Dict
    ) -> Dict:
        """
        Aggregate analysis from all frames

        Args:
            analysis_results: List of frame analysis dictionaries
            video_metadata: Video metadata dictionary

        Returns:
            Aggregated summary dictionary
        """
        print("📊 Aggregating analysis from all frames...")

        if not analysis_results:
            raise ValueError("No analysis results to aggregate")

        # Calculate statistics
        total_frames = len(analysis_results)
        scores = [r['analysis'].get('score', 0) for r in analysis_results]
        avg_score = sum(scores) / total_frames if total_frames > 0 else 0

        # Aggregate errors and strengths
        all_errors = []
        all_strengths = []
        for result in analysis_results:
            analysis = result['analysis']
            all_errors.extend(analysis.get('tactical_errors', []))
            all_strengths.extend(analysis.get('tactical_strengths', []))

        # Count soldier appearances across frames
        total_soldier_count = sum(
            r['analysis'].get('soldier_count', 0)
            for r in analysis_results
        )

        # Aggregate cover statistics
        cover_stats = {
            'full_cover': 0,
            'partial_cover': 0,
            'no_cover': 0,
            'exposed': 0
        }

        for result in analysis_results:
            cover_summary = result['analysis'].get('cover_summary', {})
            for key in cover_stats:
                cover_stats[key] += cover_summary.get(key, 0)

        # Formation analysis
        formations = [
            r['analysis'].get('movement_analysis', {}).get('formation', 'unknown')
            for r in analysis_results
        ]

        # Identify most common issues
        error_frequency = {}
        for error in all_errors:
            # Simple keyword extraction for categorization
            if 'spacing' in error.lower() or 'tight' in error.lower():
                error_frequency['spacing_issues'] = error_frequency.get('spacing_issues', 0) + 1
            if 'cover' in error.lower() or 'exposed' in error.lower():
                error_frequency['cover_issues'] = error_frequency.get('cover_issues', 0) + 1
            if 'formation' in error.lower():
                error_frequency['formation_issues'] = error_frequency.get('formation_issues', 0) + 1

        # Identify strengths
        strength_frequency = {}
        for strength in all_strengths:
            if 'cover' in strength.lower():
                strength_frequency['cover_utilization'] = strength_frequency.get('cover_utilization', 0) + 1
            if 'formation' in strength.lower() or 'stack' in strength.lower():
                strength_frequency['formation_discipline'] = strength_frequency.get('formation_discipline', 0) + 1
            if 'weapon' in strength.lower() or 'muzzle' in strength.lower():
                strength_frequency['weapon_discipline'] = strength_frequency.get('weapon_discipline', 0) + 1

        # Create summary
        summary = {
            'video_name': video_metadata.get('filename', 'Unknown'),
            'duration': video_metadata.get('duration', 0),
            'resolution': video_metadata.get('resolution', [0, 0]),
            'frame_count': total_frames,
            'frames_analyzed': [
                {
                    'index': r['index'],
                    'timestamp': r['timestamp'],
                    'score': r['analysis'].get('score', 0),
                    'formation': r['analysis'].get('movement_analysis', {}).get('formation', 'unknown'),
                    'soldier_count': r['analysis'].get('soldier_count', 0),
                    'cover_summary': r['analysis'].get('cover_summary', {})
                }
                for r in analysis_results
            ],
            'overall_performance': {
                'average_score': round(avg_score, 1),
                'min_score': min(scores),
                'max_score': max(scores),
                'score_range': max(scores) - min(scores),
                'rating': self._get_performance_rating(avg_score)
            },
            'cover_statistics': cover_stats,
            'total_soldiers': total_soldier_count,
            'formations_used': list(set(formations)),
            'tactical_errors': {
                'total': len(all_errors),
                'by_category': error_frequency,
                'examples': all_errors[:5]  # Top 5
            },
            'tactical_strengths': {
                'total': len(all_strengths),
                'by_category': strength_frequency,
                'examples': all_strengths[:5]  # Top 5
            },
            'recommendations': self._generate_recommendations(
                avg_score,
                error_frequency,
                strength_frequency
            )
        }

        print(f"✅ Aggregation complete:")
        print(f"   Average Score: {summary['overall_performance']['average_score']}/100")
        print(f"   Rating: {summary['overall_performance']['rating']}")
        print(f"   Total Errors: {summary['tactical_errors']['total']}")
        print(f"   Total Strengths: {summary['tactical_strengths']['total']}")

        return summary

    def _get_performance_rating(self, score: float) -> str:
        """Get performance rating based on score"""
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 60:
            return "Satisfactory"
        elif score >= 50:
            return "Needs Improvement"
        else:
            return "Requires Remedial Training"

    def _generate_recommendations(
        self,
        avg_score: float,
        errors: Dict,
        strengths: Dict
    ) -> List[str]:
        """Generate training recommendations based on performance"""
        recommendations = []

        # Score-based recommendations
        if avg_score < 70:
            recommendations.append("Schedule additional training sessions focusing on fundamentals")

        # Error-based recommendations
        if errors.get('spacing_issues', 0) >= 2:
            recommendations.append("Practice spacing drills - maintain 3-5 meter intervals during movement")

        if errors.get('cover_issues', 0) >= 2:
            recommendations.append("Emphasize cover utilization - always move from cover to cover")

        if errors.get('formation_issues', 0) >= 2:
            recommendations.append("Review and practice standard formations (wedge, line, column)")

        # Strength-based recommendations
        if strengths.get('weapon_discipline', 0) >= 2:
            recommendations.append("Continue excellent weapon handling - maintain this standard")

        if strengths.get('formation_discipline', 0) >= 2:
            recommendations.append("Formation discipline is strong - focus on refining entry techniques")

        # Default recommendations
        if not recommendations:
            recommendations.append("Continue current training regimen")
            recommendations.append("Focus on maintaining consistent performance across all scenarios")

        # Cap at 5 recommendations
        return recommendations[:5]

    def generate_infographic(
        self,
        summary: Dict,
        analysis_results: List[Dict]
    ) -> Optional[Image.Image]:
        """
        Generate tactical infographic using Gemini 3 Pro Image

        Args:
            summary: Aggregated summary dictionary
            analysis_results: List of frame analysis dictionaries

        Returns:
            PIL Image of the infographic, or None if generation fails
        """
        print("🎨 Generating tactical infographic...")

        # Prepare frame summaries for prompt
        frame_summaries = []
        for result in analysis_results:
            analysis = result['analysis']
            frame_summary = f"""
Frame {result['index'] + 1} (T={result['timestamp']:.1f}s):
- Score: {analysis.get('score', 0)}/100
- Formation: {analysis.get('movement_analysis', {}).get('formation', 'unknown').upper()}
- Soldiers: {analysis.get('soldier_count', 0)}
- Cover: {analysis.get('cover_summary', {}).get('full_cover', 0)}F / {analysis.get('cover_summary', {}).get('partial_cover', 0)}P / {analysis.get('cover_summary', {}).get('no_cover', 0)}N / {analysis.get('cover_summary', {}).get('exposed', 0)}E
- Key Error: {analysis.get('tactical_errors', ['None'])[0][:100] if analysis.get('tactical_errors') else 'None'}
"""
            frame_summaries.append(frame_summary)

        # Prepare prompt
        prompt = self.infographic_prompt_template.format(
            video_name=summary['video_name'],
            duration=summary['duration'],
            frame_count=summary['frame_count'],
            frame_summaries="\n".join(frame_summaries),
            avg_score=summary['overall_performance']['average_score'],
            total_soldiers=summary['total_soldiers'],
            total_errors=summary['tactical_errors']['total'],
            total_strengths=summary['tactical_strengths']['total']
        )

        try:
            print("  📡 Calling Gemini 3 Pro Image model...")
            print("  ⚠️  Note: Image generation may take 30-60 seconds...")

            # Attempt to generate infographic with Gemini 3 Pro Image
            response = self.image_model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'max_output_tokens': 4096,
                }
            )

            # Check if response contains image data (check parts first, before accessing .text)
            if hasattr(response, 'parts') and response.parts:
                print(f"  🔍 Response contains {len(response.parts)} part(s)")

                for i, part in enumerate(response.parts):
                    # Check for inline_data (image data)
                    if hasattr(part, 'inline_data') and part.inline_data:
                        print(f"  ✅ Found image data in part {i}!")
                        print(f"  📊 MIME type: {part.inline_data.mime_type}")

                        import base64
                        from io import BytesIO

                        # Data is already in bytes format (not base64 encoded)
                        if isinstance(part.inline_data.data, bytes):
                            image_data = part.inline_data.data
                        else:
                            # Fallback: try base64 decode
                            import base64
                            image_data = base64.b64decode(part.inline_data.data)

                        print(f"  📊 Image data size: {len(image_data)} bytes")

                        # Open as PIL Image
                        infographic = Image.open(BytesIO(image_data))
                        print(f"  📊 Image size: {infographic.size}")
                        print(f"  📊 Image mode: {infographic.mode}")
                        print("  ✅ Infographic generated successfully!")
                        return infographic

                    # Check for text data
                    elif hasattr(part, 'text') and part.text:
                        print(f"  ℹ️  Part {i} contains text (not image)")

            # If we can safely access .text (no inline_data), show it
            try:
                if hasattr(response, 'text'):
                    response_text = response.text[:200] if len(response.text) > 200 else response.text
                    print(f"  📝 Response text preview: {response_text}...")
            except:
                pass  # Ignore if we can't access text

            # If no image found in response, return None
            print("  ⚠️  Response received but no image data found")
            print("  💡 Gemini 3 Pro Image currently returns text descriptions, not generated images")
            print("  💡 Image generation API capability may not be available yet")
            return None

        except Exception as e:
            print(f"  ❌ Infographic generation error: {e}")
            return None

    def save_summary_json(
        self,
        summary: Dict,
        video_name: str
    ) -> Path:
        """
        Save summary JSON to disk

        Args:
            summary: Summary dictionary
            video_name: Name of the video (without extension)

        Returns:
            Path to the saved JSON file
        """
        output_dir = self.config.SUMMARY_DIR
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"summary_{video_name}.json"
        output_path = output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"💾 Summary saved: {output_path}")
        return output_path

    def save_summary_report(
        self,
        summary: Dict,
        video_name: str
    ) -> Path:
        """
        Save human-readable summary report

        Args:
            summary: Summary dictionary
            video_name: Name of the video (without extension)

        Returns:
            Path to the saved report file
        """
        output_dir = self.config.SUMMARY_DIR
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"report_{video_name}.txt"
        output_path = output_dir / filename

        # Generate report
        report_lines = [
            "=" * 80,
            "TACTICAL PERFORMANCE SUMMARY",
            "=" * 80,
            f"\nVideo: {summary['video_name']}",
            f"Duration: {summary['duration']:.1f} seconds",
            f"Frames Analyzed: {summary['frame_count']}",
            f"Total Soldiers: {summary['total_soldiers']}",
            "\n" + "=" * 80,
            "OVERALL PERFORMANCE",
            "=" * 80,
            f"\nAverage Score: {summary['overall_performance']['average_score']}/100",
            f"Rating: {summary['overall_performance']['rating']}",
            f"Score Range: {summary['overall_performance']['min_score']}-{summary['overall_performance']['max_score']}",
            "\n" + "=" * 80,
            "FRAME-BY-FRAME SCORES",
            "=" * 80,
        ]

        for frame in summary['frames_analyzed']:
            report_lines.append(
                f"\nFrame {frame['index'] + 1} (T={frame['timestamp']:.1f}s): "
                f"{frame['score']}/100 - {frame['formation'].upper()}"
            )

        report_lines.extend([
            "\n" + "=" * 80,
            "COVER UTILIZATION",
            "=" * 80,
            f"\nFull Cover: {summary['cover_statistics']['full_cover']} instances",
            f"Partial Cover: {summary['cover_statistics']['partial_cover']} instances",
            f"No Cover: {summary['cover_statistics']['no_cover']} instances",
            f"Exposed: {summary['cover_statistics']['exposed']} instances",
            "\n" + "=" * 80,
            f"TACTICAL ERRORS ({summary['tactical_errors']['total']} total)",
            "=" * 80,
        ])

        for i, error in enumerate(summary['tactical_errors']['examples'], 1):
            report_lines.append(f"\n{i}. {error}")

        report_lines.extend([
            "\n" + "=" * 80,
            f"TACTICAL STRENGTHS ({summary['tactical_strengths']['total']} total)",
            "=" * 80,
        ])

        for i, strength in enumerate(summary['tactical_strengths']['examples'], 1):
            report_lines.append(f"\n{i}. {strength}")

        report_lines.extend([
            "\n" + "=" * 80,
            "TRAINING RECOMMENDATIONS",
            "=" * 80,
        ])

        for i, rec in enumerate(summary['recommendations'], 1):
            report_lines.append(f"\n{i}. {rec}")

        report_lines.extend([
            "\n" + "=" * 80,
            "END OF REPORT",
            "=" * 80,
        ])

        # Write report
        with open(output_path, 'w') as f:
            f.write('\n'.join(report_lines))

        print(f"📄 Report saved: {output_path}")
        return output_path
