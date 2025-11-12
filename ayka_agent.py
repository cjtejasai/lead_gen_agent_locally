#!/usr/bin/env python3
"""
AYKA AI Agent - OpenAI Function Calling Demo
Analyzes conversation transcripts and sends email notifications
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


# Function definitions for OpenAI
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "send_email_notification",
            "description": "Send an email notification with lead generation insights from a conversation",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient": {
                        "type": "string",
                        "description": "Email address of the recipient"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject line"
                    },
                    "body": {
                        "type": "object",
                        "description": "Email body content",
                        "properties": {
                            "summary": {
                                "type": "string",
                                "description": "Brief summary of the conversation"
                            },
                            "speakers": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "role": {"type": "string"},
                                        "company": {"type": "string"},
                                        "interests": {"type": "array", "items": {"type": "string"}}
                                    }
                                },
                                "description": "List of speakers identified in the conversation"
                            },
                            "opportunities": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string"},
                                        "description": {"type": "string"},
                                        "priority": {"type": "string", "enum": ["high", "medium", "low"]}
                                    }
                                },
                                "description": "Lead generation opportunities identified"
                            },
                            "action_items": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific action items and follow-ups"
                            }
                        },
                        "required": ["summary", "speakers", "opportunities", "action_items"]
                    }
                },
                "required": ["recipient", "subject", "body"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_lead_data",
            "description": "Save extracted lead data to a JSON file for further processing",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the output file"
                    },
                    "leads": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "company": {"type": "string"},
                                "role": {"type": "string"},
                                "needs": {"type": "array", "items": {"type": "string"}},
                                "offers": {"type": "array", "items": {"type": "string"}},
                                "contact_priority": {"type": "string"}
                            }
                        },
                        "description": "List of lead information"
                    }
                },
                "required": ["filename", "leads"]
            }
        }
    }
]


class AYKAAgent:
    """AI Agent using OpenAI function calling for lead generation"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")

        self.client = OpenAI(api_key=self.api_key)
        self.recipient_email = os.getenv("RECIPIENT_EMAIL", "demo@example.com")

    def read_transcript(self, transcript_file):
        """Read transcript file"""
        with open(transcript_file, 'r') as f:
            return f.read()

    def send_email_notification(self, recipient, subject, body):
        """Function to send email (mock for demo)"""
        print("\n" + "="*80)
        print("📧 EMAIL NOTIFICATION")
        print("="*80)
        print(f"\nTo: {recipient}")
        print(f"Subject: {subject}\n")
        print("-"*80)

        # Format email body
        print(f"\n{body['summary']}\n")

        print("\n👥 SPEAKERS IDENTIFIED:")
        for i, speaker in enumerate(body.get('speakers', []), 1):
            print(f"\n{i}. {speaker.get('name', 'Unknown')}")
            if speaker.get('role'):
                print(f"   Role: {speaker['role']}")
            if speaker.get('company'):
                print(f"   Company: {speaker['company']}")
            if speaker.get('interests'):
                print(f"   Interests: {', '.join(speaker['interests'])}")

        print("\n\n🎯 OPPORTUNITIES:")
        for i, opp in enumerate(body.get('opportunities', []), 1):
            priority_emoji = "🔴" if opp.get('priority') == 'high' else "🟡" if opp.get('priority') == 'medium' else "🟢"
            print(f"\n{i}. {priority_emoji} {opp.get('type', 'Unknown')}")
            print(f"   {opp.get('description', '')}")

        print("\n\n✅ ACTION ITEMS:")
        for i, action in enumerate(body.get('action_items', []), 1):
            print(f"{i}. {action}")

        print("\n" + "="*80)

        return {
            "status": "success",
            "message": f"Email prepared for {recipient}"
        }

    def save_lead_data(self, filename, leads):
        """Function to save lead data"""
        output_dir = Path("leads_data")
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / filename

        data = {
            "generated_at": datetime.now().isoformat(),
            "leads": leads
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\n💾 Lead data saved to: {output_file}")

        return {
            "status": "success",
            "file": str(output_file),
            "leads_count": len(leads)
        }

    def execute_function(self, function_name, arguments):
        """Execute the requested function"""
        if function_name == "send_email_notification":
            return self.send_email_notification(**arguments)
        elif function_name == "save_lead_data":
            return self.save_lead_data(**arguments)
        else:
            return {"status": "error", "message": f"Unknown function: {function_name}"}

    def process_transcript(self, transcript_file):
        """Process transcript using OpenAI function calling"""

        print("\n" + "="*80)
        print("🤖 AYKA AI AGENT - Processing Transcript")
        print("="*80)
        print(f"\nFile: {transcript_file}")

        # Read transcript
        transcript_content = self.read_transcript(transcript_file)
        print(f"Length: {len(transcript_content)} characters\n")

        # Create the prompt
        system_prompt = """You are AYKA, an AI assistant specialized in lead generation from networking event conversations.

Analyze the provided conversation transcript and:
1. Identify all speakers, their roles, companies, and interests
2. Extract lead generation opportunities (partnerships, investments, hiring, etc.)
3. Determine action items and follow-ups
4. Use the send_email_notification function to prepare an email summary
5. Use the save_lead_data function to save structured lead information

Be specific and actionable in your analysis."""

        user_prompt = f"""Analyze this networking conversation transcript and extract lead generation insights:

TRANSCRIPT:
{transcript_content}

Use the available functions to:
1. Send an email notification to '{self.recipient_email}' with key insights
2. Save the extracted lead data for CRM integration"""

        print("🔄 Analyzing with OpenAI GPT-4...")

        # Call OpenAI with function calling
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )

        # Process function calls
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            print(f"\n✅ AI requested {len(tool_calls)} function call(s)\n")

            # Execute each function call
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                print(f"\n🔧 Executing: {function_name}")
                result = self.execute_function(function_name, function_args)

                # Add function result to messages
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call.model_dump()]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(result)
                })

            # Get final response after function execution
            final_response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages
            )

            final_message = final_response.choices[0].message.content
            if final_message:
                print("\n" + "="*80)
                print("💬 AI SUMMARY")
                print("="*80)
                print(f"\n{final_message}\n")

        else:
            print("\n⚠️  No function calls were made")
            print(f"\nResponse: {response_message.content}")

        print("\n" + "="*80)
        print("✅ Processing Complete")
        print("="*80)


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("\n🎯 AYKA AI Agent - OpenAI Function Calling Demo")
        print("="*60)
        print("\nUsage: python ayka_agent.py <transcript_file> [recipient_email]")
        print("\nExample:")
        print("  python ayka_agent.py transcripts/demo_conversation.txt")
        print("  python ayka_agent.py transcripts/demo_conversation.txt user@example.com")
        print("\nAvailable transcripts:")

        transcript_dir = Path("transcripts")
        if transcript_dir.exists():
            transcripts = sorted(transcript_dir.glob("*.txt"), reverse=True)[:5]
            for t in transcripts:
                print(f"  - {t}")

        sys.exit(1)

    transcript_file = sys.argv[1]
    custom_recipient = sys.argv[2] if len(sys.argv) > 2 else None

    if not Path(transcript_file).exists():
        print(f"❌ File not found: {transcript_file}")
        sys.exit(1)

    try:
        agent = AYKAAgent()

        # Override recipient if provided
        if custom_recipient:
            agent.recipient_email = custom_recipient
            print(f"📧 Using custom recipient: {custom_recipient}\n")
        else:
            print(f"📧 Using default recipient: {agent.recipient_email}\n")

        agent.process_transcript(transcript_file)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
