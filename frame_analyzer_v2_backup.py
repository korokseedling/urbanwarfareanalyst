"""
Frame Analyzer Module - Stage 2 (Updated)
Handles tactical analysis using Gemini 2.5 Flash and annotation using Gemini 3 Pro Image
"""

import json
import base64
import io
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image
import google.generativeai as genai


class FrameAnalyzer:
    """Analyzes urban warfare training frames and generates tactical annotations"""

    def __init__(self, config):
        """
        Initialize the FrameAnalyzer

        Args:
            config: Configuration object with API keys and model settings
        """
        self.config = config

        # Configure Gemini API
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in configuration")

        genai.configure(api_key=config.GEMINI_API_KEY)

        # Initialize models
        self.analysis_model = genai.GenerativeModel(config.GEMINI_ANALYSIS_MODEL)
        self.image_model = genai.GenerativeModel(config.GEMINI_IMAGE_MODEL)

        # Load prompt templates
        self.analysis_prompt_template = self._load_prompt_template('frame_analysis.txt')
        self.annotation_prompt_template = self._load_prompt_template('image_annotation.txt')

        # Ensure output directories exist
        config.ANALYSIS_JSON_DIR.mkdir(parents=True, exist_ok=True)
        config.ANNOTATED_FRAMES_DIR.mkdir(parents=True, exist_ok=True)

    def _load_prompt_template(self, filename: str) -> str:
        """Load a prompt template from the prompts directory"""
        prompt_path = self.config.PROMPTS_DIR / filename
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt template not found: {prompt_path}")

        with open(prompt_path, 'r') as f:
            return f.read()

    def analyze_frame(
        self,
        image: Image.Image,
        timestamp: float,
        scenario_context: str = ""
    ) -> Dict:
        """
        Analyze a single frame for tactical information

        Args:
            image: PIL Image object
            timestamp: Timestamp of the frame in seconds
            scenario_context: Optional context about the scenario

        Returns:
            Dictionary containing tactical analysis
        """
        print(f"  🔍 Analyzing frame at {timestamp:.1f}s...")

        # Prepare the prompt
        prompt = self.analysis_prompt_template.format(
            timestamp=timestamp,
            context=scenario_context if scenario_context else "Urban warfare training exercise"
        )

        try:
            # Generate analysis using Gemini 2.5 Flash
            response = self.analysis_model.generate_content(
                [prompt, image],
                generation_config={
                    'temperature': self.config.TEMPERATURE,
                    'max_output_tokens': self.config.MAX_TOKENS,
                }
            )

            # Parse JSON response
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            analysis = json.loads(response_text)

            print(f"  ✅ Analysis complete - Score: {analysis.get('score', 'N/A')}/100")

            return analysis

        except json.JSONDecodeError as e:
            print(f"  ❌ JSON parsing error: {e}")
            print(f"  Raw response: {response_text[:200]}...")
            raise

        except Exception as e:
            print(f"  ❌ Analysis error: {e}")
            raise

    def save_analysis_json(
        self,
        analysis: Dict,
        video_name: str,
        frame_index: int
    ) -> Path:
        """
        Save analysis JSON to disk

        Args:
            analysis: Analysis dictionary
            video_name: Name of the video (without extension)
            frame_index: Index of the frame

        Returns:
            Path to the saved JSON file
        """
        # Create video-specific directory
        output_dir = self.config.ANALYSIS_JSON_DIR / video_name
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save JSON
        timestamp = analysis.get('timestamp', 0)
        filename = f"analysis_{frame_index:03d}_{timestamp:.1f}s.json"
        output_path = output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)

        return output_path

    def _create_tactical_summary(self, analysis: Dict) -> str:
        """
        Create a condensed tactical summary for annotation prompt

        Args:
            analysis: Full tactical analysis dictionary

        Returns:
            Condensed summary string
        """
        summary_parts = []

        # Cover summary
        if 'cover_summary' in analysis:
            cover = analysis['cover_summary']
            summary_parts.append(f"COVER STATUS:")
            summary_parts.append(f"  - Full Cover: {cover.get('full_cover', 0)} soldiers")
            summary_parts.append(f"  - Partial Cover: {cover.get('partial_cover', 0)} soldiers")
            summary_parts.append(f"  - No Cover: {cover.get('no_cover', 0)} soldiers")
            summary_parts.append(f"  - Exposed: {cover.get('exposed', 0)} soldiers")

        # Formation
        if 'movement_analysis' in analysis:
            movement = analysis['movement_analysis']
            summary_parts.append(f"\nFORMATION: {movement.get('formation', 'unknown').upper()}")
            summary_parts.append(f"SPACING: {movement.get('spacing', 'unknown').upper()}")

        # Top threats (max 2)
        if 'primary_threats' in analysis:
            threats = analysis['primary_threats']
            high_threats = [t for t in threats if t.get('threat_level') == 'high'][:2]
            if high_threats:
                summary_parts.append(f"\nKEY THREATS:")
                for threat in high_threats:
                    summary_parts.append(f"  - {threat.get('type', 'unknown').upper()}: {threat.get('description', 'unknown location')}")

        return "\n".join(summary_parts)

    def annotate_frame(
        self,
        image: Image.Image,
        analysis: Dict
    ) -> Image.Image:
        """
        Generate annotated frame using Gemini 3 Pro Image model

        Args:
            image: Original PIL Image
            analysis: Analysis dictionary from analyze_frame()

        Returns:
            Annotated PIL Image
        """
        print(f"  🎨 Generating tactical overlay...")

        # Create condensed tactical summary
        tactical_summary = self._create_tactical_summary(analysis)

        # Prepare annotation prompt
        prompt = self.annotation_prompt_template.format(
            timestamp=analysis.get('timestamp', 0),
            score=analysis.get('score', 0),
            tactical_summary=tactical_summary
        )

        try:
            # Note: Gemini 3 Pro Image Preview currently doesn't support image generation via API
            # Falling back to a simpler overlay approach
            # This would need to be updated when the API supports image-to-image generation

            # For now, create a simple PIL-based annotation with minimal info
            from PIL import ImageDraw, ImageFont

            annotated = image.copy()
            draw = ImageDraw.Draw(annotated, 'RGBA')

            # Try to load a font
            try:
                font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
                font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()

            # Add score (top-right)
            score = analysis.get('score', 0)
            score_text = f"{score}/100"
            score_color = self._get_score_color(score)

            # Draw score background
            score_bbox = draw.textbbox((0, 0), score_text, font=font_large)
            score_width = score_bbox[2] - score_bbox[0]
            score_height = score_bbox[3] - score_bbox[1]

            padding = 15
            score_x = annotated.width - score_width - padding * 2 - 20
            score_y = 20

            draw.rectangle(
                [score_x, score_y, score_x + score_width + padding * 2, score_y + score_height + padding * 2],
                fill=(0, 0, 0, 200)
            )

            draw.text(
                (score_x + padding, score_y + padding),
                score_text,
                fill=score_color,
                font=font_large
            )

            # Add timestamp (top-left)
            timestamp_text = f"T: {analysis.get('timestamp', 0):.1f}s"
            draw.rectangle(
                [20, 20, 150, 50],
                fill=(0, 0, 0, 200)
            )
            draw.text((30, 25), timestamp_text, fill=(255, 255, 255), font=font_small)

            # Add cover summary (bottom-left)
            if 'cover_summary' in analysis:
                cover = analysis['cover_summary']
                cover_text = (
                    f"Cover: {cover.get('full_cover', 0)}F "
                    f"{cover.get('partial_cover', 0)}P "
                    f"{cover.get('no_cover', 0)}N "
                    f"{cover.get('exposed', 0)}E"
                )

                cover_bbox = draw.textbbox((0, 0), cover_text, font=font_small)
                cover_width = cover_bbox[2] - cover_bbox[0]
                cover_y = annotated.height - 60

                draw.rectangle(
                    [20, cover_y, 40 + cover_width, cover_y + 35],
                    fill=(0, 0, 0, 200)
                )
                draw.text((30, cover_y + 8), cover_text, fill=(255, 255, 255), font=font_small)

            print(f"  ✅ Tactical overlay generated")
            return annotated

        except Exception as e:
            print(f"  ❌ Annotation error: {e}")
            print(f"  ⚠️  Returning original image")
            return image

    def save_annotated_frame(
        self,
        annotated_image: Image.Image,
        video_name: str,
        frame_index: int,
        timestamp: float
    ) -> Path:
        """
        Save annotated frame to disk

        Args:
            annotated_image: Annotated PIL Image
            video_name: Name of the video (without extension)
            frame_index: Index of the frame
            timestamp: Timestamp in seconds

        Returns:
            Path to saved image
        """
        # Create video-specific directory
        output_dir = self.config.ANNOTATED_FRAMES_DIR / video_name
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save image
        filename = f"annotated_{frame_index:03d}_{timestamp:.1f}s.jpg"
        output_path = output_dir / filename

        annotated_image.save(
            output_path,
            format='JPEG',
            quality=self.config.FRAME_QUALITY
        )

        return output_path

    def _get_score_color(self, score: int) -> Tuple[int, int, int]:
        """Get color based on score"""
        if score >= 90:
            return (0, 255, 0)      # Green
        elif score >= 70:
            return (255, 255, 0)    # Yellow
        elif score >= 50:
            return (255, 165, 0)    # Orange
        else:
            return (255, 0, 0)      # Red
