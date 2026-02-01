# AI-Powered Event Categorization

## Overview

The KRWL> event management system now includes AI-powered event categorization using a local Large Language Model (LLM). This feature intelligently categorizes scraped events into the appropriate schema categories, improving accuracy over simple keyword matching.

## Key Features

- **Local LLM Processing**: Uses Ollama to run LLMs locally (no external API calls)
- **Privacy-Preserving**: All data processing happens on your machine
- **Automatic Fallback**: Falls back to improved keyword-based categorization if AI is unavailable
- **Optional**: Can be enabled/disabled via configuration
- **60+ Categories**: Supports all event categories defined in the schema

## How It Works

### 1. Event Scraping
When events are scraped from sources:
```python
# In scraper.py
event = {
    'title': 'Rock Concert Tonight',
    'description': 'Live music performance...',
    # ... other fields
}
```

### 2. AI Categorization
The AI categorizer analyzes the event:
```python
# In ai_categorizer.py
category, confidence, method = categorizer.categorize_event(
    title="Rock Concert Tonight",
    description="Live music performance..."
)
# Result: ('music', 0.95, 'ai')
```

### 3. Fallback to Keywords
If AI is unavailable, uses improved keyword matching:
```python
# Keyword matching with scoring
category, confidence, method = categorizer.categorize_event(...)
# Result: ('music', 0.75, 'keyword')
```

## Installation & Setup

### Prerequisites
- Python 3.x
- Ollama (for AI categorization)

### Install Ollama

**macOS / Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download installer from https://ollama.ai/

### Pull Required Model
```bash
ollama pull llama3.2
```

**Recommended Models:**
- `llama3.2` - Fast, efficient, good for categorization (default)
- `llama3.1` - Larger, more capable
- `mistral` - Alternative efficient model

### Enable in Configuration

Edit `config.json`:
```json
{
  "ai": {
    "categorization": {
      "enabled": true
    },
    "ollama": {
      "host": "http://localhost:11434",
      "model": "llama3.2",
      "timeout": 30
    }
  }
}
```

## Configuration Options

### AI Categorization Settings

| Option | Default | Description |
|--------|---------|-------------|
| `ai.categorization.enabled` | `false` | Enable/disable AI categorization |
| `ai.ollama.host` | `http://localhost:11434` | Ollama server URL |
| `ai.ollama.model` | `llama3.2` | LLM model to use |
| `ai.ollama.timeout` | `30` | Request timeout (seconds) |
| `ai.ollama.rate_limit.min_delay` | `0.5` | Min delay between requests |
| `ai.ollama.rate_limit.max_delay` | `2.0` | Max delay between requests |

## Testing

### Run Test Suite
```bash
cd /path/to/krwl.in
python3 tests/test_ai_categorization.py
```

### Test Output
```
============================================================
AI CATEGORIZATION TEST SUITE
============================================================

TEST 1: Keyword-Based Categorization (Fallback)
✓ Title: Rock Concert
  Expected: music, Got: music
  Method: keyword, Confidence: 0.75

[... more tests ...]

============================================================
TEST SUMMARY
============================================================
✓ PASS: Keyword Categorization
✓ PASS: AI Categorization
✓ PASS: Status Reporting

✓ All tests passed!
```

### Manual Testing

**Test with Scraper:**
```bash
# Enable AI categorization in config.json
python3 src/event_manager.py scrape

# Check logs for AI categorization messages:
# "AI categorized as 'music' (confidence: 0.95)"
```

**Test Categorizer Directly:**
```python
from pathlib import Path
from modules.ai_categorizer import AICategorizer
from modules.utils import load_config

config = load_config(Path("."))
categorizer = AICategorizer(config, Path("."))

# Test categorization
category, confidence, method = categorizer.categorize_event(
    "Python Workshop",
    "Learn Python programming basics"
)
print(f"Category: {category}, Method: {method}, Confidence: {confidence}")

# Check status
status = categorizer.get_status()
print(status)
```

## Supported Categories

The AI categorizer supports all 60+ event categories defined in `event_schema.py`:

### Performance & Stage
- on-stage, music, opera-house, theatre, concert

### Social & Community
- pub-games, festivals, community, social, meetup

### Learning & Skills
- workshops, school, education, training, seminar

### Shopping & Commerce
- shopping, market, bazaar, fair, trade-show

### Sports & Fitness
- sports, sports-field, swimming, fitness, athletics

### Arts & Culture
- arts, museum, gallery, exhibition, cultural

### Food & Drink
- food, restaurant, cafe, dining, culinary

