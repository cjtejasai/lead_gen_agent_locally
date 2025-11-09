"""
Neo4j Graph Database Schema for Ayka Lead Generation Platform

This module defines the graph structure for storing and querying
user interests, connections, and match opportunities.
"""

from enum import Enum


class NodeLabel(str, Enum):
    """Node labels in the graph"""
    PERSON = "Person"
    INTEREST = "Interest"
    EVENT = "Event"
    COMPANY = "Company"
    NEED = "Need"
    OFFERING = "Offering"
    RECORDING = "Recording"
    TOPIC = "Topic"
    SKILL = "Skill"


class RelationshipType(str, Enum):
    """Relationship types in the graph"""
    INTERESTED_IN = "INTERESTED_IN"
    WORKS_AT = "WORKS_AT"
    ATTENDED = "ATTENDED"
    LOOKING_FOR = "LOOKING_FOR"
    OFFERS = "OFFERS"
    MATCHED_WITH = "MATCHED_WITH"
    RECORDED_AT = "RECORDED_AT"
    MENTIONED = "MENTIONED"
    HAS_SKILL = "HAS_SKILL"
    COLLABORATES_WITH = "COLLABORATES_WITH"
    INVESTED_IN = "INVESTED_IN"
    WORKS_IN_DOMAIN = "WORKS_IN_DOMAIN"


# Neo4j Cypher Queries for Schema Creation

CREATE_CONSTRAINTS = [
    # Unique constraints
    "CREATE CONSTRAINT person_email IF NOT EXISTS FOR (p:Person) REQUIRE p.email IS UNIQUE",
    "CREATE CONSTRAINT company_name IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE",
    "CREATE CONSTRAINT event_id IF NOT EXISTS FOR (e:Event) REQUIRE e.event_id IS UNIQUE",
    "CREATE CONSTRAINT recording_id IF NOT EXISTS FOR (r:Recording) REQUIRE r.recording_id IS UNIQUE",
]

CREATE_INDEXES = [
    # Indexes for faster lookups
    "CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON (p.name)",
    "CREATE INDEX person_category IF NOT EXISTS FOR (p:Person) ON (p.category)",
    "CREATE INDEX interest_topic IF NOT EXISTS FOR (p:Interest) ON (p.topic)",
    "CREATE INDEX need_type IF NOT EXISTS FOR (n:Need) ON (n.need_type)",
    "CREATE INDEX offering_type IF NOT EXISTS FOR (o:Offering) ON (o.offering_type)",
    "CREATE INDEX event_date IF NOT EXISTS FOR (e:Event) ON (e.date)",
    "CREATE INDEX recording_date IF NOT EXISTS FOR (r:Recording) ON (r.created_at)",

    # Full-text indexes for search
    "CREATE FULLTEXT INDEX person_search IF NOT EXISTS FOR (p:Person) ON EACH [p.name, p.company, p.title]",
    "CREATE FULLTEXT INDEX interest_search IF NOT EXISTS FOR (i:Interest) ON EACH [i.topic, i.description]",
    "CREATE FULLTEXT INDEX company_search IF NOT EXISTS FOR (c:Company) ON EACH [c.name, c.industry]",
]


# Sample queries for common operations

