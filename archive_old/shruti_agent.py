#!/usr/bin/env python3
"""
Shruti Agent - AYKA Lead Generation Intelligence
Processes conversation transcripts and sends actionable insights
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import anthropic

load_dotenv()


class ShrutiAgent:
    """
    AI Agent for analyzing networking conversations and generating lead insights
    """

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.email_user = os.getenv("EMAIL_USER")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.recipient = os.getenv("RECIPIENT_EMAIL", self.email_user)

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env")

    def process(self, transcript_file):
        """Process transcript and send insights"""
        # Read transcript
        with open(transcript_file, 'r') as f:
            content = f.read()

        # Extract speaker count
        speakers = len(set(line.split(']')[0].replace('[', '')
                          for line in content.split('\n')
                          if line.startswith('[SPEAKER_')))

        # Analyze with AI
        insights = self._analyze(content)

        # Send email
        subject = f"🎯 Lead Insights - {speakers} Speakers - {datetime.now().strftime('%d %b')}"
        self._send_email(subject, insights, transcript_file)

        return insights

    def _analyze(self, transcript):
        """Core AI analysis"""
        client = anthropic.Anthropic(api_key=self.api_key)

        prompt = f"""Analyze this networking event conversation for lead generation opportunities.

TRANSCRIPT:
{transcript}

Provide:

1. SPEAKERS & ROLES
Brief role of each speaker

2. KEY TOPICS
Main discussion topics and industries

3. PEOPLE & COMPANIES
Names, companies, skills, products mentioned

4. NEEDS & OFFERS
- What each speaker is LOOKING FOR
- What each speaker is OFFERING

5. LEAD OPPORTUNITIES
Specific connections or matches that could be made

6. ACTION ITEMS
Concrete next steps and follow-ups

Keep it concise and actionable."""

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    def _send_email(self, subject, body, transcript_file):
        """Send email with insights"""
        if not self.email_password:
            print("\n" + "="*70)
            print(body)
            print("="*70)
            print("\n⚠️  Email not configured. Add EMAIL_USER and EMAIL_PASSWORD to .env")
            return

        msg = MIMEMultipart()
        msg['From'] = self.email_user
        msg['To'] = self.recipient
        msg['Subject'] = subject

        email_body = f"""🎙️ AYKA LEAD GENERATION INSIGHTS
{'='*70}

{body}

{'='*70}
Transcript: {transcript_file}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        msg.attach(MIMEText(email_body, 'plain'))

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()
            print(f"✅ Insights emailed to {self.recipient}")
        except Exception as e:
            print(f"✗ Email failed: {e}")
            print("\n" + "="*70)
            print(email_body)
            print("="*70)


def main():
    if len(sys.argv) < 2:
        print("Usage: python shruti_agent.py <transcript_file>")
        print("Example: python shruti_agent.py transcripts/transcript_20251109_175417.txt")
        sys.exit(1)

    transcript_file = sys.argv[1]

    if not Path(transcript_file).exists():
        print(f"✗ File not found: {transcript_file}")
        sys.exit(1)

    agent = ShrutiAgent()
    agent.process(transcript_file)


if __name__ == "__main__":
    main()