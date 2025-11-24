"""
SERP data fetching and analysis
"""
from models import SERPResult, SERPData, ArticleOutline
from typing import List, Dict
import re
from collections import Counter


class SERPAnalyzer:
    """Analyzes search results to extract themes and structure"""
    
    def get_serp_data(self, query: str) -> SERPData:
        """
        Fetch SERP data. Using mock data for simplicity.
        In production, replace with SerpAPI, DataForSEO, or ValueSERP
        """
        mock_results = self._generate_mock_serp(query)
        return SERPData(query=query, results=mock_results)
    
    def _generate_mock_serp(self, query: str) -> List[SERPResult]:
        """Generate realistic mock SERP data"""
        # Simplified mock - in real implementation, this would call an API
        results = [
            SERPResult(
                rank=i+1,
                url=f"https://example{i}.com/article",
                title=f"Top {10+i} {query} - Complete Guide 2025",
                snippet=f"Discover the best practices for {query}. Learn about tools, strategies, and tips..."
            )
            for i in range(10)
        ]
        return results
    
    def extract_themes(self, serp_data: SERPData) -> Dict[str, int]:
        """Extract common themes and keywords from SERP results"""
        all_text = " ".join([
            f"{result.title} {result.snippet}" 
            for result in serp_data.results
        ])
        
        # Remove common words and extract meaningful terms
        words = re.findall(r'\b[a-zA-Z]{4,}\b', all_text.lower())
        stop_words = {'this', 'that', 'with', 'from', 'have', 'they', 'will', 'your', 'about', 'their', 'which', 'these', 'best', 'guide'}
        meaningful_words = [w for w in words if w not in stop_words]
        
        # Count frequency
        word_freq = Counter(meaningful_words)
        return dict(word_freq.most_common(20))
    
    def generate_outline(self, serp_data: SERPData, themes: Dict[str, int]) -> ArticleOutline:
        """Create article outline based on SERP analysis"""
        query = serp_data.query
        
        # Extract H1 from top results
        h1 = f"The Complete Guide to {query.title()}"
        
        # Generate sections based on common patterns in SERP
        sections = [
            {
                "h2": f"What is {query.title()}?",
                "h3": ["Definition and Overview", "Why It Matters", "Key Benefits"]
            },
            {
                "h2": f"Top Strategies for {query.title()}",
                "h3": ["Strategy #1: Foundation", "Strategy #2: Implementation", "Strategy #3: Optimization"]
            },
            {
                "h2": f"Best Practices and Tips",
                "h3": ["Common Mistakes to Avoid", "Expert Recommendations", "Tools and Resources"]
            },
            {
                "h2": f"Getting Started with {query.title()}",
                "h3": ["Step-by-Step Guide", "Measuring Success", "Next Steps"]
            }
        ]
        
        return ArticleOutline(h1=h1, sections=sections)
    
    def extract_questions(self, serp_data: SERPData) -> List[str]:
        """Extract common questions from SERP for FAQ section"""
        questions = [
            f"What is {serp_data.query}?",
            f"How do I get started with {serp_data.query}?",
            f"What are the benefits of {serp_data.query}?",
            f"What tools are best for {serp_data.query}?",
        ]
        return questions
