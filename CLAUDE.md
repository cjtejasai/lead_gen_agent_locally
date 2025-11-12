# AYKA Lead Generation - Agent System

## Two Main Workflows

### 1. Lead Generation (ayka_crew.py)
Process conversation transcripts → extract leads → send email
- **Transcript Analyst**: Reads and parses conversation transcripts
- **Lead Generation Specialist**: Identifies opportunities and matches needs/offers
- **Contact Research Specialist**: Finds LinkedIn profiles, emails, company websites
- **Communication Manager**: Sends HTML formatted emails with color coding

### 2. Event Discovery (event_discovery.py)
User profile → discover events → curate recommendations
- **Profile Analyst**: Analyzes user interests and networking goals
- **Event Discovery Specialist**: Searches for relevant events online
- **Event Curator**: Ranks and filters events by relevance

## Setup

```bash
pip install -r agent_requirements.txt
```

## Environment Variables Required

```bash
OPENAI_API_KEY=sk-...        # OpenAI API key
EMAIL_USER=your@gmail.com    # Gmail address
EMAIL_PASSWORD=app-password  # Gmail app password (not regular password)
SERPER_API_KEY=...           # Serper API for web search (get from serper.dev)
```

## Usage

### Lead Generation from Transcripts
```bash
python ayka_crew.py <transcript_file> <recipient_email>
```
Example:
```bash
python ayka_crew.py transcripts/demo_conversation.txt leads@company.com
```

### Event Discovery for Networking
```bash
python event_discovery.py <user_profile.json> <user_email>
```
Example:
```bash
python event_discovery.py user_profile_example.json user@example.com
```

## Output

- **Logs**: `ayka_agent.log` - All agent activities and errors
- **Leads Data**: `leads_data/leads_TIMESTAMP.json` - Structured lead information
- **Email**: Sent to specified recipient with insights

## Agent Flow

Sequential process:
1. Transcript Analyst reads file → extracts structured data
2. Lead Generator uses analysis → identifies opportunities → saves JSON
3. Contact Researcher finds LinkedIn, emails, websites for key people
4. Communication Manager creates HTML email with color coding → sends via SMTP

## Important Notes

- No mock code - all functions are real implementations
- Logging configured for both file and console output
- Agents use tools with actual side effects (file I/O, SMTP)
- Gmail requires app-specific password: https://support.google.com/accounts/answer/185833