SAMPLE_QUERIES = {
    "create_person": """
        MERGE (p:Person {email: $email})
        SET p.name = $name,
            p.category = $category,
            p.company = $company,
            p.title = $title,
            p.created_at = datetime(),
            p.updated_at = datetime()
        RETURN p
    """,

    "create_interest": """
        MERGE (i:Interest {topic: $topic})
        SET i.domain = $domain,
            i.description = $description,
            i.created_at = datetime()
        RETURN i
    """,

    "link_person_to_interest": """
        MATCH (p:Person {email: $email})
        MATCH (i:Interest {topic: $topic})
        MERGE (p)-[r:INTERESTED_IN]->(i)
        SET r.relevance_score = $relevance_score,
            r.mentions = $mentions,
            r.created_at = datetime()
        RETURN p, r, i
    """,

    "create_need": """
        MERGE (n:Need {id: $need_id})
        SET n.need_type = $need_type,
            n.description = $description,
            n.urgency = $urgency,
            n.created_at = datetime()
        RETURN n
    """,

    "create_offering": """
        MERGE (o:Offering {id: $offering_id})
        SET o.offering_type = $offering_type,
            o.description = $description,
            o.value_proposition = $value_proposition,
            o.created_at = datetime()
        RETURN o
    """,

    "link_person_to_need": """
        MATCH (p:Person {email: $email})
        MATCH (n:Need {id: $need_id})
        MERGE (p)-[r:LOOKING_FOR]->(n)
        SET r.priority = $priority,
            r.created_at = datetime()
        RETURN p, r, n
    """,

    "link_person_to_offering": """
        MATCH (p:Person {email: $email})
        MATCH (o:Offering {id: $offering_id})
        MERGE (p)-[r:OFFERS]->(o)
        SET r.confidence = $confidence,
            r.created_at = datetime()
        RETURN p, r, o
    """,

    "find_matching_needs_offerings": """
        MATCH (p1:Person)-[:LOOKING_FOR]->(n:Need)
        MATCH (p2:Person)-[:OFFERS]->(o:Offering)
        WHERE p1 <> p2
          AND o.offering_type = n.need_type
          AND p1.category IN $target_categories
        WITH p1, p2, n, o,
             gds.similarity.cosine(n.embedding, o.embedding) AS similarity
        WHERE similarity > $min_similarity
        RETURN p1, p2, n, o, similarity
        ORDER BY similarity DESC
        LIMIT $limit
    """,

    "find_common_interests": """
        MATCH (p1:Person {email: $email1})-[r1:INTERESTED_IN]->(i:Interest)<-[r2:INTERESTED_IN]-(p2:Person {email: $email2})
        RETURN i.topic AS common_interest,
               r1.relevance_score AS person1_relevance,
               r2.relevance_score AS person2_relevance,
               (r1.relevance_score + r2.relevance_score) / 2 AS avg_relevance
        ORDER BY avg_relevance DESC
    """,

    "find_potential_matches": """
        MATCH (p1:Person {email: $email})
        MATCH (p1)-[:INTERESTED_IN]->(i:Interest)<-[:INTERESTED_IN]-(p2:Person)
        WHERE p1 <> p2
          AND p2.category IN $target_categories
        WITH p1, p2, COUNT(DISTINCT i) AS common_interests
        WHERE common_interests >= $min_common_interests

        OPTIONAL MATCH (p1)-[:LOOKING_FOR]->(n:Need)
        OPTIONAL MATCH (p2)-[:OFFERS]->(o:Offering)
        WHERE n.need_type = o.offering_type

        WITH p1, p2, common_interests, COUNT(DISTINCT o) AS complementary_offerings

        RETURN p2.email AS matched_email,
               p2.name AS matched_name,
               p2.category AS matched_category,
               p2.company AS matched_company,
               common_interests,
               complementary_offerings,
               (common_interests * 0.6 + complementary_offerings * 0.4) AS match_score
        ORDER BY match_score DESC
        LIMIT $limit
    """,

    "create_match": """
        MATCH (p1:Person {email: $email1})
        MATCH (p2:Person {email: $email2})
        MERGE (p1)-[m:MATCHED_WITH]->(p2)
        SET m.score = $score,
            m.reason = $reason,
            m.common_interests = $common_interests,
            m.complementary_areas = $complementary_areas,
            m.confidence = $confidence,
            m.created_at = datetime(),
            m.status = 'new'
        RETURN m
    """,

    "get_person_network": """
        MATCH (p:Person {email: $email})
        OPTIONAL MATCH (p)-[r1:INTERESTED_IN]->(i:Interest)
        OPTIONAL MATCH (p)-[r2:LOOKING_FOR]->(n:Need)
        OPTIONAL MATCH (p)-[r3:OFFERS]->(o:Offering)
        OPTIONAL MATCH (p)-[r4:WORKS_AT]->(c:Company)
        OPTIONAL MATCH (p)-[r5:ATTENDED]->(e:Event)
        RETURN p,
               COLLECT(DISTINCT i) AS interests,
               COLLECT(DISTINCT n) AS needs,
               COLLECT(DISTINCT o) AS offerings,
               COLLECT(DISTINCT c) AS companies,
               COLLECT(DISTINCT e) AS events
    """,

    "get_match_explanation": """
        MATCH (p1:Person {email: $email1})
        MATCH (p2:Person {email: $email2})

        OPTIONAL MATCH (p1)-[:INTERESTED_IN]->(i:Interest)<-[:INTERESTED_IN]-(p2)
        WITH p1, p2, COLLECT(DISTINCT i.topic) AS common_interests

        OPTIONAL MATCH (p1)-[:LOOKING_FOR]->(n:Need)<-[:OFFERS]-(p2)
        WITH p1, p2, common_interests, COLLECT(DISTINCT n.description) AS p1_needs_met

        OPTIONAL MATCH (p2)-[:LOOKING_FOR]->(n2:Need)<-[:OFFERS]-(p1)
        WITH p1, p2, common_interests, p1_needs_met, COLLECT(DISTINCT n2.description) AS p2_needs_met

        RETURN common_interests,
               p1_needs_met,
               p2_needs_met,
               SIZE(common_interests) AS num_common_interests,
               SIZE(p1_needs_met) + SIZE(p2_needs_met) AS num_complementary_connections
    """,

    "update_match_status": """
        MATCH (p1:Person {email: $email1})-[m:MATCHED_WITH]->(p2:Person {email: $email2})
        SET m.status = $status,
            m.updated_at = datetime()
        RETURN m
    """,

    "get_user_matches": """
        MATCH (p:Person {email: $email})-[m:MATCHED_WITH]->(matched:Person)
        WHERE m.status IN $statuses
        RETURN matched.email AS email,
               matched.name AS name,
               matched.category AS category,
               matched.company AS company,
               matched.title AS title,
               m.score AS score,
               m.reason AS reason,
               m.common_interests AS common_interests,
               m.status AS status,
               m.created_at AS matched_at
        ORDER BY m.created_at DESC
        SKIP $skip
        LIMIT $limit
    """,
}


def get_query(query_name: str) -> str:
    """
    Get a predefined Cypher query by name

    Args:
        query_name: Name of the query

    Returns:
        Cypher query string
    """
    return SAMPLE_QUERIES.get(query_name, "")
