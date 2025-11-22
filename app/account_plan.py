"""Account Plan Generator"""

from typing import Dict, List, Optional
from groq import Groq
import json
from datetime import datetime
import os


class AccountPlanGenerator:
    """Generates and manages account plans for companies"""

    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768", data_dir: str = "data"):
        """Initialize the account plan generator"""
        self.client = Groq(api_key=api_key)
        self.model = model
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def generate_plan(self, company_name: str, synthesized_data: Dict) -> Dict[str, any]:
        """Generate a comprehensive account plan"""

        plan_prompt = f"""Based on the following research data about {company_name}, generate a comprehensive account plan.

Research Data:
{json.dumps(synthesized_data, indent=2)}

Create an account plan with the following sections in JSON format:
{{
    "executive_summary": "High-level overview of the account and opportunity",
    "company_background": {{
        "overview": "Company description",
        "size": "Company size (employees, revenue if known)",
        "industry": "Industry and sector",
        "headquarters": "Location"
    }},
    "products_and_services": {{
        "offerings": ["List of products/services"],
        "key_differentiators": ["What makes them unique"]
    }},
    "market_analysis": {{
        "position": "Market position",
        "competitors": ["Main competitors"],
        "trends": ["Relevant market trends"]
    }},
    "key_stakeholders": {{
        "decision_makers": ["Potential decision makers (titles/roles)"],
        "influencers": ["Key influencers"]
    }},
    "opportunity_assessment": {{
        "potential_needs": ["Potential business needs"],
        "pain_points": ["Possible pain points"],
        "opportunities": ["Engagement opportunities"]
    }},
    "engagement_strategy": {{
        "approach": "Recommended approach",
        "value_proposition": "Value we can offer",
        "next_steps": ["Recommended next steps"]
    }},
    "risks_and_challenges": ["Potential risks or challenges"],
    "success_metrics": ["How to measure success"]
}}

Return only valid JSON, nothing else."""

        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": plan_prompt}],
                model=self.model,
                temperature=0.6,
                max_tokens=3000
            )

            result = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
                result = result.strip()

            account_plan = json.loads(result)

            # Add metadata
            account_plan["metadata"] = {
                "company_name": company_name,
                "generated_at": datetime.now().isoformat(),
                "version": "1.0"
            }

            return account_plan

        except Exception as e:
            return {
                "error": f"Plan generation failed: {str(e)}",
                "metadata": {
                    "company_name": company_name,
                    "generated_at": datetime.now().isoformat()
                }
            }

    def update_section(self, account_plan: Dict, section_path: str, new_content: any) -> Dict:
        """Update a specific section of the account plan

        Args:
            account_plan: The current account plan
            section_path: Dot-notation path to section (e.g., 'engagement_strategy.approach')
            new_content: New content for the section
        """
        # Split the path
        keys = section_path.split('.')

        # Navigate to the parent of the target
        current = account_plan
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Update the target
        current[keys[-1]] = new_content

        # Update metadata
        if "metadata" not in account_plan:
            account_plan["metadata"] = {}

        account_plan["metadata"]["last_updated"] = datetime.now().isoformat()
        account_plan["metadata"]["version"] = str(
            float(account_plan["metadata"].get("version", "1.0")) + 0.1
        )

        return account_plan

    def save_plan(self, account_plan: Dict, filename: Optional[str] = None) -> str:
        """Save account plan to file"""

        if not filename:
            company_name = account_plan.get("metadata", {}).get("company_name", "unknown")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{company_name}_{timestamp}.json"

        filepath = os.path.join(self.data_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(account_plan, f, indent=2, ensure_ascii=False)

        return filepath

    def load_plan(self, filename: str) -> Dict:
        """Load account plan from file"""

        filepath = os.path.join(self.data_dir, filename)

        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_plans(self) -> List[str]:
        """List all saved account plans"""

        if not os.path.exists(self.data_dir):
            return []

        return [f for f in os.listdir(self.data_dir) if f.endswith('.json')]

    def format_plan_as_text(self, account_plan: Dict) -> str:
        """Format account plan as readable text"""

        if "error" in account_plan:
            return f"Error: {account_plan['error']}"

        text = f"""
{'=' * 80}
ACCOUNT PLAN
{'=' * 80}

Company: {account_plan.get('metadata', {}).get('company_name', 'N/A')}
Generated: {account_plan.get('metadata', {}).get('generated_at', 'N/A')}
Version: {account_plan.get('metadata', {}).get('version', 'N/A')}

{'=' * 80}
EXECUTIVE SUMMARY
{'=' * 80}
{account_plan.get('executive_summary', 'N/A')}

{'=' * 80}
COMPANY BACKGROUND
{'=' * 80}
Overview: {account_plan.get('company_background', {}).get('overview', 'N/A')}
Size: {account_plan.get('company_background', {}).get('size', 'N/A')}
Industry: {account_plan.get('company_background', {}).get('industry', 'N/A')}
Headquarters: {account_plan.get('company_background', {}).get('headquarters', 'N/A')}

{'=' * 80}
PRODUCTS AND SERVICES
{'=' * 80}
Offerings:
"""
        offerings = account_plan.get('products_and_services', {}).get('offerings', [])
        if isinstance(offerings, str):
            text += f"{offerings}\n"
        elif isinstance(offerings, list):
            for offering in offerings:
                text += f"  - {offering}\n"

        text += "\nKey Differentiators:\n"
        diffs = account_plan.get('products_and_services', {}).get('key_differentiators', [])
        if isinstance(diffs, str):
            text += f"{diffs}\n"
        elif isinstance(diffs, list):
            for diff in diffs:
                text += f"  - {diff}\n"

        text += f"""
{'=' * 80}
MARKET ANALYSIS
{'=' * 80}
Position: {account_plan.get('market_analysis', {}).get('position', 'N/A')}

Competitors:
"""
        comps = account_plan.get('market_analysis', {}).get('competitors', [])
        if isinstance(comps, str):
            text += f"{comps}\n"
        elif isinstance(comps, list):
            for comp in comps:
                text += f"  - {comp}\n"

        text += "\nMarket Trends:\n"
        trends = account_plan.get('market_analysis', {}).get('trends', [])
        if isinstance(trends, str):
            text += f"{trends}\n"
        elif isinstance(trends, list):
            for trend in trends:
                text += f"  - {trend}\n"

        text += f"""
{'=' * 80}
OPPORTUNITY ASSESSMENT
{'=' * 80}
Potential Needs:
"""
        needs = account_plan.get('opportunity_assessment', {}).get('potential_needs', [])
        if isinstance(needs, str):
            text += f"{needs}\n"
        elif isinstance(needs, list):
            for need in needs:
                text += f"  - {need}\n"

        text += "\nPain Points:\n"
        pains = account_plan.get('opportunity_assessment', {}).get('pain_points', [])
        if isinstance(pains, str):
            text += f"{pains}\n"
        elif isinstance(pains, list):
            for pain in pains:
                text += f"  - {pain}\n"

        text += "\nOpportunities:\n"
        opps = account_plan.get('opportunity_assessment', {}).get('opportunities', [])
        if isinstance(opps, str):
            text += f"{opps}\n"
        elif isinstance(opps, list):
            for opp in opps:
                text += f"  - {opp}\n"

        text += f"""
{'=' * 80}
ENGAGEMENT STRATEGY
{'=' * 80}
Approach: {account_plan.get('engagement_strategy', {}).get('approach', 'N/A')}
Value Proposition: {account_plan.get('engagement_strategy', {}).get('value_proposition', 'N/A')}

Next Steps:
"""
        steps = account_plan.get('engagement_strategy', {}).get('next_steps', [])
        if isinstance(steps, str):
            text += f"{steps}\n"
        elif isinstance(steps, list):
            for step in steps:
                text += f"  - {step}\n"

        text += f"""
{'=' * 80}
RISKS AND CHALLENGES
{'=' * 80}
"""
        risks = account_plan.get('risks_and_challenges', [])
        if isinstance(risks, str):
            text += f"{risks}\n"
        elif isinstance(risks, list):
            for risk in risks:
                text += f"  - {risk}\n"

        text += f"""
{'=' * 80}
SUCCESS METRICS
{'=' * 80}
"""
        metrics = account_plan.get('success_metrics', [])
        if isinstance(metrics, str):
            text += f"{metrics}\n"
        elif isinstance(metrics, list):
            for metric in metrics:
                text += f"  - {metric}\n"

        text += f"\n{'=' * 80}\n"

        return text
