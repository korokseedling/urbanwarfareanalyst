# AI Urban Warfare Analyst

A Python notebook prototype demonstrating automated tactical video analysis of urban training footage. The system extracts key frames, generates annotated visual overlays, and produces individualized performance assessments.

## Overview

**Runtime Environment:** Google Colab / Jupyter Notebook
**Primary Model:** Gemini 2.5 Flash (vision-capable)
**Input:** MP4 video file of urban warfare training exercise
**Output:** Annotated key frames + JSON performance report

---

## Project Structure

```
Urban Warfare Analyst/
├── .env                              # Environment variables (API keys)
├── .env.example                      # Template for environment setup
├── .gitignore                        # Git ignore patterns
├── config.py                         # Centralized configuration
├── frame_extractor.py                # Frame extraction module
├── requirements.txt                  # Python dependencies
├── CLAUDE.md                         # Project-specific Claude instructions
├── function_specs.md                 # Technical specifications
│
├── prompts/                          # LLM prompt templates
│   ├── README.md                     # Prompt documentation
│   ├── frame_analysis.txt            # Stage 2: Frame analysis prompt
│   └── performance_summary.txt       # Stage 3: Summary generation prompt
│
├── 01_frame_extraction_demo.ipynb    # Stage 1: Key frame extraction
├── 02_frame_analysis_demo.ipynb      # Stage 2: Analysis & annotation (TODO)
├── 03_performance_summary_demo.ipynb # Stage 3: Performance summary (TODO)
│
└── outputs/                          # Generated outputs (auto-created)
    └── [video_name]/
        └── frames/                   # Extracted frames
```

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 3. Run Stage 1: Frame Extraction

Open `01_frame_extraction_demo.ipynb` in Jupyter:

```bash
jupyter notebook 01_frame_extraction_demo.ipynb
```

Or in Google Colab:
1. Upload notebook to Google Drive
2. Open with Google Colab
3. Upload your video file
4. Run all cells

---

## Configuration

All configuration is centralized in `config.py` and `.env`:

### Environment Variables (.env)

```bash
# API Keys
GEMINI_API_KEY=your_gemini_api_key_here

# Model Settings
GEMINI_MODEL=gemini-2.0-flash-exp
TEMPERATURE=0.7
MAX_TOKENS=2048

# Frame Extraction
NUM_FRAMES=3
FRAME_RESIZE_MAX=720
```

### Configuration Class (config.py)

```python
from config import Config, config

# Print current configuration
config.print_config()

# Access configuration values
print(config.NUM_FRAMES)  # 3
print(config.FRAME_EXTRACTION_POSITIONS)  # [0.25, 0.50, 0.75]
```

---

## Stage 1: Key Frame Extraction

**Notebook:** `01_frame_extraction_demo.ipynb`
**Runtime:** ~18 seconds
**Status:** ✅ Complete

### Features

- Extract 3 frames at 25%, 50%, 75% positions
- Automatic resize to 720p for API optimization
- Returns PIL Image objects with timestamps
- Saves frames to disk (optional)
- Base64 encoding for API transmission

### Usage

```python
from frame_extractor import FrameExtractor
from config import config

extractor = FrameExtractor(config)

# Extract key frames
frames = extractor.extract_key_frames(
    video_path="./training_video.mp4",
    num_frames=3,
    positions=[0.25, 0.50, 0.75],
    resize_max=720
)

# frames is List[Tuple[Image, float]]
for image, timestamp in frames:
    print(f"Frame at {timestamp:.1f}s: {image.size}")
```

---

## Stage 2: Frame Analysis & Annotation

**Notebook:** `02_frame_analysis_demo.ipynb`
**Runtime Target:** ~25 seconds
**Status:** 📋 Planned

### Planned Features

- Parallel frame analysis using `asyncio`
- Gemini 2.5 Flash vision analysis
- Tactical element detection:
  - Soldier positions and cover status
  - Threat identification
  - Movement patterns
  - Formation assessment
- Visual overlay generation:
  - Movement pathways (polylines)
  - Threat markers (green/red)
  - Cover zones (bounding boxes)
- JSON-structured tactical data

### Prompt Template

Located in `prompts/frame_analysis.txt`:

