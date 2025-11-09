from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings


class CalendarIntegrationService:
    """
    Service for integrating with Google Calendar and other calendar providers
    """

    def __init__(self):
        self.service_name = "calendar"
        self.api_version = "v3"

    def create_credentials(self, access_token: str, refresh_token: str) -> Credentials:
        """
        Create Google OAuth2 credentials from tokens

        Args:
            access_token: OAuth2 access token
            refresh_token: OAuth2 refresh token

        Returns:
            Google Credentials object
        """
        creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
        )
        return creds

    def create_meeting(
        self,
        access_token: str,
        refresh_token: str,
        title: str,
        description: str,
        start_time: datetime,
        duration_minutes: int,
        attendee_emails: List[str],
        location: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a calendar event/meeting

        Args:
            access_token: User's Google access token
            refresh_token: User's Google refresh token
            title: Meeting title
            description: Meeting description
            start_time: Meeting start time
            duration_minutes: Meeting duration in minutes
            attendee_emails: List of attendee email addresses
            location: Optional location/meeting link

        Returns:
            Dictionary with event details including meeting link
        """
        logger.info(f"Creating calendar event: {title}")

        try:
            # Create credentials
            creds = self.create_credentials(access_token, refresh_token)

            # Build Calendar API service
            service = build(self.service_name, self.api_version, credentials=creds)

            # Calculate end time
            end_time = start_time + timedelta(minutes=duration_minutes)

            # Prepare event data
            event = {
                "summary": title,
                "description": description,
                "start": {
                    "dateTime": start_time.isoformat(),
                    "timeZone": "UTC",
                },
                "end": {
                    "dateTime": end_time.isoformat(),
                    "timeZone": "UTC",
                },
                "attendees": [{"email": email} for email in attendee_emails],
                "conferenceData": {
                    "createRequest": {
                        "requestId": f"ayka-{int(datetime.utcnow().timestamp())}",
                        "conferenceSolutionKey": {"type": "hangoutsMeet"},
                    }
                },
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "email", "minutes": 24 * 60},  # 1 day before
                        {"method": "popup", "minutes": 30},  # 30 minutes before
                    ],
                },
            }

            if location:
                event["location"] = location

            # Create the event
            created_event = (
                service.events()
                .insert(
                    calendarId="primary",
                    body=event,
                    conferenceDataVersion=1,
                    sendUpdates="all",
                )
                .execute()
            )

            logger.info(f"Event created: {created_event['id']}")

            # Extract meeting link
            meeting_link = None
            if "conferenceData" in created_event:
                if "entryPoints" in created_event["conferenceData"]:
                    for entry_point in created_event["conferenceData"]["entryPoints"]:
                        if entry_point["entryPointType"] == "video":
                            meeting_link = entry_point["uri"]
                            break

            return {
                "event_id": created_event["id"],
                "event_link": created_event.get("htmlLink"),
                "meeting_link": meeting_link,
                "status": created_event["status"],
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
            }

        except HttpError as error:
            logger.error(f"Calendar API error: {error}")
            raise Exception(f"Failed to create calendar event: {error}")

        except Exception as e:
            logger.error(f"Error creating calendar event: {e}")
            raise

    def update_meeting(
        self,
        access_token: str,
        refresh_token: str,
        event_id: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update an existing calendar event

        Args:
            access_token: User's Google access token
            refresh_token: User's Google refresh token
            event_id: Calendar event ID to update
            updates: Dictionary of fields to update

        Returns:
            Updated event details
        """
        logger.info(f"Updating calendar event: {event_id}")

        try:
            creds = self.create_credentials(access_token, refresh_token)
            service = build(self.service_name, self.api_version, credentials=creds)

            # Get existing event
            event = service.events().get(calendarId="primary", eventId=event_id).execute()

            # Apply updates
            if "title" in updates:
                event["summary"] = updates["title"]
            if "description" in updates:
                event["description"] = updates["description"]
            if "start_time" in updates:
                event["start"]["dateTime"] = updates["start_time"].isoformat()
            if "duration_minutes" in updates:
                start = datetime.fromisoformat(event["start"]["dateTime"].replace("Z", "+00:00"))
                end = start + timedelta(minutes=updates["duration_minutes"])
                event["end"]["dateTime"] = end.isoformat()

            # Update the event
            updated_event = (
                service.events()
                .update(calendarId="primary", eventId=event_id, body=event, sendUpdates="all")
                .execute()
            )

            logger.info(f"Event updated: {event_id}")

            return {
                "event_id": updated_event["id"],
                "status": updated_event["status"],
            }

        except HttpError as error:
            logger.error(f"Calendar API error: {error}")
            raise Exception(f"Failed to update calendar event: {error}")

    def cancel_meeting(
        self, access_token: str, refresh_token: str, event_id: str
    ) -> bool:
        """
        Cancel a calendar event

        Args:
            access_token: User's Google access token
            refresh_token: User's Google refresh token
            event_id: Calendar event ID to cancel

        Returns:
            True if successful
        """
        logger.info(f"Cancelling calendar event: {event_id}")

        try:
            creds = self.create_credentials(access_token, refresh_token)
            service = build(self.service_name, self.api_version, credentials=creds)

            # Delete the event
            service.events().delete(
                calendarId="primary", eventId=event_id, sendUpdates="all"
            ).execute()

            logger.info(f"Event cancelled: {event_id}")
            return True

        except HttpError as error:
            logger.error(f"Calendar API error: {error}")
            raise Exception(f"Failed to cancel calendar event: {error}")

    def get_availability(
        self,
        access_token: str,
        refresh_token: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict[str, datetime]]:
        """
        Get user's availability (free time slots)

        Args:
            access_token: User's Google access token
            refresh_token: User's Google refresh token
            start_date: Start of time range
            end_date: End of time range

        Returns:
            List of free time slots
        """
        logger.info("Fetching user availability")

        try:
            creds = self.create_credentials(access_token, refresh_token)
            service = build(self.service_name, self.api_version, credentials=creds)

            # Query free/busy information
            body = {
                "timeMin": start_date.isoformat() + "Z",
                "timeMax": end_date.isoformat() + "Z",
                "items": [{"id": "primary"}],
            }

            freebusy = service.freebusy().query(body=body).execute()

            busy_slots = freebusy["calendars"]["primary"]["busy"]

            # Calculate free slots (simplified - just returns gaps between busy slots)
            free_slots = []
            current_time = start_date

            for busy_slot in busy_slots:
                busy_start = datetime.fromisoformat(busy_slot["start"].replace("Z", "+00:00"))
                if current_time < busy_start:
                    free_slots.append({"start": current_time, "end": busy_start})
                current_time = datetime.fromisoformat(busy_slot["end"].replace("Z", "+00:00"))

            # Add final free slot if there's time remaining
            if current_time < end_date:
                free_slots.append({"start": current_time, "end": end_date})

            logger.info(f"Found {len(free_slots)} free time slots")
            return free_slots

        except HttpError as error:
            logger.error(f"Calendar API error: {error}")
            raise Exception(f"Failed to fetch availability: {error}")

    def send_meeting_invite(
        self,
        match_id: int,
        user_email: str,
        matched_email: str,
        title: str,
        description: str,
        proposed_times: List[datetime],
    ) -> Dict[str, Any]:
        """
        Send meeting invite with multiple proposed time slots

        Args:
            match_id: Match ID
            user_email: Requesting user's email
            matched_email: Matched user's email
            title: Meeting title
            description: Meeting description
            proposed_times: List of proposed meeting times

        Returns:
            Dictionary with invite details
        """
        logger.info(f"Sending meeting invite for match {match_id}")

        # This is a simplified version - in production you'd:
        # 1. Store proposed times in database
        # 2. Send email notification to matched user
        # 3. Provide interface for them to accept a time
        # 4. Create actual calendar event once time is confirmed

        # For now, return a mock response
        return {
            "match_id": match_id,
            "invite_status": "sent",
            "proposed_times": [t.isoformat() for t in proposed_times],
            "message": f"Meeting invite sent to {matched_email}",
        }
