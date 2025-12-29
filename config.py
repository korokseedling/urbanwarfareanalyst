"""
Configuration module for AI Urban Warfare Analyst
Loads settings from .env file and provides centralized config access
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file explicitly
_env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=_env_path, override=True)

class Config:
    """Central configuration class for the Urban Warfare Analyst"""

    # ==================== API Configuration ====================
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

    # ==================== Model Configuration ====================
    # Stage-specific models
    GEMINI_ANALYSIS_MODEL = os.getenv('GEMINI_ANALYSIS_MODEL', 'gemini-2.5-flash-preview-09-2025')
    GEMINI_IMAGE_MODEL = os.getenv('GEMINI_IMAGE_MODEL', 'gemini-3-pro-image-preview')

    # Default/fallback model
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash-preview-09-2025')

    # Model parameters
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '2048'))

    # ==================== Video Processing Configuration ====================
    MAX_VIDEO_DURATION = int(os.getenv('MAX_VIDEO_DURATION', '120'))  # seconds
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '100'))  # megabytes
    SUPPORTED_FORMATS = ['.mp4', '.mov', '.avi', '.mkv', '.wmv']

    # ==================== Frame Extraction Configuration ====================
    NUM_FRAMES = int(os.getenv('NUM_FRAMES', '3'))
    FRAME_RESIZE_MAX = int(os.getenv('FRAME_RESIZE_MAX', '720'))  # max dimension in pixels
    FRAME_EXTRACTION_POSITIONS = [0.25, 0.50, 0.75]  # Extract at 25%, 50%, 75%
    FRAME_FORMAT = 'JPEG'
    FRAME_QUALITY = 85  # JPEG quality 0-100

    # ==================== Directory Configuration ====================
    BASE_DIR = Path(__file__).parent
    OUTPUT_DIR = BASE_DIR / 'outputs'
    PROMPTS_DIR = BASE_DIR / 'prompts'

    # Stage 2 output directories
    ANALYSIS_JSON_DIR = OUTPUT_DIR / 'analysis_json'
    ANNOTATED_FRAMES_DIR = OUTPUT_DIR / 'annotated_frames'

    # Stage 3 output directories
    SUMMARY_DIR = OUTPUT_DIR / 'summaries'
    INFOGRAPHIC_DIR = OUTPUT_DIR / 'infographics'

    # ==================== Stage 2: Analysis Configuration ====================
    ENABLE_PARALLEL_ANALYSIS = True
    MAX_CONCURRENT_REQUESTS = 3

    # Overlay/annotation settings
    BBOX_COLOR = (255, 0, 0)  # Red for bounding boxes
    BBOX_THICKNESS = 2
    TEXT_COLOR = (255, 255, 255)  # White text
    TEXT_BG_COLOR = (0, 0, 0, 180)  # Semi-transparent black background

    # ==================== Stage 3: Summary Configuration ====================
    SCORE_RANGE = (0, 100)
    BENCHMARK_THRESHOLD = 70

    # Performance categories
    PERFORMANCE_CATEGORIES = [
        'cover_utilization',
        'threat_awareness',
        'formation_discipline',
        'spacing',
        'movement_efficiency'
    ]

    @classmethod
    def validate(cls):
        """Validate that required configuration is present"""
        errors = []

        if not cls.GEMINI_API_KEY or cls.GEMINI_API_KEY == 'your_gemini_api_key_here':
            errors.append("GEMINI_API_KEY not set in .env file")

        if cls.NUM_FRAMES < 1:
            errors.append(f"NUM_FRAMES must be at least 1, got {cls.NUM_FRAMES}")

        if cls.FRAME_RESIZE_MAX < 100:
            errors.append(f"FRAME_RESIZE_MAX must be at least 100, got {cls.FRAME_RESIZE_MAX}")

        return errors

    @classmethod
    def print_config(cls):
        """Print current configuration (hiding sensitive data)"""
        print("=" * 60)
        print("AI URBAN WARFARE ANALYST - CONFIGURATION")
        print("=" * 60)
        print(f"API Key Set: {'✅' if cls.GEMINI_API_KEY and cls.GEMINI_API_KEY != 'your_gemini_api_key_here' else '❌'}")
        print(f"\nModels:")
        print(f"  Stage 2 (Analysis): {cls.GEMINI_ANALYSIS_MODEL}")
        print(f"  Stage 3 (Overlays): {cls.GEMINI_IMAGE_MODEL}")
        print(f"  Default/Fallback: {cls.GEMINI_MODEL}")
        print(f"\nModel Parameters:")
        print(f"  Temperature: {cls.TEMPERATURE}")
        print(f"  Max Tokens: {cls.MAX_TOKENS}")
        print(f"\nFrame Extraction:")
        print(f"  Number of Frames: {cls.NUM_FRAMES}")
        print(f"  Extraction Positions: {[f'{int(p*100)}%' for p in cls.FRAME_EXTRACTION_POSITIONS]}")
        print(f"  Max Frame Size: {cls.FRAME_RESIZE_MAX}px")
        print(f"  Frame Format: {cls.FRAME_FORMAT} (Quality: {cls.FRAME_QUALITY})")
        print(f"\nVideo Limits:")
        print(f"  Max Duration: {cls.MAX_VIDEO_DURATION}s")
        print(f"  Max File Size: {cls.MAX_FILE_SIZE_MB}MB")
        print(f"  Supported Formats: {', '.join(cls.SUPPORTED_FORMATS)}")
        print(f"\nDirectories:")
        print(f"  Base: {cls.BASE_DIR}")
        print(f"  Output: {cls.OUTPUT_DIR}")
        print(f"  Prompts: {cls.PROMPTS_DIR}")
        print("=" * 60)


# Create a singleton instance
config = Config()

# Validate on import (optional - can comment out if too strict)
validation_errors = config.validate()
if validation_errors:
    print("⚠️ Configuration Warnings:")
    for error in validation_errors:
        print(f"  - {error}")
