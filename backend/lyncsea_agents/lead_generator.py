#!/usr/bin/env python3
"""
Lyncsea Lead Generation - Multi-Agent System
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

# Configure logging - log to backend/logs/
log_dir = Path(__file__).parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'agents.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('lyncsea')


@tool("read_transcript")
def read_transcript_tool(file_path: str) -> str:
    """Read and return transcript content from file"""
    with open(file_path, 'r') as f:
        return f.read()


@tool("get_current_date")
def get_current_date_tool() -> str:
    """Get current date and time for deadline calculations"""
    now = datetime.now()
    return f"Today is {now.strftime('%A, %B %d, %Y')} at {now.strftime('%I:%M %p')}. Current date in YYYY-MM-DD format: {now.strftime('%Y-%m-%d')}"


@tool("save_leads")
def save_leads_tool(leads_data: dict) -> str:
    """Save lead data to JSON file"""
    # Save to data/leads/ directory (project root)
    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / "data" / "leads"
    output_dir.mkdir(parents=True, exist_ok=True)

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
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    if not email_user or not email_password:
        logger.error(f"Email credentials missing - USER: {bool(email_user)}, PASS: {bool(email_password)}")
        raise ValueError("EMAIL_USER and EMAIL_PASSWORD must be set in .env")

    msg = MIMEMultipart('alternative')
    msg['From'] = email_user
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(html_body, 'html'))

    # Use SSL for port 465, TLS for port 587
    if smtp_port == 465:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    else:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

    server.login(email_user, email_password)
    server.send_message(msg)
    server.quit()

    logger.info(f"Email sent to {recipient} via {smtp_server}")
    return f"Email sent successfully to {recipient}"


class LyncseaCrew:
    """Lyncsea Lead Generation Crew"""

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
            backstory='Experienced in B2B lead generation, understanding business needs, investment opportunities, and strategic partnerships. Expert at converting relative dates to absolute dates.',
            tools=[get_current_date_tool, save_leads_tool],
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
            description="""⚠️ CRITICAL RULES - READ CAREFULLY:

            1. ONLY extract information that is EXPLICITLY MENTIONED in the transcript
            2. NEVER invent, assume, or fabricate names, companies, or details
            3. If NO clear leads are found, return EMPTY arrays - this is ACCEPTABLE
            4. Each lead MUST have a direct quote or reference from the transcript
            5. If you're uncertain about ANY detail, OMIT it rather than guess

            📅 FOR ACTION ITEMS WITH DEADLINES:
            - FIRST use the get_current_date tool to know today's date
            - Convert relative dates to absolute dates in YYYY-MM-DD format:
              - "tomorrow" → calculate tomorrow's date (e.g., 2025-01-16)
              - "next week" → calculate date 7 days from now
              - "Friday" → find the next Friday's date
              - "end of month" → last day of current month
            - If no specific time mentioned, use "none" for deadline

            Based ONLY on the transcript analysis, identify:
            - High-value lead opportunities (investment, partnership, hiring) - ONLY if clearly discussed
            - Match needs with offers - ONLY if both are explicitly stated
            - Priority ranking (high/medium/low) - based on urgency mentioned in conversation
            - Action items for follow-up - ONLY if specific commitments were made

            VALIDATION CHECKLIST before saving:
            ✓ Can I quote the exact sentence where this person/company was mentioned?
            ✓ Is this information directly stated, not inferred?
            ✓ Would I be comfortable showing the speaker this extracted data?

            If NO genuine leads found, save:
            {
                "leads": [],
                "opportunities": [],
                "action_items": [],
                "note": "No clear lead opportunities identified in this conversation"
            }

            If leads ARE found, save with structure:
            {
                "leads": [
                    {
                        "name": "Exact name from transcript",
                        "company": "Exact company name mentioned",
                        "role": "Their role if stated",
                        "opportunity": "What they're looking for/offering",
                        "priority": "high/medium/low",
                        "evidence_quote": "Direct quote from conversation",
                        "email": "email if mentioned",
                        "linkedin": "LinkedIn URL if found"
                    }
                ],
                "opportunities": [{"type": "...", "description": "...", "priority": "..."}],
                "action_items": [
                    {
                        "action": "Connect with Sarah Chen for coffee meeting",
                        "deadline": "2025-01-16",
                        "deadline_type": "specific",
                        "priority": "high",
                        "action_type": "meeting",
                        "quote": "Let's grab coffee tomorrow to discuss the API",
                        "mentioned_by": "SPEAKER_02",
                        "speaker_name": "Sarah Chen",
                        "contact_email": "sarah@company.com",
                        "contact_company": "TechCorp"
                    }
                ]
            }

            ACTION_ITEM deadline_type options:
            - "specific" = exact date mentioned (tomorrow, Friday, Jan 15)
            - "week" = vague week reference (next week, sometime next week)
            - "month" = vague month reference (next month, end of month)
            - "none" = no deadline mentioned

            ACTION_ITEM action_type options:
            - "meeting" = coffee, call, demo, catch up
            - "follow_up" = circle back, check in, reconnect
            - "send_document" = send proposal, email deck, share info
            - "other" = anything else

            REMEMBER: Empty results are BETTER than fake results. Quality over quantity.""",
            agent=lead_generator,
            expected_output="ACCURATE lead opportunities (or empty arrays) saved to JSON file with evidence quotes and properly formatted dates",
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
        logger.info(f"Starting Lyncsea Crew for {transcript_file}")

        agents = self.create_agents()
        tasks = self.create_tasks(transcript_file, recipient_email, agents)

        crew = Crew(
            agents=list(agents),
            tasks=tasks,
            process=Process.sequential,
            verbose=False
        )

        result = crew.kickoff()
        logger.info("Lyncsea Crew completed")

        return result


def main():
    if len(sys.argv) < 3:
        print("Usage: python lead_generator.py <transcript_file> <recipient_email>")
        print("\nExample:")
        print("  python lead_generator.py data/transcripts/demo_conversation.txt user@example.com")
        sys.exit(1)

    transcript_file = sys.argv[1]
    recipient_email = sys.argv[2]

    if not Path(transcript_file).exists():
        logger.error(f"File not found: {transcript_file}")
        sys.exit(1)

    try:
        crew = LyncseaCrew()
        result = crew.run(transcript_file, recipient_email)
        logger.info(f"Final result: {result}")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()