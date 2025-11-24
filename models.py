"""
Data models for SEO article generation system
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SERPResult(BaseModel):
    """Individual search result"""
    rank: int
    url: str
    title: str
    snippet: str


class SERPData(BaseModel):
    """Collection of search results"""
    query: str
    results: List[SERPResult]
    
    
class KeywordAnalysis(BaseModel):
    """Keywords identified and used in the article"""
    primary_keyword: str
    secondary_keywords: List[str]
    keyword_density: float = Field(description="Percentage of primary keyword usage")


class InternalLink(BaseModel):
    """Suggested internal link"""
    anchor_text: str
    target_page: str
    context: str = Field(description="Where in the article this link makes sense")


class ExternalReference(BaseModel):
    """Authoritative external source to cite"""
    source_name: str
    url: str
    context: str = Field(description="What to cite and where")


class SEOMetadata(BaseModel):
    """SEO metadata for the article"""
    title_tag: str = Field(max_length=60)
    meta_description: str = Field(max_length=160)
    
    @validator('title_tag')
    def validate_title_length(cls, v):
        if len(v) > 60:
            raise ValueError('Title tag must be 60 characters or less')
        return v
    
    @validator('meta_description')
    def validate_description_length(cls, v):
        if len(v) > 160:
            raise ValueError('Meta description must be 160 characters or less')
        return v


class ArticleOutline(BaseModel):
    """Structured outline extracted from SERP analysis"""
    h1: str
    sections: List[dict] = Field(description="List of {h2: str, h3: List[str]}")


class GeneratedArticle(BaseModel):
    """Complete article output"""
    content: str = Field(description="Full HTML article content")
    outline: ArticleOutline
    seo_metadata: SEOMetadata
    keyword_analysis: KeywordAnalysis
    internal_links: List[InternalLink]
    external_references: List[ExternalReference]
    word_count: int
    faq_section: Optional[str] = None


class ArticleRequest(BaseModel):
    """Input parameters for article generation"""
    topic: str
    target_word_count: int = 1500
    language: str = "en"


class GenerationJob(BaseModel):
    """Job tracking model"""
    job_id: str
    status: JobStatus
    request: ArticleRequest
    serp_data: Optional[SERPData] = None
    article: Optional[GeneratedArticle] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
