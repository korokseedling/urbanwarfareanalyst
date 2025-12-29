"""
Frame Extraction Module for AI Urban Warfare Analyst
Implements percentage-based key frame extraction from video files
"""

import cv2
import base64
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from PIL import Image
import io
import numpy as np

from config import Config


class FrameExtractor:
    """Extract key frames from video files for AI analysis"""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize FrameExtractor

        Args:
            config: Configuration object (uses default Config if None)
        """
        self.config = config or Config()

    def extract_key_frames(
        self,
        video_path: str,
        num_frames: Optional[int] = None,
        positions: Optional[List[float]] = None,
        resize_max: Optional[int] = None
    ) -> List[Tuple[Image.Image, float]]:
        """
        Extract key frames from video at specified percentage positions

        Args:
            video_path: Path to input MP4/video file
            num_frames: Number of frames to extract (default from config)
            positions: List of positions as percentages (0.0-1.0)
                      Default: [0.25, 0.50, 0.75] for 3 frames
            resize_max: Max dimension for resizing (default: 720px)

        Returns:
            List of (PIL Image, timestamp) tuples

        Raises:
            FileNotFoundError: If video file doesn't exist
            ValueError: If video cannot be opened or read
        """
        # Use config defaults if not specified
        num_frames = num_frames or self.config.NUM_FRAMES
        positions = positions or self.config.FRAME_EXTRACTION_POSITIONS
        resize_max = resize_max or self.config.FRAME_RESIZE_MAX

        # Validate video path
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Open video
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")

        try:
            # Get video metadata
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps

            # Validate we have enough frames
            if total_frames < num_frames:
                print(f"⚠️ Warning: Video has {total_frames} frames but {num_frames} requested")

            # Extract frames at specified positions
            frames = []
            for position in positions[:num_frames]:
                # Calculate frame number and timestamp
                frame_number = int(total_frames * position)
                timestamp = frame_number / fps

                # Seek to frame
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                ret, frame = cap.read()

                if not ret:
                    print(f"⚠️ Warning: Could not read frame at position {position:.0%} (frame {frame_number})")
                    continue

                # Convert BGR (OpenCV) to RGB (PIL)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Convert to PIL Image
                pil_image = Image.fromarray(frame_rgb)

                # Resize if needed
                if resize_max:
                    pil_image = self._resize_image(pil_image, resize_max)

                frames.append((pil_image, timestamp))

                print(f"  ✓ Extracted frame at {position:.0%} ({timestamp:.1f}s)")

            return frames

        finally:
            cap.release()

    def _resize_image(self, image: Image.Image, max_dimension: int) -> Image.Image:
        """
        Resize image maintaining aspect ratio

        Args:
            image: PIL Image to resize
            max_dimension: Maximum width or height

        Returns:
            Resized PIL Image
        """
        width, height = image.size

        # Only resize if image exceeds max dimension
        if width <= max_dimension and height <= max_dimension:
            return image

        # Calculate new dimensions maintaining aspect ratio
        if width > height:
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        else:
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))

        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def validate_video(self, video_path: str) -> Dict:
        """
        Validate video file and return metadata

        Args:
            video_path: Path to video file

        Returns:
            Dict with validation result and metadata
        """
        video_path = Path(video_path)

        # Check file exists
        if not video_path.exists():
            return {
                'valid': False,
                'error': f'File not found: {video_path}'
            }

        # Check file extension
        if video_path.suffix.lower() not in self.config.SUPPORTED_FORMATS:
            return {
                'valid': False,
                'error': f'Unsupported format: {video_path.suffix}. '
                        f'Supported: {", ".join(self.config.SUPPORTED_FORMATS)}'
            }

        # Check file size
        file_size_mb = video_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.config.MAX_FILE_SIZE_MB:
            return {
                'valid': False,
                'error': f'File too large: {file_size_mb:.1f}MB '
                        f'(max: {self.config.MAX_FILE_SIZE_MB}MB)'
            }

        # Open and check video
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return {
                'valid': False,
                'error': 'Cannot open video file'
            }

        try:
            # Get video metadata
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = total_frames / fps if fps > 0 else 0

            # Check duration
            if duration > self.config.MAX_VIDEO_DURATION:
                return {
                    'valid': False,
                    'error': f'Video too long: {duration:.1f}s '
                            f'(max: {self.config.MAX_VIDEO_DURATION}s)'
                }

            return {
                'valid': True,
                'metadata': {
                    'filename': video_path.name,
                    'size_mb': file_size_mb,
                    'duration': duration,
                    'fps': fps,
                    'resolution': (width, height),
                    'frame_count': total_frames
                }
            }

        finally:
            cap.release()

    @staticmethod
    def image_to_base64(image: Image.Image, format: str = 'JPEG', quality: int = 85) -> str:
        """
        Convert PIL Image to base64 string

        Args:
            image: PIL Image object
            format: Image format (JPEG, PNG, etc.)
            quality: JPEG quality (0-100)

        Returns:
            Base64 encoded string
        """
        buffer = io.BytesIO()
        image.save(buffer, format=format, quality=quality)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    @staticmethod
    def save_frame(
        image: Image.Image,
        output_path: str,
        format: str = 'JPEG',
        quality: int = 85
    ) -> Path:
        """
        Save frame to disk

        Args:
            image: PIL Image to save
            output_path: Output file path
            format: Image format
            quality: JPEG quality (0-100)

        Returns:
            Path to saved file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, format=format, quality=quality)
        return output_path

    def extract_and_save_frames(
        self,
        video_path: str,
        output_dir: str,
        prefix: str = 'frame',
        **kwargs
    ) -> List[Dict]:
        """
        Extract frames and save to disk with metadata

        Args:
            video_path: Path to input video
            output_dir: Directory to save frames
            prefix: Filename prefix for saved frames
            **kwargs: Additional arguments passed to extract_key_frames

        Returns:
            List of dicts with frame metadata and paths
        """
        # Extract frames
        frames = self.extract_key_frames(video_path, **kwargs)

        # Create output directory
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save frames and collect metadata
        frame_data = []
        for idx, (image, timestamp) in enumerate(frames):
            # Generate filename
            filename = f"{prefix}_{idx:03d}_{timestamp:.1f}s.jpg"
            filepath = output_dir / filename

            # Save frame
            self.save_frame(
                image,
                filepath,
                format=self.config.FRAME_FORMAT,
                quality=self.config.FRAME_QUALITY
            )

            # Collect metadata
            frame_data.append({
                'index': idx,
                'timestamp': timestamp,
                'filename': filename,
                'path': str(filepath),
                'size': filepath.stat().st_size,
                'image': image,
                'base64': self.image_to_base64(
                    image,
                    format=self.config.FRAME_FORMAT,
                    quality=self.config.FRAME_QUALITY
                )
            })

        return frame_data
