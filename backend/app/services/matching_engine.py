from typing import Dict, Any, List, Tuple
from loguru import logger
from neo4j import GraphDatabase
import numpy as np
from openai import OpenAI

from app.core.config import settings
from app.core.neo4j_schema import get_query


class MatchingEngine:
    """
    Service for finding and scoring potential collaboration matches
    """

    def __init__(self):
        self.neo4j_driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def close(self):
        """Close Neo4j driver"""
        if self.neo4j_driver:
            self.neo4j_driver.close()

    def find_matches(
        self,
        user_email: str,
        target_categories: List[str] = None,
        min_score: float = 50.0,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Find potential matches for a user

        Args:
            user_email: User's email
            target_categories: Filter by user categories
            min_score: Minimum match score (0-100)
            limit: Maximum number of matches to return

        Returns:
            List of match dictionaries with scores and reasons
        """
        logger.info(f"Finding matches for {user_email}")

        if target_categories is None:
            target_categories = ["ceo_investor", "student", "general"]

        # Get potential matches from Neo4j
        with self.neo4j_driver.session() as session:
            result = session.run(
                get_query("find_potential_matches"),
                email=user_email,
                target_categories=target_categories,
                min_common_interests=1,
                limit=limit * 2,  # Get more candidates for scoring
            )

            candidates = [record.data() for record in result]

        if not candidates:
            logger.info("No potential matches found")
            return []

        # Score each candidate
        scored_matches = []
        for candidate in candidates:
            score = self._calculate_match_score(user_email, candidate)

            if score["total_score"] >= min_score:
                # Get match explanation
                explanation = self._generate_match_explanation(
                    user_email, candidate["matched_email"]
                )

                scored_matches.append(
                    {
                        "matched_email": candidate["matched_email"],
                        "matched_name": candidate["matched_name"],
                        "matched_category": candidate["matched_category"],
                        "matched_company": candidate.get("matched_company"),
                        "score": score,
                        "common_interests": explanation.get("common_interests", []),
                        "complementary_areas": explanation.get(
                            "complementary_areas", []
                        ),
                        "reason": explanation.get("reason", ""),
                    }
                )

        # Sort by score
        scored_matches.sort(key=lambda x: x["score"]["total_score"], reverse=True)

        return scored_matches[:limit]

    def _calculate_match_score(
        self, user_email: str, candidate: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calculate comprehensive match score

        Scoring factors:
        - Interest overlap (40%)
        - Complementary needs/offerings (30%)
        - Category fit (20%)
        - Context relevance (10%)
        """
        # Get match data from graph
        with self.neo4j_driver.session() as session:
            result = session.run(
                get_query("get_match_explanation"),
                email1=user_email,
                email2=candidate["matched_email"],
            )
            data = result.single()

            if not data:
                return {"total_score": 0.0}

            num_common = data.get("num_common_interests", 0)
            num_complementary = data.get("num_complementary_connections", 0)

        # Calculate component scores
        interest_overlap = min((num_common / 5.0) * 100, 100)  # Normalize to 100
        complementary_needs = min((num_complementary / 3.0) * 100, 100)

        # Category fit (simple heuristic)
        category_fit = self._calculate_category_fit(candidate["matched_category"])

        # Context relevance (could be based on recency, event, etc.)
        context_relevance = 80.0  # Default high relevance

        # Weighted total score
        total_score = (
            interest_overlap * 0.4
            + complementary_needs * 0.3
            + category_fit * 0.2
            + context_relevance * 0.1
        )

        return {
            "total_score": round(total_score, 2),
            "interest_overlap": round(interest_overlap, 2),
            "complementary_needs": round(complementary_needs, 2),
            "category_fit": round(category_fit, 2),
            "context_relevance": round(context_relevance, 2),
        }

    def _calculate_category_fit(self, matched_category: str) -> float:
        """
        Calculate how well the categories fit for collaboration

        CEO/Investor + Student = High (mentorship)
        CEO/Investor + CEO/Investor = High (partnerships)
        Student + Student = Medium (peer learning)
        etc.
        """
        # This is a simple heuristic - could be more sophisticated
        category_scores = {
            "ceo_investor": 90.0,
            "general": 70.0,
            "student": 75.0,
        }

        return category_scores.get(matched_category, 60.0)

    def _generate_match_explanation(
        self, user_email: str, matched_email: str
    ) -> Dict[str, Any]:
        """
        Generate human-readable explanation for why users match

        Uses LLM to create compelling match descriptions
        """
        # Get match data from graph
        with self.neo4j_driver.session() as session:
            result = session.run(
                get_query("get_match_explanation"),
                email1=user_email,
                email2=matched_email,
            )
            data = result.single()

            if not data:
                return {"reason": "No clear connection found"}

            common_interests = data.get("common_interests", [])
            p1_needs_met = data.get("p1_needs_met", [])
            p2_needs_met = data.get("p2_needs_met", [])

        # Generate explanation using LLM
        prompt = f"""Generate a compelling 1-2 sentence explanation for why these two people should connect:

Common Interests: {', '.join(common_interests) if common_interests else 'None'}
Complementary Needs:
- Person 1's needs that Person 2 can fulfill: {', '.join(p1_needs_met) if p1_needs_met else 'None'}
- Person 2's needs that Person 1 can fulfill: {', '.join(p2_needs_met) if p2_needs_met else 'None'}

Be specific and actionable. Focus on the value of the connection."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at explaining business networking connections.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=150,
            )

            reason = response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Failed to generate explanation: {e}")
            reason = f"Shared interests: {', '.join(common_interests[:3])}"

        return {
            "common_interests": common_interests,
            "complementary_areas": p1_needs_met + p2_needs_met,
            "reason": reason,
        }

    def create_match(
        self,
        user_email: str,
        matched_email: str,
        score: Dict[str, float],
        reason: str,
        common_interests: List[str],
        complementary_areas: List[str],
    ) -> bool:
        """
        Create a match relationship in Neo4j

        Args:
            user_email: First user's email
            matched_email: Second user's email
            score: Match score dictionary
            reason: Explanation of the match
            common_interests: List of common interests
            complementary_areas: List of complementary areas

        Returns:
            True if successful
        """
        logger.info(f"Creating match between {user_email} and {matched_email}")

        try:
            with self.neo4j_driver.session() as session:
                session.run(
                    get_query("create_match"),
                    email1=user_email,
                    email2=matched_email,
                    score=score["total_score"],
                    reason=reason,
                    common_interests=common_interests,
                    complementary_areas=complementary_areas,
                    confidence=score.get("interest_overlap", 0) / 100.0,
                )

            logger.info("Match created successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to create match: {e}")
            return False

    def update_match_status(
        self, user_email: str, matched_email: str, status: str
    ) -> bool:
        """
        Update the status of a match

        Args:
            user_email: User's email
            matched_email: Matched user's email
            status: New status (new, contacted, scheduled, completed, dismissed)

        Returns:
            True if successful
        """
        logger.info(f"Updating match status to '{status}'")

        try:
            with self.neo4j_driver.session() as session:
                session.run(
                    get_query("update_match_status"),
                    email1=user_email,
                    email2=matched_email,
                    status=status,
                )

            return True

        except Exception as e:
            logger.error(f"Failed to update match status: {e}")
            return False

    def get_user_matches(
        self,
        user_email: str,
        statuses: List[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Get existing matches for a user

        Args:
            user_email: User's email
            statuses: Filter by status
            skip: Number of matches to skip
            limit: Maximum matches to return

        Returns:
            List of match dictionaries
        """
        if statuses is None:
            statuses = ["new", "contacted", "scheduled"]

        logger.info(f"Getting matches for {user_email}")

        with self.neo4j_driver.session() as session:
            result = session.run(
                get_query("get_user_matches"),
                email=user_email,
                statuses=statuses,
                skip=skip,
                limit=limit,
            )

            matches = [record.data() for record in result]

        return matches
