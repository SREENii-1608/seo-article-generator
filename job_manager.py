"""
Job management and persistence
"""
import sqlite3
import json
import uuid
from datetime import datetime
from typing import Optional
from models import GenerationJob, JobStatus, ArticleRequest, SERPData, GeneratedArticle


class JobManager:
    """Manages job persistence and tracking"""
    
    def __init__(self, db_path: str = "jobs.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                topic TEXT NOT NULL,
                target_word_count INTEGER,
                language TEXT,
                serp_data TEXT,
                article_data TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_job(self, request: ArticleRequest) -> GenerationJob:
        """Create a new generation job"""
        job_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        job = GenerationJob(
            job_id=job_id,
            status=JobStatus.PENDING,
            request=request,
            created_at=now,
            updated_at=now
        )
        
        self._save_job(job)
        return job
    
    def get_job(self, job_id: str) -> Optional[GenerationJob]:
        """Retrieve job by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM jobs WHERE job_id = ?
        """, (job_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return self._row_to_job(row)
    
    def update_job_status(self, job_id: str, status: JobStatus, error: Optional[str] = None):
        """Update job status"""
        job = self.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        job.status = status
        job.updated_at = datetime.utcnow()
        if error:
            job.error_message = error
        
        self._save_job(job)
    
    def save_serp_data(self, job_id: str, serp_data: SERPData):
        """Save SERP data to job"""
        job = self.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        job.serp_data = serp_data
        job.updated_at = datetime.utcnow()
        self._save_job(job)
    
    def save_article(self, job_id: str, article: GeneratedArticle):
        """Save generated article to job"""
        job = self.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        job.article = article
        job.status = JobStatus.COMPLETED
        job.updated_at = datetime.utcnow()
        self._save_job(job)
    
    def _save_job(self, job: GenerationJob):
        """Persist job to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        serp_json = json.dumps(job.serp_data.dict()) if job.serp_data else None
        article_json = json.dumps(job.article.dict()) if job.article else None
        
        cursor.execute("""
            INSERT OR REPLACE INTO jobs 
            (job_id, status, topic, target_word_count, language, serp_data, 
             article_data, error_message, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job.job_id,
            job.status.value,
            job.request.topic,
            job.request.target_word_count,
            job.request.language,
            serp_json,
            article_json,
            job.error_message,
            job.created_at.isoformat(),
            job.updated_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _row_to_job(self, row) -> GenerationJob:
        """Convert database row to GenerationJob"""
        (job_id, status, topic, word_count, language, serp_json, 
         article_json, error, created, updated) = row
        
        request = ArticleRequest(
            topic=topic,
            target_word_count=word_count,
            language=language
        )
        
        serp_data = SERPData(**json.loads(serp_json)) if serp_json else None
        article = GeneratedArticle(**json.loads(article_json)) if article_json else None
        
        return GenerationJob(
            job_id=job_id,
            status=JobStatus(status),
            request=request,
            serp_data=serp_data,
            article=article,
            error_message=error,
            created_at=datetime.fromisoformat(created),
            updated_at=datetime.fromisoformat(updated)
        )
    
    def list_jobs(self, limit: int = 10) -> list:
        """List recent jobs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT job_id, status, topic, created_at 
            FROM jobs 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "job_id": row[0],
                "status": row[1],
                "topic": row[2],
                "created_at": row[3]
            }
            for row in rows
        ]
