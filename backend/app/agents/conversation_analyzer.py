from typing import Dict, Any
from app.agents.base_agent import BaseAgent


class ConversationAnalyzer(BaseAgent):
    def __init__(self):
        super().__init__(
            name="conversation_analyzer",
            model="gpt-4-turbo-preview",
            provider="openai",
            temperature=0.7
        )

    def get_system_prompt(self) -> str:
        return """You are an AI analyst for Lyncsea lead generation platform.
Analyze networking event conversations and extract actionable insights for connecting people based on skills, needs, and opportunities.

Focus on:
- Speaker roles and interests
- Topics and industries discussed
- Entities (people, companies, skills, products)
- What speakers are looking for vs offering
- Potential matches and connections
- Concrete next steps

Be concise and actionable."""

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        transcript = input_data.get("transcript", "")

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"""Analyze this conversation:

{transcript}

Provide:
1. SPEAKERS & ROLES
2. KEY TOPICS
3. ENTITIES (people, companies, skills)
4. NEEDS & OFFERS (what each speaker wants/offers)
5. LEAD OPPORTUNITIES (matches to make)
6. ACTION ITEMS (next steps)"""}
        ]

        analysis = self.call_llm(messages, max_tokens=1500)

        return {
            "analysis": analysis,
            "transcript_length": len(transcript)
        }