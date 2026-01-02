# AI Providers Guide

## Overview

The SmartScraper system supports multiple AI providers for intelligent event extraction from text and images. AI providers can extract structured event information from unstructured content, making scraping more reliable and flexible.

## Supported Providers

### Free/Rate-Limited Providers

#### 1. DuckDuckGo AI (Recommended for Free Use)
- **Cost**: Free
- **Rate Limits**: Moderate (configurable)
- **Models**: GPT-4O-mini equivalent
- **Best For**: General event extraction

**Configuration:**
```json
{
  "ai": {
    "default_provider": "duckduckgo",
    "duckduckgo": {
      "model": "gpt-4o-mini",
      "rate_limit": {
        "min_delay": 5.0,
        "max_delay": 15.0,
        "max_requests_per_session": 10
      }
    }
  }
}
```

#### 2. Bing AI/Copilot
- **Cost**: Free
- **Rate Limits**: Moderate
- **Best For**: Conversational event extraction

**Configuration:**
```json
{
  "ai": {
    "bing": {
      "conversation_style": "balanced",
      "rate_limit": {
        "min_delay": 5.0,
        "max_delay": 10.0,
        "max_requests_per_session": 8
      }
    }
  }
}
```

#### 3. Google Gemini
- **Cost**: Free tier available, then paid
- **Rate Limits**: Generous free tier
- **Models**: gemini-pro, gemini-pro-vision
- **Best For**: Complex event extraction, image analysis
- **Requires**: API key

**Configuration:**
```json
{
  "ai": {
    "google": {
      "model": "gemini-pro",
      "api_key": "YOUR_GOOGLE_API_KEY",
      "rate_limit": {
        "min_delay": 2.0,
        "max_delay": 5.0,
        "max_requests_per_session": 15
      }
    }
  }
}
```

**Get API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create new API key
3. Add to configuration

### Local Providers

#### 4. Ollama (Self-Hosted)
- **Cost**: Free (hardware costs only)
- **Rate Limits**: None (local)
- **Models**: llama3.2, mistral, etc.
- **Best For**: Privacy-focused, unlimited use
- **Requires**: Local Ollama installation

**Installation:**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull llama3.2
```

**Configuration:**
```json
{
  "ai": {
    "ollama": {
      "host": "http://localhost:11434",
      "model": "llama3.2",
      "rate_limit": {
        "min_delay": 0.5,
        "max_delay": 1.0,
        "max_requests_per_session": 50
      }
    }
  }
}
```

### Paid/Premium Providers

#### 5. OpenAI (Not Yet Implemented)
- **Cost**: Paid per token
- **Models**: GPT-4, GPT-3.5-turbo
- **Best For**: Highest quality extraction
- **Status**: Stub implementation

#### 6. Anthropic Claude (Not Yet Implemented)
- **Cost**: Paid per token
- **Models**: Claude 3 Opus, Sonnet, Haiku
- **Best For**: Long context, detailed analysis
- **Status**: Stub implementation

#### 7. Groq (Not Yet Implemented)
- **Cost**: Paid
- **Speed**: Extremely fast inference
- **Best For**: High-volume scraping
- **Status**: Stub implementation

## Configuration

### Default Provider

Set the default AI provider in the config:

```json
{
  "ai": {
    "default_provider": "duckduckgo"
  }
}
```

### Per-Source Provider Override

Override AI provider for specific sources:

```json
{
  "scraping": {
    "sources": [
      {
        "name": "Complex Events",
        "type": "html",
        "url": "https://example.com/events",
        "options": {
          "ai_provider": "google",
          "ai_prompt": "Custom extraction prompt..."
        }
      }
    ]
  }
}
```

### Custom AI Prompts

Provide custom prompts for better extraction:

```json
{
  "options": {
    "ai_prompt": "Extract event details. Focus on: 1) Exact dates and times, 2) Venue location with address, 3) Ticket prices if mentioned. Return as JSON."
  }
}
```

## Rate Limiting

### Configuration

All providers support rate limiting:

```json
{
  "rate_limit": {
    "min_delay": 5.0,           // Min seconds between requests
    "max_delay": 15.0,          // Max seconds between requests  
    "max_requests_per_session": 10  // Requests before rotation
  }
}
```

### Behavior

- **Random delays**: Between min_delay and max_delay
- **Session rotation**: After max_requests_per_session
- **Backoff**: Automatic backoff on rate limit errors
- **Retry logic**: Configurable retries per source

## Usage

### Text Extraction

AI providers extract structured event data from text:

**Input (unstructured):**
```
Join us for the Summer Music Festival on June 15-17, 2024
at Central Park. Tickets available at www.example.com
```

**Output (structured):**
```json
{
  "title": "Summer Music Festival",
  "start_time": "2024-06-15T18:00:00",
  "end_time": "2024-06-17T23:00:00",
  "location": {
    "name": "Central Park",
    "lat": 50.3167,
    "lon": 11.9167
  },
  "url": "https://www.example.com"
}
```

### Image Analysis

Extract events from poster/flyer images:

```python
from modules.smart_scraper import SmartScraper

scraper = SmartScraper(config, base_path)
event_data = scraper.analyze_image('event_poster.jpg')
```

## Best Practices

### 1. Start with Free Providers

Begin with DuckDuckGo or Bing for testing:
- No API keys required
- Generous rate limits
- Good quality

### 2. Use Local for Development

Ollama is perfect for development:
- No rate limits
- No API costs
- Full privacy

### 3. Upgrade for Production

Consider paid providers for production:
- Higher rate limits
- Better quality
- SLA guarantees

### 4. Monitor Usage

Track AI provider usage:
```bash
# Check logs for AI provider calls
grep "AI provider" logs/scraper.log

# Monitor rate limiting
grep "Rate limit" logs/scraper.log
```

### 5. Fallback Strategy

Configure multiple providers:
```json
{
  "ai": {
    "default_provider": "duckduckgo",
    "duckduckgo": {...},
    "ollama": {...}  // Fallback if DuckDuckGo unavailable
  }
}
```

## Troubleshooting

### Provider Not Available

```
⚠ AI providers not available (optional)
```

**Solution**: Install required packages:
```bash
# For DuckDuckGo (when library available)
pip install duckduckgo-ai

# For Google
pip install google-generativeai

# For Ollama
# Just ensure Ollama is running locally
```

### Rate Limit Errors

```
⚠ Rate limited, waiting 60s
```

**Solutions**:
- Increase delay times
- Reduce max_requests_per_session
- Switch to different provider
- Use local Ollama

### Poor Extraction Quality

**Solutions**:
- Use custom AI prompts
- Try different provider
- Provide more context in prompt
- Use image analysis instead of text

## Dependencies

### Required (Core)
- None (AI providers are optional)

### Optional (Per Provider)
```bash
# DuckDuckGo AI (when available)
pip install duckduckgo-ai

# Google Gemini
pip install google-generativeai

# Ollama (separate installation)
curl -fsSL https://ollama.com/install.sh | sh

# Future providers
pip install openai anthropic groq
```

## Examples

See `examples/config.smart_scraper.example.json` for complete configuration examples.

## Future Enhancements

- OpenAI integration
- Anthropic Claude integration
- Groq integration
- Custom model fine-tuning
- Batch processing
- Cost tracking
- Quality metrics

## Resources

- [Google AI Studio](https://makersuite.google.com/)
- [Ollama](https://ollama.com/)
- [OpenAI Platform](https://platform.openai.com/)
- [Anthropic](https://www.anthropic.com/)
