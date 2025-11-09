from typing import Dict, Any, List
import json
from loguru import logger

from app.agents.base_agent import BaseAgent


class ContentAnalyzerAgent(BaseAgent):
    """
    Agent responsible for analyzing transcript content and extracting:
    - Key topics and themes
    - Business interests
    - Pain points
    - Opportunities mentioned
    """

    def __init__(self):
        super().__init__(
            name="ContentAnalyzer",
            model="gpt-4-turbo-preview",
            provider="openai",
            temperature=0.3,
        )

    def get_system_prompt(self) -> str:
        return """You are an expert business analyst specializing in extracting insights from conversations at networking events.

Your task is to analyze conversation transcripts and extract:

1. KEY TOPICS: Main subjects discussed (technology, business models, industries, etc.)
2. INTERESTS: Areas the person shows genuine interest in (investments, partnerships, hiring, etc.)
3. PAIN POINTS: Problems, challenges, or frustrations mentioned
4. OFFERINGS: What the person can provide (funding, expertise, services, connections, etc.)
5. BUSINESS CONTEXT: Industry, company stage, role, expertise areas

Be specific and actionable. Focus on identifying collaboration opportunities.

Return your analysis as a structured JSON object with these keys:
- topics: List of topics with relevance scores
- interests: List of interests with context
- pain_points: List of challenges mentioned
- offerings: List of what they can provide
- business_context: Summary of their business situation
- key_quotes: Important verbatim quotes that reveal intent

Keep your analysis concise but comprehensive."""

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze transcript content

        Args:
            input_data: {
                "transcript": str,
                "speaker_segments": List[dict],  # optional
                "context": dict  # optional metadata
            }

        Returns:
            Dictionary with extracted insights
        """
        transcript = input_data.get("transcript", "")
        if not transcript:
            raise ValueError("No transcript provided")

        logger.info(f"Analyzing transcript of length {len(transcript)}")

        # Prepare messages for LLM
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {
                "role": "user",
                "content": f"""Analyze this conversation transcript from a networking event:

{transcript}

Extract key topics, interests, pain points, offerings, and business context.
Return as JSON.""",
            },
        ]

        # Call LLM
        response = self.call_llm(messages)

        # Parse JSON response
        try:
            analysis = json.loads(response)
        except json.JSONDecodeError:
            # If LLM didn't return valid JSON, try to extract it
            logger.warning("LLM response was not valid JSON, attempting to extract")
            # Try to find JSON in the response
            import re

            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                logger.error("Could not extract JSON from LLM response")
                analysis = {"error": "Invalid response format", "raw": response}

        return analysis


class EntityExtractorAgent(BaseAgent):
    """
    Agent responsible for extracting named entities:
    - People names
    - Companies
    - Locations
    - Technologies/Products
    """

    def __init__(self):
        super().__init__(
            name="EntityExtractor",
            model="gpt-4-turbo-preview",
            provider="openai",
            temperature=0.2,
        )

    def get_system_prompt(self) -> str:
        return """You are an expert at extracting named entities from business conversations.

Extract the following types of entities:
1. PEOPLE: Full names of individuals mentioned
2. COMPANIES: Company and organization names
3. LOCATIONS: Cities, countries, regions mentioned in business context
4. TECHNOLOGIES: Specific technologies, platforms, or tools mentioned
5. PRODUCTS: Product or service names

For each entity, provide:
- type: The entity type
- value: The entity name/value
- confidence: Your confidence level (0.0 to 1.0)
- context: Brief context of how it was mentioned

Return as JSON with an "entities" array.

Only extract entities that are clearly mentioned. Do not infer or assume."""

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract named entities from transcript

        Args:
            input_data: {
                "transcript": str
            }

        Returns:
            Dictionary with extracted entities
        """
        transcript = input_data.get("transcript", "")
        if not transcript:
            raise ValueError("No transcript provided")

        logger.info("Extracting entities from transcript")

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {
                "role": "user",
                "content": f"""Extract named entities from this transcript:

{transcript}

Return as JSON with an "entities" array.""",
            },
        ]

        response = self.call_llm(messages)

        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            logger.error("Could not parse entity extraction response")
            result = {"entities": []}

        return result


class IntentClassifierAgent(BaseAgent):
    """
    Agent responsible for classifying user intents:
    - What are they looking for?
    - What can they offer?
    - What type of collaboration?
    """

    def __init__(self):
        super().__init__(
            name="IntentClassifier",
            model="gpt-4-turbo-preview",
            provider="openai",
            temperature=0.3,
        )

    def get_system_prompt(self) -> str:
        return """You are an expert at understanding business networking intentions.

Analyze the conversation and identify what the person is LOOKING FOR and what they can OFFER.

Looking for (needs):
- Investment (seeking funding)
- Partnership (business partnerships)
- Hiring (looking to hire talent)
- Learning (wants to learn or get mentorship)
- Customers (looking for clients/customers)
- Services (needs specific services)
- Collaboration (project collaboration)

Offering:
- Investment (can provide funding)
- Partnership (can be a partner)
- Employment (offering jobs)
- Mentorship (can mentor/teach)
- Services (provides specific services)
- Expertise (has specific knowledge/skills)
- Network (can make introductions)

For each intent, provide:
- intent_type: The type of intent
- description: Specific description
- confidence: Confidence level (0.0 to 1.0)
- urgency: high/medium/low
- supporting_evidence: Quotes or context supporting this intent

Return as JSON with "looking_for" and "offering" arrays."""

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify user intents

        Args:
            input_data: {
                "transcript": str,
                "user_category": str  # ceo_investor, student, general
            }

        Returns:
            Dictionary with classified intents
        """
        transcript = input_data.get("transcript", "")
        user_category = input_data.get("user_category", "general")

        if not transcript:
            raise ValueError("No transcript provided")

        logger.info(f"Classifying intents for {user_category} user")

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {
                "role": "user",
                "content": f"""This conversation is from a {user_category} at a networking event.

Transcript:
{transcript}

Identify what they are looking for and what they can offer.
Return as JSON.""",
            },
        ]

        response = self.call_llm(messages)

        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            logger.error("Could not parse intent classification response")
            result = {"looking_for": [], "offering": []}

        return result
