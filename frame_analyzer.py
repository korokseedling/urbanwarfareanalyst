"""
Frame Analyzer Module - Stage 2 (Enhanced Annotations)
Handles tactical analysis using Gemini 2.5 Flash and enhanced visual annotations
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import google.generativeai as genai


class FrameAnalyzer:
    """Analyzes urban warfare training frames and generates enhanced tactical annotations"""

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

    def _get_annotation_data(
        self,
        image: Image.Image,
        analysis: Dict
    ) -> Optional[Dict]:
        """
        Get soldier positions, threat axes, and blindspots from Gemini Image Model

        Args:
            image: Original PIL Image
            analysis: Tactical analysis dictionary

        Returns:
            Dictionary with soldiers, threat_axes, and blindspots
        """
        print(f"    📍 Getting annotation positions from AI...")

        tactical_summary = self._create_tactical_summary(analysis)

        # Prepare annotation prompt
        prompt = self.annotation_prompt_template.format(
            timestamp=analysis.get('timestamp', 0),
            score=analysis.get('score', 0),
            tactical_summary=tactical_summary
        )

        try:
            # Get annotation guidance from Gemini Image Model
            response = self.image_model.generate_content(
                [prompt, image],
                generation_config={
                    'temperature': 0.4,  # Lower temperature for more precise coordinates
                    'max_output_tokens': 2048,
                }
            )

            response_text = response.text.strip()

            # Remove markdown code blocks
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            annotation_data = json.loads(response_text)
            print(f"    ✅ Got {len(annotation_data.get('soldiers', []))} soldiers, {len(annotation_data.get('blindspots', []))} blindspots")

            return annotation_data

        except Exception as e:
            print(f"    ⚠️  Could not get annotation data from AI: {e}")
            return None

    def annotate_frame(
        self,
        image: Image.Image,
        analysis: Dict
    ) -> Image.Image:
        """
        Generate annotated frame with enhanced visual overlays

        Args:
            image: Original PIL Image
            analysis: Analysis dictionary from analyze_frame()

        Returns:
            Annotated PIL Image
        """
        print(f"  🎨 Generating enhanced tactical overlay...")

        # Get annotation data from AI
        annotation_data = self._get_annotation_data(image, analysis)

        # Create annotated image
        annotated = image.copy()
        draw = ImageDraw.Draw(annotated, 'RGBA')

        # Load fonts
        try:
            font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
            font_medium = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
            font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()

        img_width = annotated.width
        img_height = annotated.height

        # Draw annotations if we have the data
        if annotation_data:
            # 1. Draw blindspots (red rectangles) - draw first so they're in background
            for blindspot in annotation_data.get('blindspots', []):
                self._draw_blindspot(draw, blindspot, img_width, img_height, font_small)

            # 2. Draw soldiers and threat axes
            for soldier in annotation_data.get('soldiers', []):
                self._draw_soldier_and_axis(draw, soldier, img_width, img_height)

        # Add score overlay (top-right)
        score = analysis.get('score', 0)
        self._draw_score_badge(draw, score, img_width, font_large)

        # Add timestamp (top-left)
        timestamp_text = f"T: {analysis.get('timestamp', 0):.1f}s"
        draw.rectangle([20, 20, 150, 50], fill=(0, 0, 0, 200))
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
            cover_y = img_height - 60

            draw.rectangle(
                [20, cover_y, 40 + cover_width, cover_y + 35],
                fill=(0, 0, 0, 200)
            )
            draw.text((30, cover_y + 8), cover_text, fill=(255, 255, 255), font=font_small)

        print(f"  ✅ Enhanced tactical overlay generated")
        return annotated

    def _draw_soldier_and_axis(
        self,
        draw: ImageDraw.Draw,
        soldier: Dict,
        img_width: int,
        img_height: int
    ):
        """Draw green circle for soldier and green arrow for threat axis"""
        pos = soldier.get('position', {})
        x = int((pos.get('x', 50) / 100) * img_width)
        y = int((pos.get('y', 50) / 100) * img_height)

        # Draw green circle around soldier
        radius = 25
        draw.ellipse(
            [x - radius, y - radius, x + radius, y + radius],
            outline=(0, 255, 0, 255),
            width=3
        )

        # Draw threat axis arrow
        threat_axis = soldier.get('threat_axis', {})
        direction = threat_axis.get('direction', 0)
        length = threat_axis.get('length', 20)

        # Convert to radians and calculate end point
        angle_rad = math.radians(direction)
        arrow_length = int((length / 100) * min(img_width, img_height))

        end_x = int(x + arrow_length * math.cos(angle_rad))
        end_y = int(y + arrow_length * math.sin(angle_rad))

        # Draw arrow line
        draw.line([(x, y), (end_x, end_y)], fill=(0, 255, 0, 255), width=3)

        # Draw arrowhead
        arrow_size = 10
        arrow_angle1 = angle_rad + math.radians(150)
        arrow_angle2 = angle_rad - math.radians(150)

        arrow_x1 = int(end_x + arrow_size * math.cos(arrow_angle1))
        arrow_y1 = int(end_y + arrow_size * math.sin(arrow_angle1))
        arrow_x2 = int(end_x + arrow_size * math.cos(arrow_angle2))
        arrow_y2 = int(end_y + arrow_size * math.sin(arrow_angle2))

        draw.polygon(
            [(end_x, end_y), (arrow_x1, arrow_y1), (arrow_x2, arrow_y2)],
            fill=(0, 255, 0, 255)
        )

    def _draw_blindspot(
        self,
        draw: ImageDraw.Draw,
        blindspot: Dict,
        img_width: int,
        img_height: int,
        font
    ):
        """Draw red semi-transparent rectangle for blindspot with caption"""
        area = blindspot.get('area', {})
        x = int((area.get('x', 0) / 100) * img_width)
        y = int((area.get('y', 0) / 100) * img_height)
        width = int((area.get('width', 10) / 100) * img_width)
        height = int((area.get('height', 10) / 100) * img_height)

        severity = blindspot.get('severity', 'medium')
        alpha = 120 if severity == 'high' else 80

        # Draw semi-transparent red rectangle
        draw.rectangle(
            [x, y, x + width, y + height],
            fill=(255, 0, 0, alpha),
            outline=(255, 0, 0, 255),
            width=2
        )

        # Add caption
        caption = blindspot.get('caption', 'Blindspot')
        caption_bbox = draw.textbbox((0, 0), caption, font=font)
        caption_width = caption_bbox[2] - caption_bbox[0]
        caption_height = caption_bbox[3] - caption_bbox[1]

        # Position caption above the blindspot area
        caption_x = x + (width - caption_width) // 2
        caption_y = max(5, y - caption_height - 5)

        # Draw caption background
        draw.rectangle(
            [caption_x - 5, caption_y - 2, caption_x + caption_width + 5, caption_y + caption_height + 2],
            fill=(0, 0, 0, 200)
        )

        # Draw caption text
        draw.text((caption_x, caption_y), caption, fill=(255, 255, 255), font=font)

    def _draw_score_badge(
        self,
        draw: ImageDraw.Draw,
        score: int,
        img_width: int,
        font
    ):
        """Draw color-coded score badge in top-right corner"""
        score_text = f"{score}/100"
        score_color = self._get_score_color(score)

        score_bbox = draw.textbbox((0, 0), score_text, font=font)
        score_width = score_bbox[2] - score_bbox[0]
        score_height = score_bbox[3] - score_bbox[1]

        padding = 15
        score_x = img_width - score_width - padding * 2 - 20
        score_y = 20

        draw.rectangle(
            [score_x, score_y, score_x + score_width + padding * 2, score_y + score_height + padding * 2],
            fill=(0, 0, 0, 200)
        )

        draw.text(
            (score_x + padding, score_y + padding),
            score_text,
            fill=score_color,
            font=font
        )

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
