# Quick Start Guide

Get running in 5 minutes!

## Step 1: Generate Project Files

```bash
python3 generate_project.py
```

This creates all necessary files in the current directory.

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Or with virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 3: Set API Key

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Get your key from: https://console.anthropic.com/

## Step 4: Generate Your First Article

```bash
python main.py generate "best productivity tools for remote teams"
```

Done! Your article is generated and saved to the database.

## View Output

```bash
# Save to file
python main.py generate "your topic" --output article.json

# View the JSON
cat article.json
```

## Example Commands

```bash
# Generate with custom word count
python main.py generate "email marketing" --word-count 2000

# Check job status
python main.py status abc-123-def

# List all jobs
python main.py list

# Resume failed job
python main.py resume abc-123-def
```

## Run Tests

```bash
pytest test_seo_agent.py -v
```

## What You Get

Each article includes:
- ✅ Full HTML content
- ✅ SEO title & description
- ✅ Keyword analysis
- ✅ 3-5 internal link suggestions
- ✅ 2-4 external references
- ✅ FAQ section

## Troubleshooting

**"No module named 'pydantic'"**
```bash
pip install -r requirements.txt
```

**"ANTHROPIC_API_KEY not found"**
```bash
export ANTHROPIC_API_KEY='your-key'
```

**Tests failing**
```bash
# Skip tests requiring API key
pytest -v -k "not EndToEnd"
```

That's it! You're ready to generate SEO articles. 🚀