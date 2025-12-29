# Quick Start Guide

Get up and running with AI Urban Warfare Analyst in 5 minutes.

## Step 1: Install Dependencies (1 minute)

```bash
cd "/Users/samuel.tan/Desktop/Other Projects/2025 Q4/Army AI Transformation/Urban Warfare Analyst"
pip install -r requirements.txt
```

## Step 2: Configure API Key (1 minute)

1. Get your Gemini API key from: https://makersuite.google.com/app/apikey

2. Edit the `.env` file:
```bash
# Open .env in your editor
nano .env
# or
code .env
```

3. Replace `your_gemini_api_key_here` with your actual API key:
```
GEMINI_API_KEY=AIzaSy...your_actual_key_here
```

## Step 3: Prepare Your Video (1 minute)

Place your training video in the project directory or note its full path:

```bash
# Requirements:
# - Format: MP4, MOV, AVI, MKV, or WMV
# - Max size: 100MB
# - Max duration: 120 seconds
# - Resolution: Any (will be auto-resized to 720p)
```

## Step 4: Run Stage 1 Notebook (2 minutes)

### Option A: Jupyter Notebook

```bash
jupyter notebook 01_frame_extraction_demo.ipynb
```

Then:
1. Update `video_path` in Cell 2
2. Run All Cells (Cell → Run All)
3. View extracted frames

### Option B: Google Colab

1. Upload `01_frame_extraction_demo.ipynb` to Google Drive
2. Open with Google Colab
3. Upload your video file when prompted
4. Update `video_path` in Cell 2
5. Run All Cells

### Option C: JupyterLab

```bash
jupyter lab 01_frame_extraction_demo.ipynb
```

---

## Expected Output

After running the notebook, you should see:

1. **Configuration display** showing your settings
2. **Video validation** with metadata (duration, resolution, fps)
3. **Frame extraction** progress:
   - Frame at 25% (X.Xs)
   - Frame at 50% (Y.Ys)
   - Frame at 75% (Z.Zs)
4. **Preview of 3 frames** with timestamps
5. **Saved frames** in `outputs/[video_name]/frames/`

---

## Troubleshooting

### Issue: "GEMINI_API_KEY not set"

**Solution:** Make sure you edited `.env` file with your actual API key.

```bash
# Check your .env file
cat .env | grep GEMINI_API_KEY
```

### Issue: "Video validation failed"

**Possible causes:**
- File doesn't exist at specified path
- File format not supported
- File too large (>100MB)
- Video too long (>120s)

**Solution:** Check the error message and adjust video or path.

### Issue: "ModuleNotFoundError"

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: OpenCV cannot open video

**Solution:** Install ffmpeg:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from: https://ffmpeg.org/download.html
```

---

## Next Steps

After successfully running Stage 1:

1. **Review extracted frames** - Are they representative of the action?
2. **Adjust frame count** (optional) - Edit `NUM_FRAMES` in `.env`
3. **Wait for Stage 2** - Frame analysis notebook (coming soon)
4. **Wait for Stage 3** - Performance summary notebook (coming soon)

---

## Test with Sample Video

Don't have a training video yet? Use a sample:

```bash
# Download a sample video (Koala.mp4 in current directory)
# Or use any short video file for testing

video_path = "./Koala.mp4"
```

---

## Getting Help

- Check `README.md` for full documentation
- Review `function_specs.md` for technical details
- Check `config.py` for configuration options
- Review `prompts/README.md` for prompt documentation

---

**Estimated Total Time:** ~5 minutes from clone to first extracted frames!
