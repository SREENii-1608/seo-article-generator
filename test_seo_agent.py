"""
Tests for SEO article generation system
"""
import pytest
import os
import tempfile
from models import ArticleRequest, JobStatus
from seo_agent import SEOAgent
from serp_analyzer import SERPAnalyzer
from job_manager import JobManager


class TestSERPAnalyzer:
    """Test SERP analysis functionality"""
    
    def test_get_serp_data(self):
        analyzer = SERPAnalyzer()
        serp_data = analyzer.get_serp_data("best productivity tools")
        
        assert serp_data.query == "best productivity tools"
        assert len(serp_data.results) == 10
        assert all(r.rank > 0 for r in serp_data.results)
    
    def test_extract_themes(self):
        analyzer = SERPAnalyzer()
        serp_data = analyzer.get_serp_data("remote work strategies")
        themes = analyzer.extract_themes(serp_data)
        
        assert isinstance(themes, dict)
        assert len(themes) > 0
    
    def test_generate_outline(self):
        analyzer = SERPAnalyzer()
        serp_data = analyzer.get_serp_data("email marketing tips")
        themes = analyzer.extract_themes(serp_data)
        outline = analyzer.generate_outline(serp_data, themes)
        
        assert outline.h1
        assert len(outline.sections) > 0
        assert all('h2' in s and 'h3' in s for s in outline.sections)
    
    def test_extract_questions(self):
        analyzer = SERPAnalyzer()
        serp_data = analyzer.get_serp_data("content marketing")
        questions = analyzer.extract_questions(serp_data)
        
        assert len(questions) > 0
        assert all('?' in q for q in questions)


class TestJobManager:
    """Test job persistence"""
    
    def test_create_and_retrieve_job(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            db_path = tmp.name
        
        try:
            manager = JobManager(db_path)
            request = ArticleRequest(topic="test topic", target_word_count=1000)
            
            job = manager.create_job(request)
            assert job.job_id
            assert job.status == JobStatus.PENDING
            
            retrieved = manager.get_job(job.job_id)
            assert retrieved.job_id == job.job_id
            assert retrieved.request.topic == "test topic"
        finally:
            os.unlink(db_path)
    
    def test_update_job_status(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            db_path = tmp.name
        
        try:
            manager = JobManager(db_path)
            request = ArticleRequest(topic="test")
            job = manager.create_job(request)
            
            manager.update_job_status(job.job_id, JobStatus.RUNNING)
            updated = manager.get_job(job.job_id)
            assert updated.status == JobStatus.RUNNING
        finally:
            os.unlink(db_path)
    
    def test_list_jobs(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            db_path = tmp.name
        
        try:
            manager = JobManager(db_path)
            
            # Create multiple jobs
            for i in range(3):
                request = ArticleRequest(topic=f"topic {i}")
                manager.create_job(request)
            
            jobs = manager.list_jobs()
            assert len(jobs) == 3
        finally:
            os.unlink(db_path)


class TestSEOValidation:
    """Test SEO criteria validation"""
    
    def test_title_tag_length(self):
        from models import SEOMetadata
        
        # Valid title
        metadata = SEOMetadata(
            title_tag="Test Title",
            meta_description="Test description"
        )
        assert len(metadata.title_tag) <= 60
        
        # Title too long should be truncated or raise error
        with pytest.raises(Exception):
            SEOMetadata(
                title_tag="x" * 70,
                meta_description="Test"
            )
    
    def test_meta_description_length(self):
        from models import SEOMetadata
        
        # Valid description
        metadata = SEOMetadata(
            title_tag="Test",
            meta_description="Short description"
        )
        assert len(metadata.meta_description) <= 160
        
        # Description too long
        with pytest.raises(Exception):
            SEOMetadata(
                title_tag="Test",
                meta_description="x" * 170
            )
    
    def test_article_structure(self):
        """Test that generated articles have proper structure"""
        from models import ArticleOutline
        
        outline = ArticleOutline(
            h1="Main Heading",
            sections=[
                {"h2": "Section 1", "h3": ["Sub 1", "Sub 2"]},
                {"h2": "Section 2", "h3": ["Sub 3"]}
            ]
        )
        
        assert outline.h1
        assert len(outline.sections) == 2
        assert all('h2' in s for s in outline.sections)


class TestEndToEnd:
    """End-to-end integration tests"""
    
    @pytest.mark.skipif(
        not os.environ.get("ANTHROPIC_API_KEY"),
        reason="Requires ANTHROPIC_API_KEY"
    )
    def test_complete_article_generation(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            db_path = tmp.name
        
        try:
            agent = SEOAgent(db_path)
            request = ArticleRequest(
                topic="digital marketing strategies",
                target_word_count=800
            )
            
            job = agent.generate_article(request)
            
            assert job.status == JobStatus.COMPLETED
            assert job.article is not None
            assert job.article.word_count > 0
            assert job.article.seo_metadata.title_tag
            assert len(job.article.internal_links) >= 3
            assert len(job.article.external_references) >= 2
        finally:
            os.unlink(db_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
