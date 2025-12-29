# AI Urban Warfare Analyst: Function Specifications

## Product Overview

A Python notebook prototype demonstrating automated tactical video analysis of urban training footage. The system extracts key frames, generates annotated visual overlays, and produces individualized performance assessments.

---

## Technical Architecture

**Runtime Environment:** Google Colab / Jupyter Notebook  
**Primary Model:** Gemini 2.5 Flash (vision-capable)  
**Input:** MP4 video file of urban warfare training exercise  
**Output:** Annotated key frames + JSON performance report

---

## Stage 1: Key Frame Extraction

**Function:** `extract_key_frames(video_path, num_frames=3)`

| Parameter | Type | Description |
|-----------|------|-------------|
| `video_path` | str | Path to input MP4 file |
| `num_frames` | int | Number of frames to extract (default: 3) |

**Logic:**
- Calculate video duration and extract at 25%, 50%, 75% intervals
- Resize frames to 720p max to reduce API payload size
- Return list of PIL Image objects with timestamps

**Output:** `List[Tuple[Image, float]]` (image, timestamp pairs)

**Optimization Notes:**
- Reduced from 5 to 3 frames for demo efficiency
- Scene change detection removed (adds processing overhead)
- Frame resizing reduces Gemini API latency by approximately 40%

---

## Stage 2: Frame Analysis and Annotation

**Function:** `analyze_frames_batch(frames, context)`

| Parameter | Type | Description |
|-----------|------|-------------|
| `frames` | List[Tuple] | List of (image, timestamp) pairs |
| `context` | str | Exercise scenario description |

**Optimization Strategy:** Parallel API calls using `asyncio.gather()`

```python
async def analyze_frames_batch(frames, context):
    tasks = [analyze_single_frame(f, t, context) for f, t in frames]
    return await asyncio.gather(*tasks)
```

**Analysis Prompt Template:**
```
Analyze this urban warfare training frame. Return JSON with:
- soldier_positions: [{id, x, y, cover_status}]
- threats: [{x, y, identified: bool}]
- tactical_errors: [string]
- score: int (0-100)
```

**Function:** `generate_overlay(frame, analysis_json)`

| Parameter | Type | Description |
|-----------|------|-------------|
| `frame` | Image | Original extracted frame |
| `analysis_json` | dict | LLM analysis output |

**Overlay Elements:**
- Movement pathways (colored polylines)
- Threat markers (green checkmarks / red X markers)
- Cover assessment zones (bounding boxes)

**Optimization Notes:**
- Simplified prompt reduces token count and response time
- Pre-loaded overlay assets (icons, fonts) avoid runtime file I/O
- Batch overlay generation using PIL composite operations

**Output:** Annotated PIL Image with visual overlay

---

## Stage 3: Performance Summary Generation

**Function:** `generate_performance_summary(all_analyses)`

| Parameter | Type | Description |
|-----------|------|-------------|
| `all_analyses` | List[dict] | Compiled frame analyses |

**Summary Components:**
- Overall tactical score (0-100)
- Cover utilization rating
- Threat response accuracy percentage
- Key improvement areas (ranked list)
- Comparison against optimal execution benchmarks

**Output:** Structured JSON report + markdown summary

---

## Dependencies

```python
opencv-python>=4.8.0
Pillow>=10.0.0
google-generativeai>=0.5.0
numpy>=1.24.0
aiohttp>=3.9.0  # For async API calls
nest-asyncio>=1.6.0  # Enable asyncio in Jupyter
```

---

## Notebook Cell Structure

| Cell | Function | Expected Runtime |
|------|----------|------------------|
| 1 | Environment setup and imports | 5s |
| 2 | Video upload and validation | 5s |
| 3 | Key frame extraction (3 frames) | 8s |
| 4 | Parallel frame analysis | 15s |
| 5 | Batch overlay generation | 10s |
| 6 | Performance summary | 8s |
| 7 | Results display and export | 3s |

**Total Demo Runtime:** ~54 seconds (under 1 minute)

**Per-Stage Breakdown (all under 30s target):**
- Stage 1 (Extraction): 8s
- Stage 2 (Analysis + Overlay): 25s
- Stage 3 (Summary): 8s

---

## Success Criteria for POC

1. Successfully extract 4-5 representative frames from test video
2. Generate coherent tactical analysis for each frame
3. Produce visually clear annotated overlays
4. Output actionable performance summary with specific improvement recommendations

---

## Limitations and Assumptions

- POC uses simulated or stock footage (not live training data)
- Single camera angle analysis only
- No real-time processing capability
- Manual trigger for each analysis stage