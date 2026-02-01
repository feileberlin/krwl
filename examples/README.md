# Examples

This directory contains example scripts demonstrating various features of the KRWL> Events from here til sunrise system.

## Available Examples

### AI Categorization Demo (`ai_categorization_demo.py`)

Demonstrates the AI-powered event categorization feature.

**Run:**
```bash
python3 examples/ai_categorization_demo.py
```

**Shows:**
- Keyword-based categorization (always works)
- AI-powered categorization (if Ollama available)
- Categorizer status information

**Requirements:**
- Python 3.x
- Ollama (optional, for AI categorization)

**See also:** `docs/AI_CATEGORIZATION.md` for full documentation

## Adding New Examples

When adding new examples:
1. Create executable Python script in this directory
2. Add shebang: `#!/usr/bin/env python3`
3. Make executable: `chmod +x examples/your_example.py`
4. Add documentation to this README
5. Test the example works standalone
