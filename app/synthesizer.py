"""Data synthesis engine to consolidate research findings"""

from typing import List, Dict, Optional
from groq import Groq
import json


class DataSynthesizer:
    """Synthesizes research data from multiple sources"""

    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768"):
        """Initialize the synthesizer with Groq API"""
        self.client = Groq(api_key=api_key)
        self.model = model

    def synthesize_research(self, research_data: Dict, company_name: str) -> Dict[str, any]:
        """Synthesize research findings into structured data"""

        sources = research_data.get("sources", [])

        # Prepare sources text
        sources_text = ""
        for idx, source in enumerate(sources, 1):
            if "error" not in source:
                sources_text += f"\nSource {idx}:\n"
                sources_text += f"Title: {source.get('title', 'N/A')}\n"
                sources_text += f"Content: {source.get('snippet', 'N/A')}\n"
                sources_text += f"URL: {source.get('link', 'N/A')}\n"

        synthesis_prompt = f"""Analyze the following research sources about {company_name} and synthesize the information into a structured format.

{sources_text}

Provide a comprehensive synthesis in the following JSON format:
{{
    "company_overview": "Brief overview of the company",
    "products_services": ["List of main products/services"],
    "market_position": "Market position and competitive landscape",
    "recent_developments": ["Recent news and developments"],
    "key_insights": ["Key insights from the research"],
    "potential_conflicts": ["Any conflicting information found"],
    "data_quality": "Assessment of data quality and completeness"
}}

Return only valid JSON, nothing else."""

        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": synthesis_prompt}],
                model=self.model,
                temperature=0.5,
                max_tokens=2000
            )

            result = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
                result = result.strip()

            synthesized_data = json.loads(result)
            synthesized_data["sources_analyzed"] = len(sources)

            return synthesized_data

        except Exception as e:
            return {
                "error": f"Synthesis failed: {str(e)}",
                "company_overview": "Unable to synthesize data",
                "sources_analyzed": len(sources)
            }

    def identify_conflicts(self, research_data: Dict) -> List[str]:
        """Identify conflicting information in research data"""

        sources = research_data.get("sources", [])
        if len(sources) < 2:
            return []

        sources_text = ""
        for idx, source in enumerate(sources, 1):
            if "error" not in source:
                sources_text += f"\nSource {idx}: {source.get('snippet', 'N/A')}\n"

        conflict_prompt = f"""Analyze these sources and identify any conflicting information:

{sources_text}

List any contradictions or conflicting claims you find. If no conflicts exist, return an empty list.
Return a JSON array of strings, each describing a conflict.
Example: ["Source 1 claims X while Source 3 claims Y", "Conflicting revenue figures found"]

Return only valid JSON array, nothing else."""

        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": conflict_prompt}],
                model=self.model,
                temperature=0.3,
                max_tokens=1000
            )

            result = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
                result = result.strip()

            conflicts = json.loads(result)

            return conflicts if isinstance(conflicts, list) else []

        except Exception as e:
            return [f"Error identifying conflicts: {str(e)}"]

    def generate_summary(self, synthesized_data: Dict) -> str:
        """Generate a human-readable summary from synthesized data"""

        summary = f"""Company Research Summary
{'=' * 50}

Company Overview:
{synthesized_data.get('company_overview', 'N/A')}

Products & Services:
"""
        for product in synthesized_data.get('products_services', []):
            summary += f"- {product}\n"

        summary += f"""
Market Position:
{synthesized_data.get('market_position', 'N/A')}

Recent Developments:
"""
        for dev in synthesized_data.get('recent_developments', []):
            summary += f"- {dev}\n"

        summary += f"""
Key Insights:
"""
        for insight in synthesized_data.get('key_insights', []):
            summary += f"- {insight}\n"

        conflicts = synthesized_data.get('potential_conflicts', [])
        if conflicts:
            summary += f"\nPotential Conflicts Detected:\n"
            for conflict in conflicts:
                summary += f"⚠ {conflict}\n"

        summary += f"""
Data Quality: {synthesized_data.get('data_quality', 'Unknown')}
Sources Analyzed: {synthesized_data.get('sources_analyzed', 0)}
"""

        return summary
