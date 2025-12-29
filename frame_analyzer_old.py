"""
Frame Analyzer Module - Stage 2
Handles tactical analysis of extracted frames using Gemini 2.5 Flash
"""

import json
import base64
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
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

        # Load analysis prompt template
        self.prompt_template = self._load_prompt_template()

        # Ensure output directories exist
        config.ANALYSIS_JSON_DIR.mkdir(parents=True, exist_ok=True)
        config.ANNOTATED_FRAMES_DIR.mkdir(parents=True, exist_ok=True)

    def _load_prompt_template(self) -> str:
        """Load the frame analysis prompt template"""
        prompt_path = self.config.PROMPTS_DIR / 'frame_analysis.txt'
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
        prompt = self.prompt_template.format(
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

    def annotate_frame(
        self,
        image: Image.Image,
        analysis: Dict,
        show_soldiers: bool = True,
        show_threats: bool = True,
        show_score: bool = True
    ) -> Image.Image:
        """
        Generate annotated frame with tactical overlays

        Args:
            image: Original PIL Image
            analysis: Analysis dictionary from analyze_frame()
            show_soldiers: Whether to show soldier positions
            show_threats: Whether to show threat markers
            show_score: Whether to show score overlay

        Returns:
            Annotated PIL Image
        """
        # Create a copy to annotate
        annotated = image.copy()
        draw = ImageDraw.Draw(annotated, 'RGBA')

        # Try to load a font, fall back to default if not available
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
            font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except:
            font = ImageFont.load_default()
            font_large = ImageFont.load_default()

        # Annotate soldier positions
        if show_soldiers and 'soldier_positions' in analysis:
            for soldier in analysis['soldier_positions']:
                x, y = soldier.get('x', 0), soldier.get('y', 0)
                cover = soldier.get('cover_status', 'unknown')

                # Draw circle for soldier
                radius = 20
                color = self._get_cover_color(cover)
                draw.ellipse(
                    [x - radius, y - radius, x + radius, y + radius],
                    outline=color,
                    width=self.config.BBOX_THICKNESS
                )

                # Label
                label = f"{soldier.get('id', 'soldier')}\n{cover}"
                self._draw_label(draw, label, x, y - radius - 30, font, color)

        # Annotate threats
        if show_threats and 'threats' in analysis:
            for threat in analysis['threats']:
                x, y = threat.get('x', 0), threat.get('y', 0)
                threat_type = threat.get('type', 'unknown')
                threat_level = threat.get('threat_level', 'unknown')

                # Draw threat marker (triangle)
                size = 15
                points = [
                    (x, y - size),
                    (x - size, y + size),
                    (x + size, y + size)
                ]
                color = self._get_threat_color(threat_level)
                draw.polygon(points, outline=color, width=self.config.BBOX_THICKNESS)

                # Label
                label = f"{threat_type}\n{threat_level}"
                self._draw_label(draw, label, x, y + size + 5, font, color)

        # Add score overlay
        if show_score:
            score = analysis.get('score', 0)
            score_text = f"TACTICAL SCORE: {score}/100"

            # Draw score box in top-right
            score_color = self._get_score_color(score)
            self._draw_text_box(
                draw,
                score_text,
                annotated.width - 20,
                20,
                font_large,
                score_color,
                align='right'
            )

        # Add timestamp
        timestamp = analysis.get('timestamp', 0)
        timestamp_text = f"T: {timestamp:.1f}s"
        self._draw_text_box(
            draw,
            timestamp_text,
            20,
            20,
            font,
            (255, 255, 255),
            align='left'
        )

        return annotated

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

    def _get_cover_color(self, cover_status: str) -> Tuple[int, int, int]:
        """Get color based on cover status"""
        colors = {
            'full_cover': (0, 255, 0),      # Green
            'partial_cover': (255, 255, 0),  # Yellow
            'no_cover': (255, 128, 0),       # Orange
            'exposed': (255, 0, 0),          # Red
        }
        return colors.get(cover_status, (128, 128, 128))

    def _get_threat_color(self, threat_level: str) -> Tuple[int, int, int]:
        """Get color based on threat level"""
        colors = {
            'high': (255, 0, 0),      # Red
            'medium': (255, 165, 0),  # Orange
            'low': (255, 255, 0),     # Yellow
        }
        return colors.get(threat_level, (128, 128, 128))

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

    def _draw_label(
        self,
        draw: ImageDraw.Draw,
        text: str,
        x: int,
        y: int,
        font,
        color: Tuple[int, int, int]
    ):
        """Draw text label with background"""
        # Get text size
        bbox = draw.textbbox((x, y), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Draw background rectangle
        padding = 2
        draw.rectangle(
            [x - padding, y - padding,
             x + text_width + padding, y + text_height + padding],
            fill=(0, 0, 0, 180)
        )

        # Draw text
        draw.text((x, y), text, fill=color, font=font)

    def _draw_text_box(
        self,
        draw: ImageDraw.Draw,
        text: str,
        x: int,
        y: int,
        font,
        color: Tuple[int, int, int],
        align: str = 'left'
    ):
        """Draw text with background box"""
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        padding = 8

        if align == 'right':
            box_x1 = x - text_width - padding * 2
            box_x2 = x
            text_x = x - text_width - padding
        else:  # left
            box_x1 = x
            box_x2 = x + text_width + padding * 2
            text_x = x + padding

        # Draw background
        draw.rectangle(
            [box_x1, y, box_x2, y + text_height + padding * 2],
            fill=(0, 0, 0, 200)
        )

        # Draw text
        draw.text((text_x, y + padding), text, fill=color, font=font)
