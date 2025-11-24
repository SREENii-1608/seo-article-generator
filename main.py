"""
CLI interface for SEO article generation
"""
import argparse
import json
import sys
from models import ArticleRequest
from seo_agent import SEOAgent


def main():
    parser = argparse.ArgumentParser(description="Generate SEO-optimized articles")
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate a new article')
    generate_parser.add_argument('topic', help='Article topic or primary keyword')
    generate_parser.add_argument('--word-count', type=int, default=1500, help='Target word count')
    generate_parser.add_argument('--language', default='en', help='Language code')
    generate_parser.add_argument('--output', '-o', help='Output file for article JSON')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check job status')
    status_parser.add_argument('job_id', help='Job ID to check')
    
    # Resume command
    resume_parser = subparsers.add_parser('resume', help='Resume a failed job')
    resume_parser.add_argument('job_id', help='Job ID to resume')
    
    # List command
    subparsers.add_parser('list', help='List recent jobs')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    agent = SEOAgent()
    
    if args.command == 'generate':
        request = ArticleRequest(
            topic=args.topic,
            target_word_count=args.word_count,
            language=args.language
        )
        
        print(f"\n🚀 Generating article for: {args.topic}")
        print(f"Target word count: {args.word_count}")
        print("-" * 60)
        
        job = agent.generate_article(request)
        
        print(f"\n✅ Article generated successfully!")
        print(f"Job ID: {job.job_id}")
        print(f"Status: {job.status.value}")
        
        if job.article:
            print(f"Word count: {job.article.word_count}")
            print(f"Primary keyword: {job.article.keyword_analysis.primary_keyword}")
            print(f"Keyword density: {job.article.keyword_analysis.keyword_density}%")
            print(f"\nSEO Metadata:")
            print(f"  Title: {job.article.seo_metadata.title_tag}")
            print(f"  Description: {job.article.seo_metadata.meta_description}")
            
            # Save to file if requested
            if args.output:
                output_data = {
                    "job_id": job.job_id,
                    "topic": job.request.topic,
                    "article": job.article.dict()
                }
                with open(args.output, 'w') as f:
                    json.dump(output_data, f, indent=2, default=str)
                print(f"\n💾 Article saved to: {args.output}")
    
    elif args.command == 'status':
        job = agent.get_job_status(args.job_id)
        print(f"\nJob ID: {job.job_id}")
        print(f"Topic: {job.request.topic}")
        print(f"Status: {job.status.value}")
        print(f"Created: {job.created_at}")
        print(f"Updated: {job.updated_at}")
        
        if job.error_message:
            print(f"Error: {job.error_message}")
        
        if job.article:
            print(f"\nArticle Details:")
            print(f"  Word count: {job.article.word_count}")
            print(f"  Primary keyword: {job.article.keyword_analysis.primary_keyword}")
    
    elif args.command == 'resume':
        print(f"\n🔄 Resuming job: {args.job_id}")
        job = agent.resume_job(args.job_id)
        print(f"✅ Job resumed. Status: {job.status.value}")
    
    elif args.command == 'list':
        jobs = agent.list_jobs()
        print("\n📋 Recent Jobs:")
        print("-" * 80)
        for job in jobs:
            print(f"ID: {job['job_id'][:8]}... | Status: {job['status']:10} | Topic: {job['topic']}")
        print("-" * 80)


if __name__ == "__main__":
    main()
