# Deploying to Vercel

This guide explains how to deploy the Urban Warfare Training Analysis Viewer to Vercel.

## Prerequisites

- GitHub account with the repository pushed
- Vercel account (free tier works fine)
- Repository URL: https://github.com/korokseedling/urbanwarfareanalyst

## Deployment Steps

### Option 1: Deploy via Vercel Website (Recommended)

1. **Go to Vercel**
   - Visit https://vercel.com/
   - Sign in with your GitHub account

2. **Import Project**
   - Click "Add New..." → "Project"
   - Select "Import Git Repository"
   - Choose `korokseedling/urbanwarfareanalyst` from your repositories

3. **Configure Project**
   - **Framework Preset:** Select "Other" (static site)
   - **Root Directory:** Leave as `.` (root)
   - **Build Command:** Leave empty (no build needed)
   - **Output Directory:** Leave empty (serves from root)

4. **Deploy**
   - Click "Deploy"
   - Wait 1-2 minutes for deployment to complete
   - Your site will be live at: `https://urbanwarfareanalyst.vercel.app` (or similar)

### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI globally
npm install -g vercel

# Navigate to project directory
cd "/Users/samuel.tan/Desktop/Other Projects/2025 Q4/Army AI Transformation/Urban Warfare Analyst"

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

## What Gets Deployed

The deployment includes:

- **`index.html`** - Main web interface (Training Analysis Viewer)
- **`icons/`** - Military-themed icons (army, binoculars, vest, helmet)
- **`outputs/`** - Demo training analysis outputs:
  - Tactical infographic
  - 3 original key frames
  - 3 AI-annotated frames with tactical overlays
- **Camouflage images** - Military theme assets

## Configuration Files

- **`vercel.json`** - Vercel deployment configuration
  - Static file serving
  - Cache headers for performance
  - Route configuration

- **`.gitignore`** - Updated to allow demo outputs
  - Blocks JSON files from outputs
  - Blocks video files
  - Allows image files for web deployment

## After Deployment

Once deployed, you'll have a live URL like:
- `https://urbanwarfareanalyst.vercel.app`
- `https://urbanwarfareanalyst-korokseedling.vercel.app`
- Or a custom domain you configure

### Features Available:

1. **Session Report** - Left sidebar with tactical analysis
   - Overall score (79.3/100)
   - Cover utilization statistics
   - Tactical errors and strengths
   - Training recommendations

2. **AI Footage Analysis** - Main viewer
   - Toggle between original and annotated frames
   - View tactical infographic
   - Interactive frame selection

3. **Training Personnel Details** - Bottom section
   - 6 soldier profiles with scores
   - Expandable tactical assessments
   - Individual performance feedback

## Updating the Deployment

To update the live site:

```bash
# Make changes to your code
# ...

# Commit and push to GitHub
git add .
git commit -m "Update description"
git push origin main

# Vercel will automatically redeploy!
```

Vercel automatically redeploys when you push to the `main` branch on GitHub.

## Custom Domain (Optional)

1. Go to your project settings on Vercel
2. Navigate to "Domains"
3. Add your custom domain
4. Update DNS records as instructed by Vercel

## Troubleshooting

### Images not loading?
- Check that all image paths in `index.html` are relative (no leading `/`)
- Verify images are committed to GitHub (check .gitignore)

### 404 errors?
- Ensure `index.html` exists in the root directory
- Check `vercel.json` routing configuration

### Deployment fails?
- Check Vercel build logs
- Ensure no build command is set (this is a static site)
- Verify all referenced files exist in the repository

## Performance Optimization

The site is already optimized with:
- Cache headers (1 hour)
- Compressed images
- Static file serving from Vercel's global CDN
- No JavaScript bundling needed

## Security Notes

- **No API keys are exposed** - All processing happens locally
- Training footage is not included in deployment
- Only demo outputs (images) are public
- Original `.env` file is never committed

---

**Live Demo:** Once deployed, your site will be accessible worldwide via HTTPS automatically!
