# SEO Article Generation System

An intelligent agent-based system that generates SEO-optimized articles by analyzing search engine results and producing high-quality, keyword-optimized content.

## Quick Start

```bash
# 1. Generate all project files
python3 generate_project.py

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set API key
export ANTHROPIC_API_KEY='your-key'

# 4. Generate an article
python main.py generate "best productivity tools for remote teams"
```

## Features

✅ SERP Analysis - Analyzes top 10 search results  
✅ AI-Powered Writing - Uses Claude for natural content  
✅ SEO Optimization - Proper keywords, meta tags, structure  
✅ Job Persistence - SQLite tracking with resume capability  
✅ Link Suggestions - Internal/external linking recommendations  
✅ FAQ Generation - Auto-generated FAQ sections  
✅ Full Test Coverage - Comprehensive test suite

## Commands

```bash
# Generate article
python main.py generate "topic" [--word-count 1500] [--output file.json]

# Check job status
python main.py status <job-id>

# Resume failed job
python main.py resume <job-id>

# List jobs
python main.py list

# Run tests
pytest test_seo_agent.py -v
```

## Project Structure

```
├── models.py              # Pydantic data models
├── serp_analyzer.py       # SERP analysis
├── article_generator.py   # AI content generation
├── job_manager.py         # Job persistence
├── seo_agent.py           # Main orchestrator
├── main.py                # CLI interface
├── test_seo_agent.py      # Tests
└── requirements.txt       # Dependencies
```

## Output Format

Each generated article includes:
- Full HTML content with proper heading hierarchy
- SEO metadata (title, description)
- Keyword analysis with density tracking
- 3-5 internal link suggestions
- 2-4 external reference suggestions
- Auto-generated FAQ section
- Word count and validation

## Architecture

The system follows a modular design:
1. **SERPAnalyzer** - Fetches and analyzes search results
2. **ArticleGenerator** - Uses Claude API to create content
3. **JobManager** - Handles persistence and tracking
4. **SEOAgent** - Orchestrates the entire process

## Testing

Run tests:
```bash
pytest test_seo_agent.py -v
```

Tests cover:
- SERP data fetching
- Job persistence
- SEO validation
- End-to-end generation (requires API key)

## Extending

### Add Real SERP API

Replace mock implementation in `serp_analyzer.py`:

```python
def get_serp_data(self, query: str) -> SERPData:
    import requests
    response = requests.get(
        "https://serpapi.com/search",
        params={"q": query, "api_key": os.environ["SERP_API_KEY"]}
    )
    # Parse and return results
```

### Add Content Quality Scoring

```python
class ContentQualityScorer:
    def score_article(self, article: GeneratedArticle) -> float:
        score = 0.0
        if 1.0 <= article.keyword_analysis.keyword_density <= 3.0:
            score += 25
        # Add more scoring criteria
        return score
```

## Troubleshooting

**No API key found**
```bash
export ANTHROPIC_API_KEY='your-key'
```

**Job not found**  
Check `jobs.db` in current directory

**Generation failed**  
Check error with `python main.py status <job-id>`

## License

MIT