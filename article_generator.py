"""
Article generation using AI
"""
import os
import json
import anthropic
from models import (
    ArticleOutline, GeneratedArticle, SEOMetadata, 
    KeywordAnalysis, InternalLink, ExternalReference
)
from typing import List


class ArticleGenerator:
    """Generates SEO-optimized articles using Claude API"""
    
    def __init__(self):
        # API key should be set as environment variable
import google.generativeai as genai
genai.configure(api_key=...)
self.model = genai.GenerativeModel('gemini-pro')
    def generate_article(
        self, 
        topic: str, 
        outline: ArticleOutline,
        target_word_count: int,
        questions: List[str]
    ) -> GeneratedArticle:
        """Generate complete article with SEO optimization"""
        
        # Create detailed prompt for article generation
        prompt = self._create_article_prompt(topic, outline, target_word_count, questions)
        
        # Call Claude API
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse response
        response_text = message.content[0].text
        article_data = self._parse_article_response(response_text, topic, outline, target_word_count)
        
        return article_data
    
    def _create_article_prompt(
        self, 
        topic: str, 
        outline: ArticleOutline,
        target_word_count: int,
        questions: List[str]
    ) -> str:
        """Create comprehensive prompt for article generation"""
        
        sections_str = "\n".join([
            f"## {section['h2']}\n" + "\n".join([f"### {h3}" for h3 in section['h3']])
            for section in outline.sections
        ])
        
        prompt = f"""Generate a complete, SEO-optimized article about "{topic}".

OUTLINE:
# {outline.h1}

{sections_str}

REQUIREMENTS:
- Target word count: {target_word_count} words
- Write in a natural, engaging style (not robotic)
- Include primary keyword "{topic}" in the first paragraph
- Use proper HTML heading hierarchy (h1, h2, h3)
- Each section should be substantial and informative
- Include a FAQ section at the end answering: {', '.join(questions[:3])}

OUTPUT FORMAT (must be valid JSON):
{{
    "article_html": "Full HTML article with proper heading tags",
    "title_tag": "SEO title under 60 chars",
    "meta_description": "Meta description under 160 chars",
    "primary_keyword": "main keyword",
    "secondary_keywords": ["keyword1", "keyword2", "keyword3"],
    "internal_links": [
        {{"anchor_text": "text", "target_page": "suggested-page-topic", "context": "where it fits"}},
        ...3-5 suggestions
    ],
    "external_references": [
        {{"source_name": "Source", "url": "https://example.com", "context": "what to cite"}},
        ...2-4 authoritative sources
    ],
    "faq_html": "HTML FAQ section"
}}

Generate the article now as JSON only (no markdown code blocks):"""
        
        return prompt
    
    def _parse_article_response(
        self, 
        response: str, 
        topic: str,
        outline: ArticleOutline,
        target_word_count: int
    ) -> GeneratedArticle:
        """Parse Claude's response into structured article"""
        
        # Clean response and parse JSON
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            data = self._create_fallback_article(topic, outline, target_word_count)
        
        # Count words in article
        word_count = len(data['article_html'].split())
        
        # Calculate keyword density
        content_lower = data['article_html'].lower()
        primary_count = content_lower.count(data['primary_keyword'].lower())
        keyword_density = (primary_count / word_count * 100) if word_count > 0 else 0
        
        return GeneratedArticle(
            content=data['article_html'],
            outline=outline,
            seo_metadata=SEOMetadata(
                title_tag=data['title_tag'][:60],
                meta_description=data['meta_description'][:160]
            ),
            keyword_analysis=KeywordAnalysis(
                primary_keyword=data['primary_keyword'],
                secondary_keywords=data['secondary_keywords'],
                keyword_density=round(keyword_density, 2)
            ),
            internal_links=[
                InternalLink(**link) for link in data['internal_links']
            ],
            external_references=[
                ExternalReference(**ref) for ref in data['external_references']
            ],
            word_count=word_count,
            faq_section=data.get('faq_html')
        )
    
    def _create_fallback_article(self, topic: str, outline: ArticleOutline, target_word_count: int) -> dict:
        """Create fallback article if AI generation fails"""
        return {
            "article_html": f"<h1>{outline.h1}</h1><p>Article content for {topic}...</p>",
            "title_tag": f"{topic.title()} - Complete Guide",
            "meta_description": f"Learn everything about {topic}. Expert guide with tips and strategies.",
            "primary_keyword": topic,
            "secondary_keywords": [f"{topic} guide", f"{topic} tips", f"{topic} strategies"],
            "internal_links": [
                {"anchor_text": f"{topic} tools", "target_page": f"{topic}-tools", "context": "In tools section"}
            ],
            "external_references": [
                {"source_name": "Industry Report", "url": "https://example.com", "context": "Cite statistics"}
            ],
            "faq_html": "<h2>FAQ</h2><p>Common questions about " + topic + "</p>"
        }
