"""
Main SEO article generation agent
"""
import logging
from models import ArticleRequest, GenerationJob, JobStatus
from serp_analyzer import SERPAnalyzer
from article_generator import ArticleGenerator
from job_manager import JobManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SEOAgent:
    """Main agent orchestrating the article generation process"""
    
    def __init__(self, db_path: str = "jobs.db"):
        self.serp_analyzer = SERPAnalyzer()
        self.article_generator = ArticleGenerator()
        self.job_manager = JobManager(db_path)
    
    def generate_article(self, request: ArticleRequest) -> GenerationJob:
        """
        Main entry point for article generation.
        Returns a job that can be tracked.
        """
        # Create job
        job = self.job_manager.create_job(request)
        logger.info(f"Created job {job.job_id} for topic: {request.topic}")
        
        try:
            # Step 1: Fetch and analyze SERP data
            self.job_manager.update_job_status(job.job_id, JobStatus.RUNNING)
            logger.info(f"Fetching SERP data for: {request.topic}")
            
            serp_data = self.serp_analyzer.get_serp_data(request.topic)
            self.job_manager.save_serp_data(job.job_id, serp_data)
            logger.info(f"SERP data fetched: {len(serp_data.results)} results")
            
            # Step 2: Extract themes and generate outline
            logger.info("Analyzing SERP themes...")
            themes = self.serp_analyzer.extract_themes(serp_data)
            outline = self.serp_analyzer.generate_outline(serp_data, themes)
            questions = self.serp_analyzer.extract_questions(serp_data)
            
            # Step 3: Generate article
            logger.info("Generating article with AI...")
            article = self.article_generator.generate_article(
                topic=request.topic,
                outline=outline,
                target_word_count=request.target_word_count,
                questions=questions
            )
            
            # Step 4: Save and complete
            self.job_manager.save_article(job.job_id, article)
            logger.info(f"Article generated successfully: {article.word_count} words")
            
            # Return updated job
            return self.job_manager.get_job(job.job_id)
            
        except Exception as e:
            logger.error(f"Error generating article: {str(e)}")
            self.job_manager.update_job_status(
                job.job_id, 
                JobStatus.FAILED, 
                error=str(e)
            )
            raise
    
    def resume_job(self, job_id: str) -> GenerationJob:
        """
        Resume a failed or interrupted job.
        If SERP data exists, skip that step.
        """
        job = self.job_manager.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        if job.status == JobStatus.COMPLETED:
            logger.info(f"Job {job_id} already completed")
            return job
        
        logger.info(f"Resuming job {job_id}")
        
        try:
            # If we have SERP data, skip to article generation
            if job.serp_data:
                logger.info("SERP data found, generating article...")
                themes = self.serp_analyzer.extract_themes(job.serp_data)
                outline = self.serp_analyzer.generate_outline(job.serp_data, themes)
                questions = self.serp_analyzer.extract_questions(job.serp_data)
                
                article = self.article_generator.generate_article(
                    topic=job.request.topic,
                    outline=outline,
                    target_word_count=job.request.target_word_count,
                    questions=questions
                )
                
                self.job_manager.save_article(job_id, article)
            else:
                # Start from scratch
                return self.generate_article(job.request)
            
            return self.job_manager.get_job(job_id)
            
        except Exception as e:
            logger.error(f"Error resuming job: {str(e)}")
            self.job_manager.update_job_status(job_id, JobStatus.FAILED, error=str(e))
            raise
    
    def get_job_status(self, job_id: str) -> GenerationJob:
        """Get current status of a job"""
        job = self.job_manager.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        return job
    
    def list_jobs(self, limit: int = 10) -> list:
        """List recent jobs"""
        return self.job_manager.list_jobs(limit)
