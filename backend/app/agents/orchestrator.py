from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger

from app.agents.content_analyzer import (
    ContentAnalyzerAgent,
    EntityExtractorAgent,
    IntentClassifierAgent,
)


class AgentOrchestrator:
    """
    Orchestrates multiple agents to analyze recordings
    """

    def __init__(self):
        self.content_analyzer = ContentAnalyzerAgent()
        self.entity_extractor = EntityExtractorAgent()
        self.intent_classifier = IntentClassifierAgent()

    def analyze_recording(
        self,
        transcript: str,
        user_category: str = "general",
        parallel: bool = True,
    ) -> Dict[str, Any]:
        """
        Run all agents on a transcript

        Args:
            transcript: The conversation transcript
            user_category: User category (ceo_investor, student, general)
            parallel: Whether to run agents in parallel

        Returns:
            Combined results from all agents
        """
        logger.info("Starting orchestrated analysis")

        input_data = {"transcript": transcript, "user_category": user_category}

        if parallel:
            # Run agents in parallel for faster processing
            results = self._run_parallel(input_data)
        else:
            # Run agents sequentially
            results = self._run_sequential(input_data)

        # Combine results
        combined_results = {
            "content_analysis": results.get("content_analyzer", {}),
            "entities": results.get("entity_extractor", {}),
            "intents": results.get("intent_classifier", {}),
            "metadata": {
                "user_category": user_category,
                "transcript_length": len(transcript),
                "total_processing_time": sum(
                    r.get("processing_time", 0) for r in results.values()
                ),
            },
        }

        logger.info("Orchestrated analysis completed")
        return combined_results

    def _run_parallel(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all agents in parallel using ThreadPoolExecutor
        """
        results = {}

        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all agent tasks
            future_to_agent = {
                executor.submit(
                    self.content_analyzer.execute, input_data
                ): "content_analyzer",
                executor.submit(
                    self.entity_extractor.execute, input_data
                ): "entity_extractor",
                executor.submit(
                    self.intent_classifier.execute, input_data
                ): "intent_classifier",
            }

            # Collect results as they complete
            for future in as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                try:
                    result = future.result()
                    results[agent_name] = result
                    logger.info(f"Agent '{agent_name}' completed")
                except Exception as e:
                    logger.error(f"Agent '{agent_name}' failed: {e}")
                    results[agent_name] = {"error": str(e), "success": False}

        return results

    def _run_sequential(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all agents sequentially
        """
        results = {}

        # Run content analyzer
        try:
            results["content_analyzer"] = self.content_analyzer.execute(input_data)
        except Exception as e:
            logger.error(f"Content analyzer failed: {e}")
            results["content_analyzer"] = {"error": str(e), "success": False}

        # Run entity extractor
        try:
            results["entity_extractor"] = self.entity_extractor.execute(input_data)
        except Exception as e:
            logger.error(f"Entity extractor failed: {e}")
            results["entity_extractor"] = {"error": str(e), "success": False}

        # Run intent classifier
        try:
            results["intent_classifier"] = self.intent_classifier.execute(input_data)
        except Exception as e:
            logger.error(f"Intent classifier failed: {e}")
            results["intent_classifier"] = {"error": str(e), "success": False}

        return results

    def generate_summary(self, analysis_results: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary of the analysis

        Args:
            analysis_results: Combined results from all agents

        Returns:
            Summary text
        """
        # This could also be done by an LLM, but for now we'll do simple formatting
        content = analysis_results.get("content_analysis", {}).get("results", {})
        entities = analysis_results.get("entities", {}).get("results", {})
        intents = analysis_results.get("intents", {}).get("results", {})

        summary_parts = []

        # Topics
        if content.get("topics"):
            topics_str = ", ".join([t.get("topic", "") for t in content["topics"][:5]])
            summary_parts.append(f"Main topics discussed: {topics_str}")

        # Intents
        looking_for = intents.get("looking_for", [])
        if looking_for:
            needs_str = ", ".join([i.get("intent_type", "") for i in looking_for[:3]])
            summary_parts.append(f"Looking for: {needs_str}")

        offering = intents.get("offering", [])
        if offering:
            offers_str = ", ".join([i.get("intent_type", "") for i in offering[:3]])
            summary_parts.append(f"Can offer: {offers_str}")

        # Entities
        if entities.get("entities"):
            companies = [
                e["value"] for e in entities["entities"] if e["type"] == "COMPANIES"
            ]
            if companies:
                summary_parts.append(f"Companies mentioned: {', '.join(companies[:3])}")

        return " | ".join(summary_parts) if summary_parts else "No clear insights extracted"
