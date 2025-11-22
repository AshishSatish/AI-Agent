"""Research orchestrator for gathering company information"""

import requests
from typing import List, Dict, Optional
from serpapi import GoogleSearch
import json


class CompanyResearcher:
    """Orchestrates research from multiple sources"""

    def __init__(self, serpapi_key: str, max_sources: int = 5):
        """Initialize the researcher"""
        self.serpapi_key = serpapi_key
        self.max_sources = max_sources
        self.research_data: Dict[str, any] = {}

    def search_web(self, query: str) -> List[Dict[str, str]]:
        """Search the web using SerpAPI"""
        try:
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "num": self.max_sources,
                "engine": "google"
            }

            search = GoogleSearch(params)
            results = search.get_dict()

            # Extract organic results
            organic_results = results.get("organic_results", [])

            formatted_results = []
            for result in organic_results[:self.max_sources]:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "source": "web_search"
                })

            return formatted_results

        except Exception as e:
            return [{
                "error": str(e),
                "source": "web_search"
            }]

    def research_company(self, company_name: str) -> Dict[str, any]:
        """Conduct comprehensive research on a company"""
        self.research_data = {
            "company_name": company_name,
            "sources": [],
            "summary": {},
            "conflicts": []
        }

        # Research queries
        queries = [
            f"{company_name} company overview",
            f"{company_name} products services",
            f"{company_name} recent news",
            f"{company_name} market position competitors",
            f"{company_name} financial performance revenue"
        ]

        all_results = []
        for query in queries:
            results = self.search_web(query)
            all_results.extend(results)

        self.research_data["sources"] = all_results
        self.research_data["total_sources"] = len(all_results)

        return self.research_data

    def get_company_overview(self, company_name: str) -> Dict[str, any]:
        """Get a quick overview of the company"""
        query = f"{company_name} company overview about"
        results = self.search_web(query)

        return {
            "company_name": company_name,
            "overview_sources": results
        }

    def get_recent_news(self, company_name: str) -> List[Dict[str, str]]:
        """Get recent news about the company"""
        query = f"{company_name} recent news 2024"
        return self.search_web(query)

    def find_conflicts(self, data: Dict) -> List[str]:
        """Identify potential conflicts in research data"""
        # This is a simplified version - can be enhanced with NLP
        conflicts = []

        # Example: Check for conflicting information in snippets
        # In a production system, you'd use more sophisticated analysis

        return conflicts

    def synthesize_findings(self) -> str:
        """Create a summary of research findings"""
        if not self.research_data.get("sources"):
            return "No research data available."

        sources = self.research_data["sources"]

        summary = f"Research Summary for {self.research_data.get('company_name', 'Unknown Company')}\n\n"
        summary += f"Total sources analyzed: {len(sources)}\n\n"

        summary += "Key Findings:\n"
        for idx, source in enumerate(sources[:5], 1):
            if "error" not in source:
                summary += f"{idx}. {source.get('title', 'N/A')}\n"
                summary += f"   {source.get('snippet', 'N/A')}\n\n"

        return summary