... and many more (see `src/modules/event_schema.py` for full list)

## Architecture

### Components

1. **AICategorizer** (`src/modules/ai_categorizer.py`)
   - Main categorization logic
   - Handles AI and keyword fallback
   - Configuration management

2. **OllamaProvider** (`src/modules/smart_scraper/ai_providers/ollama.py`)
   - Ollama LLM integration
   - Event categorization prompts
   - Response parsing

3. **EventSchema** (`src/modules/event_schema.py`)
   - Schema integration
   - Category validation
   - Migration support

4. **EventScraper** (`src/modules/scraper.py`)
   - Automatic categorization during scraping
   - Integration with validation pipeline

### Data Flow

```
Event Scraped
    ↓
Check if category exists
    ↓ (no category)
AI Categorization Enabled?
    ↓ (yes)
Call Ollama LLM
    ↓ (success)
AI Category → Event
    ↓ (failure)
Keyword Fallback → Event
    ↓
Validate & Save
```

## Performance

### Categorization Speed

- **AI Mode**: ~1-3 seconds per event (depends on model and hardware)
- **Keyword Mode**: < 1ms per event

### Resource Usage

- **Memory**: ~500MB - 2GB (depends on model)
- **CPU**: Higher during categorization (especially without GPU)
- **Disk**: ~1-4GB for model storage

### Optimization Tips

1. **Use Smaller Models**: `llama3.2` is faster than `llama3.1`
2. **Batch Processing**: Scrape events in batches to amortize startup costs
3. **Rate Limiting**: Configured by default to prevent overload
4. **Cache Results**: Categories are saved with events (no re-categorization)

## Troubleshooting

### Ollama Not Available

**Error:**
```
Ollama not available - falling back to keyword categorization
```

**Solutions:**
1. Check Ollama is running: `ollama list`
2. Test connection: `curl http://localhost:11434/api/tags`
3. Start Ollama service
4. Verify port 11434 is not blocked

### Model Not Found

**Error:**
```
model 'llama3.2' not found
```

**Solution:**
```bash
ollama pull llama3.2
```

### Categorization Too Slow

**Solutions:**
1. Use smaller model: Change to `llama3.2` in config
2. Reduce timeout: Set `ai.ollama.timeout` to lower value
3. Disable AI: Set `ai.categorization.enabled` to `false`

### Low Confidence Scores

**Symptoms:**
- Categories seem incorrect
- Low confidence scores (< 0.5)

**Solutions:**
1. Review event titles/descriptions (may be ambiguous)
2. Try different model (e.g., `llama3.1` for better accuracy)
3. Check if category is in schema (`python3 src/event_manager.py categories`)

## Development

### Adding New Categories

1. **Update Event Schema** (`src/modules/event_schema.py`):
```python
EVENT_CATEGORIES = [
    # ... existing categories ...
    "new-category",
]

CATEGORY_ICON_MAP = {
    # ... existing mappings ...
    "new-category": "icon-name",
}
```

2. **Update Categorization Prompt** (`src/modules/smart_scraper/ai_providers/ollama.py`):
```python
def _build_categorization_prompt(self, text: str) -> str:
    return f"""...
    Available categories:
    - New Category Type: new-category
    ..."""
```

3. **Update Keyword Map** (`src/modules/ai_categorizer.py`):
```python
keyword_map = {
    # ... existing mappings ...
    'new-category': ['keyword1', 'keyword2'],
}
```

### Testing New Features

```python
# Add test case to tests/test_ai_categorization.py
test_events = [
    # ... existing tests ...
    ("New Event", "Description with new category", "new-category"),
]
```

## Best Practices

1. **Start with Keyword Fallback**: Test without AI first to ensure basic functionality
2. **Monitor Logs**: Check categorization accuracy in logs
3. **Review Results**: Manually verify categories for first few events
4. **Adjust Keywords**: Improve keyword map based on failures
5. **Update Regularly**: Keep Ollama and models updated

## Security & Privacy

- **No External APIs**: All processing happens locally
- **No Data Collection**: Event data never leaves your machine
- **Open Source**: Ollama and models are open source
- **Auditable**: All code is visible and can be reviewed

## License

This feature is part of the KRWL> project and follows the same license.

## Support

- **Issues**: https://github.com/feileberlin/krwl.in/issues
- **Ollama Docs**: https://ollama.ai/
- **Model List**: https://ollama.ai/library

## Credits

- **Ollama**: Local LLM runtime (https://ollama.ai/)
- **Llama**: Meta's open source LLM family
- **KRWL> Team**: Integration and implementation