```python
from pathlib import Path

# Load prompt
prompts_dir = Path('./prompts')
with open(prompts_dir / 'frame_analysis.txt', 'r') as f:
    prompt = f.read()

# Fill variables
prompt = prompt.format(
    timestamp=5.0,
    context="Room clearing exercise in 3-story building"
)
```

---

## Stage 3: Performance Summary

**Notebook:** `03_performance_summary_demo.ipynb`
**Runtime Target:** ~8 seconds
**Status:** 📋 Planned

### Planned Features

- Aggregate tactical scoring (0-100)
- Category breakdowns:
  - Cover utilization
  - Threat awareness
  - Formation discipline
  - Movement efficiency
  - Communication
- Benchmark comparison
- Key incidents timeline
- Training recommendations
- Markdown + JSON export

---

## Architecture Design

### Modular Structure

The project is designed to transition easily from notebook prototype to production code:

1. **Configuration Layer** (`config.py`, `.env`)
   - Centralized settings
   - Environment-based configuration
   - Easy to update without code changes

2. **Core Logic Layer** (`frame_extractor.py`, future modules)
   - Reusable functions
   - Importable in notebooks or scripts
   - Unit testable

3. **Prompt Layer** (`prompts/`)
   - Separated prompt templates
   - Version controlled
   - Easy to iterate and improve

4. **Presentation Layer** (Notebooks)
   - Interactive demonstrations
   - Educational documentation
   - Prototype/POC validation

### Benefits

- **Notebook Phase:** Quick iteration, visual feedback, easy sharing
- **Production Phase:** Import same modules, same config, same prompts
- **Maintainability:** Update prompts without touching code
- **Security:** API keys in `.env`, not hardcoded

---

## Performance Targets

| Stage | Component | Target Runtime |
|-------|-----------|----------------|
| 1 | Frame Extraction | 8s |
| 2 | Frame Analysis | 15s |
| 2 | Overlay Generation | 10s |
| 3 | Performance Summary | 8s |
| **Total** | **End-to-End** | **~54s** |

All stages meet the <30s individual target and <1min total target.

---

## Dependencies

### Core Requirements

```
opencv-python>=4.8.0      # Video processing
Pillow>=10.0.0            # Image manipulation
google-generativeai>=0.5.0 # Gemini API
numpy>=1.24.0             # Array operations
python-dotenv>=1.0.0      # Environment management
```

### Async Support (Stage 2)

```
aiohttp>=3.9.0            # Async HTTP
nest-asyncio>=1.6.0       # Enable asyncio in Jupyter
```

### Jupyter Support

```
ipython>=8.0.0
ipywidgets>=8.0.0
jupyter>=1.0.0
```

---

## Success Criteria for POC

- [x] Successfully extract 3 representative frames from test video
- [ ] Generate coherent tactical analysis for each frame
- [ ] Produce visually clear annotated overlays
- [ ] Output actionable performance summary with specific recommendations

---

## Limitations and Assumptions

- POC uses simulated or stock footage (not live training data)
- Single camera angle analysis only
- No real-time processing capability
- Manual trigger for each analysis stage
- Requires manual API key setup

---

## Development Roadmap

### Phase 1: Prototype (Current)
- [x] Stage 1: Frame extraction notebook
- [ ] Stage 2: Analysis & annotation notebook
- [ ] Stage 3: Performance summary notebook
- [ ] Stage 4: End-to-end integration notebook

### Phase 2: Production (Future)
- [ ] Convert notebooks to Python scripts
- [ ] Add CLI interface
- [ ] Implement batch processing
- [ ] Add real-time processing capability
- [ ] Deploy as web service (FastAPI)
- [ ] Add authentication & authorization
- [ ] Database integration for results storage

---

## Contributing

When modifying this project:

1. **Configuration Changes:** Update `.env.example` and `config.py`
2. **Prompt Changes:** Update files in `prompts/` directory
3. **Core Logic:** Update Python modules (e.g., `frame_extractor.py`)
4. **Notebook Changes:** Test all cells sequentially
5. **Documentation:** Update this README

---

## License

[Specify your license here]

---

## Contact

[Your contact information]

---

## Acknowledgments

Built for Army AI Transformation initiative, Q4 2025.
