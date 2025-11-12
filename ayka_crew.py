#!/usr/bin/env python3
"""
AYKA Lead Generation - Multi-Agent System
Clean implementation with CrewAI - No mock code
"""

import os
import sys
import json
import logging
import smtplib
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

from crewai import Agent, Task, Crew, Process
from crewai.tools import tool

try:
    from crewai_tools import SerperDevTool
except ImportError:
    SerperDevTool = None

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ayka_agent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('ayka')


@tool("read_transcript")
def read_transcript_tool(file_path: str) -> str:
    """Read and return transcript content from file"""
    with open(file_path, 'r') as f:
        return f.read()


@tool("save_leads")
def save_leads_tool(leads_data: dict) -> str:
    """Save lead data to JSON file"""
    output_dir = Path("leads_data")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f"leads_{timestamp}.json"

    with open(output_file, 'w') as f:
        json.dump(leads_data, f, indent=2)

    logger.info(f"Leads saved to {output_file}")
    return str(output_file)


@tool("send_email")
def send_email_tool(recipient: str, subject: str, html_body: str) -> str:
    """Send HTML formatted email via SMTP"""
    load_dotenv(override=True)
    email_user = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASSWORD")

    if not email_user or not email_password:
        logger.error(f"Email credentials missing - USER: {bool(email_user)}, PASS: {bool(email_password)}")
        raise ValueError("EMAIL_USER and EMAIL_PASSWORD must be set in .env")

    msg = MIMEMultipart('alternative')
    msg['From'] = email_user
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(html_body, 'html'))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email_user, email_password)
    server.send_message(msg)
    server.quit()

    logger.info(f"Email sent to {recipient}")
    return f"Email sent successfully to {recipient}"


class AYKACrew:
    """AYKA Lead Generation Crew"""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in .env")

        os.environ["OPENAI_API_KEY"] = self.openai_api_key

    def create_agents(self):
        """Create specialized agents"""

        # Agent 1: Transcript Reader
        transcript_reader = Agent(
            role='Transcript Analyst',
            goal='Read and analyze conversation transcripts to extract structured information',
            backstory='Expert at parsing conversation transcripts and identifying speakers, topics, and key discussion points',
            tools=[read_transcript_tool],
            verbose=False,
            allow_delegation=False
        )

        # Agent 2: Lead Generator
        lead_generator = Agent(
            role='Lead Generation Specialist',
            goal='Identify business opportunities, needs, and potential connections from conversations',
            backstory='Experienced in B2B lead generation, understanding business needs, investment opportunities, and strategic partnerships',
            tools=[save_leads_tool],
            verbose=False,
            allow_delegation=False
        )

        # Agent 3: Research Agent
        researcher_tools = []
        if SerperDevTool:
            search_tool = SerperDevTool()
            researcher_tools.append(search_tool)

        researcher = Agent(
            role='Contact Research Specialist',
            goal='Find contact information, LinkedIn profiles, company websites for identified leads',
            backstory='Expert at finding professional contact information and company intelligence using web research',
            tools=researcher_tools,
            verbose=False,
            allow_delegation=False
        )

        # Agent 4: Email Sender
        email_sender = Agent(
            role='Communication Manager',
            goal='Create beautifully formatted HTML emails with lead insights',
            backstory='Expert at crafting visually appealing, professional business communications with proper formatting and color coding',
            tools=[send_email_tool],
            verbose=False,
            allow_delegation=False
        )

        return transcript_reader, lead_generator, researcher, email_sender

    def create_tasks(self, transcript_file: str, recipient_email: str, agents: tuple):
        """Create tasks for agents"""
        transcript_reader, lead_generator, researcher, email_sender = agents

        # Task 1: Read and analyze transcript
        read_task = Task(
            description=f"""Read the transcript file at {transcript_file} and extract:
            - All speakers and their roles
            - Key topics discussed
            - Companies and products mentioned
            - Explicit needs or problems stated
            - Offers or solutions provided

            Return structured data with these elements.""",
            agent=transcript_reader,
            expected_output="Structured analysis of transcript with speakers, topics, companies, needs, and offers"
        )

        # Task 2: Generate leads
        generate_task = Task(
            description="""Based on the transcript analysis, identify:
            - High-value lead opportunities (investment, partnership, hiring)
            - Match needs with offers
            - Priority ranking (high/medium/low)
            - Specific action items for follow-up

            Save this data using the save_leads tool with structure:
            {
                "leads": [{"name": "...", "company": "...", "opportunity": "...", "priority": "..."}],
                "opportunities": [{"type": "...", "description": "...", "priority": "..."}],
                "action_items": ["..."]
            }""",
            agent=lead_generator,
            expected_output="Lead opportunities saved to JSON file with prioritized action items",
            context=[read_task]
        )

        # Task 3: Research contacts
        research_task = Task(
            description="""For each person and company identified, research and find:
            - LinkedIn profile URLs
            - Company websites
            - Professional email addresses (if publicly available)
            - Recent news or updates about the companies

            Focus on the high-priority leads first. Return this enriched data.""",
            agent=researcher,
            expected_output="Contact information and online profiles for identified leads",
            context=[read_task, generate_task]
        )

        # Task 4: Send formatted email
        email_task = Task(
            description=f"""Create and send a beautifully formatted HTML email to {recipient_email}.

            Subject: 🎯 Lead Insights from Networking Event - {{date}}

            Use this HTML structure with color coding:

            - Header: Use #2C3E50 background with white text
            - High priority items: #E74C3C (red)
            - Medium priority: #F39C12 (orange)
            - Low priority: #27AE60 (green)
            - Section headers: #3498DB (blue), bold, 18px
            - Body text: #34495E, 14px

            Include sections:
            1. Executive Summary (2-3 lines)
            2. 👥 Key People to Reach (with their roles, companies, LinkedIn, email if found)
            3. 🎯 Opportunities (color-coded by priority)
            4. 📋 Action Items (numbered list)
            5. 🔗 Useful Links (company websites, profiles)

            Make it visually appealing and professional. Use the send_email tool with HTML content.""",
            agent=email_sender,
            expected_output=f"Professional HTML email sent to {recipient_email}",
            context=[read_task, generate_task, research_task]
        )

        return [read_task, generate_task, research_task, email_task]

    def run(self, transcript_file: str, recipient_email: str):
        """Execute the crew workflow"""
        logger.info(f"Starting AYKA Crew for {transcript_file}")

        agents = self.create_agents()
        tasks = self.create_tasks(transcript_file, recipient_email, agents)

        crew = Crew(
            agents=list(agents),
            tasks=tasks,
            process=Process.sequential,
            verbose=False
        )

        result = crew.kickoff()
        logger.info("AYKA Crew completed")

        return result


def main():
    if len(sys.argv) < 3:
        print("Usage: python ayka_crew.py <transcript_file> <recipient_email>")
        print("\nExample:")
        print("  python ayka_crew.py transcripts/demo_conversation.txt user@example.com")
        sys.exit(1)

    transcript_file = sys.argv[1]
    recipient_email = sys.argv[2]

    if not Path(transcript_file).exists():
        logger.error(f"File not found: {transcript_file}")
        sys.exit(1)

    try:
        crew = AYKACrew()
        result = crew.run(transcript_file, recipient_email)
        logger.info(f"Final result: {result}")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()