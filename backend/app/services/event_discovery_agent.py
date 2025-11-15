#!/usr/bin/env python3
"""
Lyncsea Event Discovery Agent
Finds relevant networking events based on user profile
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from crewai import Agent, Task, Crew, Process
from crewai.tools import tool


try:
    from crewai_tools import SerperDevTool
except ImportError:
    SerperDevTool = None

load_dotenv()

# Configure logging - log to backend/logs/
log_dir = Path(__file__).parent.parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'events.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('lyncsea_events')


@tool("read_profile")
def read_profile_tool(file_path: str) -> dict:
    """Read user profile JSON"""
    with open(file_path, 'r') as f:
        return json.load(f)


@tool("save_events")
def save_events_tool(events_data: dict) -> str:
    """Save discovered events to JSON file"""
    # Save to data/events/ directory (project root)
    project_root = Path(__file__).parent.parent.parent.parent
    output_dir = project_root / "data" / "events"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f"events_{timestamp}.json"

    with open(output_file, 'w') as f:
        json.dump(events_data, f, indent=2)

    logger.info(f"Events saved to {output_file}")
    return str(output_file)


@tool("send_event_email")
def send_event_email_tool(recipient: str, subject: str, html_body: str) -> str:
    """Send HTML formatted email with event recommendations"""
    load_dotenv(override=True)
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    email_user = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    if not email_user or not email_password:
        logger.error(f"Email credentials missing")
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

    logger.info(f"Event email sent to {recipient} via {smtp_server}")
    return f"Event recommendations sent to {recipient}"


class EventDiscoveryAgent:
    """Event Discovery Agent System"""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in .env")

        os.environ["OPENAI_API_KEY"] = self.openai_api_key

    def create_agents(self):
        """Create specialized agents for event discovery"""

        # Agent 1: Profile Analyzer
        profile_analyzer = Agent(
            role='User Profile Analyst',
            goal='Analyze user profile and extract networking requirements',
            backstory='Expert at understanding professional networking needs and event preferences',
            tools=[read_profile_tool],
            verbose=False,
            allow_delegation=False
        )

        # Agent 2: Event Researcher
        search_tools = []
        if SerperDevTool:
            search_tools.append(SerperDevTool())

        event_researcher = Agent(
            role='Event Discovery Specialist',
            goal='Find relevant networking events, conferences, and meetups matching user interests',
            backstory='Expert at discovering professional events, conferences, and networking opportunities worldwide',
            tools=search_tools,
            verbose=False,
            allow_delegation=False
        )

        # Agent 3: Exhibitor Research Specialist
        exhibitor_researcher = Agent(
            role='Exhibitor Research Specialist',
            goal='Find exhibitor lists, booth details, and company information for discovered events',
            backstory='Expert at researching trade show exhibitors, conference sponsors, and booth details. Knows where to find exhibitor lists and company showcase information.',
            tools=search_tools,
            verbose=False,
            allow_delegation=False
        )

        # Agent 4: Event Curator
        event_curator = Agent(
            role='Event Curation Specialist',
            goal='Filter, rank, and present the most relevant events with exhibitor details',
            backstory='Expert at evaluating event quality, relevance, and ROI for professionals',
            tools=[save_events_tool],
            verbose=False,
            allow_delegation=False
        )

        # Agent 5: Email Sender
        email_sender = Agent(
            role='Event Communication Manager',
            goal='Create beautifully formatted HTML emails with event recommendations',
            backstory='Expert at crafting visually stunning event recommendation emails with proper formatting',
            tools=[send_event_email_tool],
            verbose=False,
            allow_delegation=False
        )

        return profile_analyzer, event_researcher, exhibitor_researcher, event_curator, email_sender

    def create_tasks(self, profile_file: str, user_email: str, agents: tuple):
        """Create tasks for event discovery"""
        profile_analyzer, event_researcher, exhibitor_researcher, event_curator, email_sender = agents

        current_date = datetime.now().strftime('%B %Y')

        # Task 1: Analyze profile
        analyze_task = Task(
            description=f"""TODAY IS {current_date}.

            Read and analyze the user profile from {profile_file}.

            Extract:
            - Professional interests and topics
            - Preferred locations for events
            - Types of events they want (conference, networking, summit, etc.)
            - What they're looking for (investments, partnerships, etc.)
            - Budget level (premium, mid-tier, free)

            Create a clear search criteria for finding events.""",
            agent=profile_analyzer,
            expected_output="Structured search criteria with topics, locations, and event types"
        )

        # Task 2: Research events
        research_task = Task(
            description=f"""TODAY IS {current_date}. Search for UPCOMING events (after {current_date}).

            Based on the user profile analysis, search online for relevant events.

            For each topic and location combination, find:
            - Upcoming conferences (next 6 months)
            - Networking events and meetups
            - Industry summits and exhibitions
            - Speaking opportunities

            Search patterns:
            - "[topic] conference [location] 2025"
            - "[topic] networking events [location]"
            - "[topic] summit [location] upcoming"
            - "crypto events Dubai" (example)
            - "AI conference Singapore 2025" (example)

            Gather:
            - Event name
            - Date and time
            - Location (venue and city)
            - Website/registration link
            - Description
            - Expected audience size
            - Ticket price (if available)

            IMPORTANT: Only include events happening AFTER {current_date}.""",
            agent=event_researcher,
            expected_output="List of discovered events with complete details",
            context=[analyze_task]
        )

        # Task 3: Research Exhibitors
        exhibitor_task = Task(
            description="""For EACH discovered event (especially conferences, trade shows, expos), research and find:

            1. **Exhibitor List**: Companies that will have booths/exhibits
            2. **For each exhibitor**:
               - Company name
               - Booth number (if available)
               - Company website
               - What they're showcasing/presenting
               - Company category (tech, finance, healthcare, etc.)
               - Contact person (if publicly available)

            Search patterns to find exhibitor info:
            - "[event name] exhibitor list"
            - "[event name] sponsors"
            - "[event name] floor plan"
            - "[event name] expo map"
            - Check event official website for exhibitor/sponsor page

            Return this data structured by event, with exhibitor arrays:
            {
                "event_name": "...",
                "exhibitors": [
                    {
                        "company": "...",
                        "booth": "...",
                        "website": "...",
                        "showcase": "...",
                        "category": "..."
                    }
                ]
            }

            If exhibitor list is not available for an event, note "Exhibitor list not yet published".""",
            agent=exhibitor_researcher,
            expected_output="Exhibitor lists with company details for discovered events",
            context=[analyze_task, research_task]
        )

        # Task 4: Curate and rank events
        curate_task = Task(
            description="""Review all discovered events WITH their exhibitor lists and create a curated list.

            Rank events by:
            1. Relevance score (1-10) based on user interests
            2. Networking potential (1-10)
            3. ROI potential (1-10)

            Group events by:
            - Must attend (high priority)
            - Should attend (medium priority)
            - Nice to attend (low priority)

            For each event provide:
            - Event name and tagline
            - Date, time, location
            - Why it's relevant to the user
            - Key topics covered
            - Expected attendees/speakers
            - Registration link
            - Estimated cost
            - Relevance score

            Save using save_events tool with structure:
            {
                "user_name": "...",
                "generated_date": "...",
                "total_events_found": N,
                "must_attend": [event objects],
                "should_attend": [event objects],
                "nice_to_attend": [event objects]
            }

            IMPORTANT: Also include exhibitor information for each event where available.""",
            agent=event_curator,
            expected_output="Curated and ranked event list with exhibitor details saved to JSON file",
            context=[analyze_task, research_task, exhibitor_task]
        )

        # Task 5: Send email
        email_task = Task(
            description=f"""TODAY IS {current_date}.

            Create and send HTML email to {user_email}.

            IMPORTANT: The html_body parameter must be ONE complete HTML string, not split into multiple parts.

            Build complete HTML with:

            1. Header section (purple background)
            2. Summary with total events found
            3. Must Attend section (red borders) - show TOP 3 events only
            4. Should Attend section (orange borders) - show TOP 3 events only
            5. Nice to Attend section (green borders) - show TOP 3 events only

            For each event show:
            - Event name
            - Date and location
            - 1-line description
            - Registration link

            Keep it SIMPLE and CLEAN. Maximum 9 events total in email.

            Call send_event_email tool with:
            - recipient: {user_email}
            - subject: "Your Personalized Event Recommendations - {current_date}"
            - html_body: ONE complete HTML string (not JSON, just HTML)""",
            agent=email_sender,
            expected_output=f"Email sent to {user_email}",
            context=[analyze_task, research_task, exhibitor_task, curate_task]
        )

        return [analyze_task, research_task, exhibitor_task, curate_task, email_task]

    def run(self, profile_file: str, user_email: str):
        """Execute event discovery workflow"""
        logger.info(f"Starting Event Discovery for {profile_file}")

        agents = self.create_agents()
        tasks = self.create_tasks(profile_file, user_email, agents)

        crew = Crew(
            agents=list(agents),
            tasks=tasks,
            process=Process.sequential,
            verbose=False
        )

        result = crew.kickoff()
        logger.info("Event Discovery completed")

        return result


def main():
    if len(sys.argv) < 3:
        print("Usage: python event_discovery.py <user_profile.json> <user_email>")
        print("\nExample:")
        print("  python event_discovery.py user_profile_example.json user@example.com")
        sys.exit(1)

    profile_file = sys.argv[1]
    user_email = sys.argv[2]

    if not Path(profile_file).exists():
        logger.error(f"Profile file not found: {profile_file}")
        sys.exit(1)

    try:
        agent = EventDiscoveryAgent()
        result = agent.run(profile_file, user_email)
        logger.info(f"Result: {result}")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()