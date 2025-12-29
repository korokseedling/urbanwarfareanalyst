# Prompt Templates

This directory contains prompt templates for the AI Urban Warfare Analyst system.

## Files

### `frame_analysis.txt`
**Stage:** 2 - Frame Analysis
**Purpose:** Analyzes individual video frames for tactical elements
**Model:** Gemini 2.5 Flash (vision-capable)

**Variables:**
- `{timestamp}` - Frame timestamp in seconds
- `{context}` - Exercise scenario description

**Output:** JSON with soldier positions, threats, tactical errors, and score

---

### `performance_summary.txt`
**Stage:** 3 - Performance Summary
**Purpose:** Generates comprehensive performance report from all frame analyses
**Model:** Gemini 2.5 Flash

**Variables:**
- `{exercise_data}` - Metadata about the exercise
- `{frame_analyses}` - Array of all frame analysis results

**Output:** JSON with overall scores, metrics, recommendations

---

## Usage

### In Python/Jupyter:

```python
from pathlib import Path

# Load prompt template
prompts_dir = Path('./prompts')
with open(prompts_dir / 'frame_analysis.txt', 'r') as f:
    prompt_template = f.read()

# Fill in variables
prompt = prompt_template.format(
    timestamp=5.0,
    context="Room clearing exercise in 3-story building"
)

# Send to LLM
response = model.generate(prompt, image=frame)
```

### In Production Code:

```python
from config import Config

# Prompts directory is configured
prompts_dir = Config.PROMPTS_DIR

# Load and format prompt
def load_prompt(template_name, **kwargs):
    with open(prompts_dir / f'{template_name}.txt', 'r') as f:
        template = f.read()
    return template.format(**kwargs)

# Usage
prompt = load_prompt('frame_analysis',
                     timestamp=5.0,
                     context="Room clearing exercise")
```

---

## Prompt Engineering Notes

- Keep prompts focused and structured
- Use JSON output format for easy parsing
- Include clear scoring criteria
- Specify coordinate systems when needed
- Request only valid JSON (no markdown formatting)
- Include examples if needed for complex tasks

---

## Version Control

When modifying prompts:
1. Document changes in git commit message
2. Test with sample data before deployment
3. Consider backwards compatibility with existing analyses
4. Update this README if new variables are added
