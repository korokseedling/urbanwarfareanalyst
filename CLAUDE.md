# Urban Warfare Analyst - Claude Instructions

## Project Overview

AI-powered tactical analysis system for urban warfare training videos using Google Gemini AI models. The system extracts key frames from training footage and provides detailed tactical analysis including:
- Soldier position identification and tracking
- Threat assessment (windows, doorways, corners)
- Tactical error detection and strength identification
- Formation analysis and scoring
- Training recommendations

**Purpose:** Enhance military training effectiveness through automated AI analysis of urban warfare exercises.

**Key Objectives:**
- Process 30-120 second training videos efficiently
- Extract 3 key frames at 25%, 50%, 75% positions
- Generate tactical annotations with bounding boxes
- Provide actionable feedback for training improvement

## Technology Stack

- **Language**: Python 3.x
- **Framework**: Jupyter Notebooks
- **AI Models**:
  - **Analysis**: Gemini 2.5 Flash Preview (`gemini-2.5-flash-preview-09-2025`)
  - **Image Generation**: Gemini 3 Pro Image Preview (`gemini-3-pro-image-preview`)
- **Key Dependencies**:
  - `opencv-python` - Video processing and frame extraction
  - `Pillow` (PIL) - Image manipulation and resizing
  - `google-generativeai` - Gemini API integration
  - `numpy` - Numerical operations
  - `python-dotenv` - Environment variable management
  - `ipywidgets` - Interactive Jupyter widgets
  - `aiohttp` - Async HTTP requests for API calls

## Code Style & Conventions

- Follow PEP 8 Python style guidelines
- Use descriptive variable and function names (e.g., `extract_key_frames`, `video_metadata`)
- Add docstrings to all classes and functions
- Use type hints where applicable
- Keep configuration centralized in `config.py`
- Store sensitive data (API keys) in `.env` file
- Use emojis in console output for better UX (✅ ❌ 📊 🎥 etc.)
- Maintain separation of concerns: extraction → analysis → summary

## Project Structure

```
Urban Warfare Analyst/
├── 01_frame_extraction_demo.ipynb       # ✅ Stage 1: Frame extraction
├── 02_frame_analysis_demo.ipynb         # ✅ Stage 2: AI analysis
├── 03_performance_summary_demo.ipynb    # ⏳ Stage 3: Summary generation (pending)
├── config.py                            # ✅ Central configuration
├── frame_extractor.py                   # ✅ Frame extraction logic
├── requirements.txt                     # ✅ Python dependencies
├── .env                                 # ✅ Environment variables (API keys)
├── .env.example                         # ✅ Template for .env
├── prompts/
│   ├── frame_analysis.txt              # ✅ Stage 2 analysis prompt
│   └── performance_summary.txt         # ✅ Stage 3 summary prompt
├── Training Footage/
│   └── urban_warfare_training.mp4      # ✅ Test video (37.7s, 6.6MB)
└── outputs/
    └── urban_warfare_training/
        └── frames/                      # ✅ Extracted frames
            ├── key_frame_000_9.4s.jpg  # Frame at 25%
            ├── key_frame_001_18.9s.jpg # Frame at 50%
            └── key_frame_002_28.3s.jpg # Frame at 75%
```

## Development Workflow

### Initial Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Running the project
```bash
# Stage 1: Frame Extraction
jupyter notebook 01_frame_extraction_demo.ipynb

# Or execute from command line
jupyter nbconvert --to notebook --execute 01_frame_extraction_demo.ipynb

# Stage 2: AI Analysis (requires GEMINI_API_KEY)
jupyter notebook 02_frame_analysis_demo.ipynb

# Stage 3: Performance Summary (requires completed Stage 2)
jupyter notebook 03_performance_summary_demo.ipynb
```

### Configuration
Edit `config.py` or `.env` to adjust:
- `GEMINI_ANALYSIS_MODEL` - Model for frame analysis (default: `gemini-2.5-flash-preview-09-2025`)
- `GEMINI_IMAGE_MODEL` - Model for overlay generation (default: `gemini-3-pro-image-preview`)
- `GEMINI_MODEL` - Default/fallback model (default: `gemini-2.5-flash-preview-09-2025`)
- `TEMPERATURE` - Model creativity (0.0-1.0, default: 0.7)
- `NUM_FRAMES` - Number of frames to extract (default: 3)
- `FRAME_RESIZE_MAX` - Max frame dimension in pixels (default: 720)
- `MAX_VIDEO_DURATION` - Max video length in seconds (default: 120)

### Testing
```bash
# Test with sample video
python3 -c "from frame_extractor import FrameExtractor; from config import config; e = FrameExtractor(config); print(e.validate_video('./Training Footage/urban_warfare_training.mp4'))"

# Verify API key and model configuration
python3 -c "from config import config; config.print_config()"

# Test model availability (verifies API key works with both models)
python3 verify_config.py
```

## Implementation Plan

