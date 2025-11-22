"""Conversational Agent using Groq API"""

from groq import Groq
from typing import List, Dict, Optional
import json


class ConversationalAgent:
    """Main conversational agent for interacting with users"""

    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768"):
        """Initialize the agent with Groq API"""
        self.client = Groq(api_key=api_key)
        self.model = model
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt = """You are a professional Company Research Assistant. Your role is to:
1. Help users research companies through natural conversation
2. Ask clarifying questions when needed
3. Gather and synthesize information from multiple sources
4. Provide updates during research process
5. Generate comprehensive account plans
6. Allow users to update specific sections of account plans

Be conversational, professional, and thorough. When you need more information, ask specific questions.
When you find conflicting information, alert the user and ask if they want you to investigate further.
"""

    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })

    def get_response(self, user_message: str, context: Optional[Dict] = None) -> str:
        """Get response from the agent"""
        # Add user message to history
        self.add_message("user", user_message)

        # Prepare messages for API call
        messages = [{"role": "system", "content": self.system_prompt}]

        # Add context if available (research findings, etc.)
        if context:
            context_message = f"\n\nCurrent Context:\n{json.dumps(context, indent=2)}"
            messages.append({"role": "system", "content": context_message})

        # Add conversation history
        messages.extend(self.conversation_history)

        try:
            # Get response from Groq
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.7,
                max_tokens=2000
            )

            response = chat_completion.choices[0].message.content

            # Add assistant response to history
            self.add_message("assistant", response)

            return response

        except Exception as e:
            return f"Error getting response: {str(e)}"

    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []

    def extract_intent(self, user_message: str) -> Dict[str, any]:
        """Extract user intent from message"""
        intent_prompt = f"""Analyze this user message and determine their intent.
Possible intents: research_company, generate_plan, update_plan, ask_question, general_chat

User message: {user_message}

Return a JSON object with:
- intent: the main intent
- company_name: extracted company name (if any)
- section: account plan section to update (if updating)
- details: any additional relevant details

Return only valid JSON, nothing else."""

        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": intent_prompt}],
                model=self.model,
                temperature=0.3,
                max_tokens=500
            )

            result = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]

            return json.loads(result)
        except Exception as e:
            return {
                "intent": "general_chat",
                "error": str(e)
            }