### **Stage 1: Key Frame Extraction** ✅ COMPLETED
**Status:** Fully implemented and tested (2025-12-10)
- [x] Video validation (format, size, duration, resolution)
- [x] Extract 3 key frames at 25%, 50%, 75% positions
- [x] Resize frames to ≤720px max dimension
- [x] Generate frame timestamps
- [x] Base64 encode frames for API transmission
- [x] Save frames to disk for verification
- [x] Display frames in notebook
- [x] Updated to use Gemini 2.5 Flash model
- **Completion Date:** December 10, 2025
- **Test Video:** urban_warfare_training.mp4 (37.7s, 6.6MB, 1280x720)
- **Output:** 3 frames (156.5 KB total base64)

### **Stage 2: Frame Analysis & Annotation** ✅ COMPLETED
**Status:** Fully implemented and tested (2025-12-29)
- [x] Load extracted frames and metadata
- [x] Send frames to Gemini 2.5 Flash API with tactical analysis prompt
- [x] Parse structured JSON response with:
  - Soldier positions (bounding boxes)
  - Threat identification (windows, doorways, corners)
  - Tactical errors and strengths
  - Formation assessment
  - Frame-level scores (0-100)
- [x] Generate annotated frames with overlays using Gemini 3 Pro Image Model
- [x] Display side-by-side comparison (original vs annotated)
- [x] Export annotated frames to disk
- [x] Handle API errors and rate limiting
- **Completion Date:** December 29, 2025
- **Dependencies:** GEMINI_API_KEY configured and working

### **Stage 3: Performance Summary** ⏳ PENDING
**Status:** Not started
- [ ] Aggregate analysis from all frames
- [ ] Calculate overall performance score
- [ ] Generate category scores:
  - Positioning (0-100)
  - Threat Awareness (0-100)
  - Formation Quality (0-100)
  - Communication (0-100)
- [ ] Identify top 3 strengths
- [ ] Identify top 3 areas for improvement
- [ ] Generate training recommendations
- [ ] Export summary report (JSON + human-readable)
- [ ] Visualize scores with charts
- **Target Runtime:** <10 seconds

## Domain-Specific Guidelines

### Tactical Analysis Focus Areas
- **Soldier Positioning:** Cover, concealment, angles of fire, mutual support
- **Threat Assessment:** Windows, doors, corners, high ground, blind spots
- **Formation Quality:** Spacing, overlapping sectors, communication distance
- **Movement Techniques:** Bounding overwatch, covering fire, room entry
- **Cover & Concealment:** Proper use of terrain and structures
- **Muzzle Awareness:** Direction of fire, flagging prevention

### Military Terminology
- Use standard military terminology (e.g., "fire team", "stack", "breach", "clear")
- Reference doctrinal formations (wedge, file, line, staggered column)
- Apply tactical principles (speed/surprise/violence of action, 3-5 second rush)
- Consider MOUT (Military Operations in Urban Terrain) best practices

### Scoring Criteria
- **90-100:** Textbook execution, minimal errors
- **70-89:** Solid performance, minor improvements needed
- **50-69:** Acceptable with notable deficiencies
- **Below 50:** Significant tactical errors, requires remedial training

## Important Notes

### API Configuration
- **API Key**: Set `GEMINI_API_KEY` in `.env` file (billing must be enabled)
- **Models Used**:
  - **Stage 2 Analysis**: `gemini-2.5-flash-preview-09-2025` (September 2025 preview)
    - Fast multimodal model for tactical frame analysis
    - Optimized for speed and efficiency
  - **Stage 3 Overlays**: `gemini-3-pro-image-preview` (also known as "Nano Banana Pro")
    - Image generation and editing model
    - Creates annotated tactical overlay images
- **Model Specifications**:
  - Gemini 2.5 Flash: Fast inference, good for text/image analysis
  - Gemini 3 Pro Image: Specialized for image generation/editing tasks
- **Environment Variable**: `GEMINI_API_KEY` or `GOOGLE_API_KEY` (if both set, `GOOGLE_API_KEY` takes precedence)

### Performance Optimization
- **Frames resized** to 720px max to reduce API latency (~40% improvement)
- **Base64 encoding** used for direct API transmission
- **Model selection**: Fast Gemini 2.5 Flash for analysis, specialized Pro Image for overlays
- **Parallel processing** for multiple frames (Stage 2)
- **Async API calls** to reduce total processing time
- **Stage-specific models** ensure optimal performance and cost efficiency

### Known Limitations
- Maximum video duration: 120 seconds
- Maximum file size: 100 MB
- Supported formats: MP4, MOV, AVI, MKV, WMV
- Frame extraction positions are fixed at 25%, 50%, 75%
- Currently uses percentage-based extraction (not event-based)

### Next Actions
1. **✅ Completed:** API key configured and models tested
2. **✅ Completed:** Model configuration updated with stage-specific models
3. **✅ Completed:** Stage 2 (Frame Analysis) notebook with Gemini 2.5 Flash
4. **Next:** Implement Stage 3 (Performance Summary) with overlay generation
5. **Future:** Add event-based frame extraction (detect significant tactical moments)

---
*Last updated: 2025-12-29*
*Stage 1 and Stage 2 completed. Ready for Stage 3 implementation.*
