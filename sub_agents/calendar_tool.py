# sub_agents/calendar_tool.py

from google.adk.tools import FunctionTool
from datetime import datetime, timedelta
import os.path
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """
    Authenticates and returns Google Calendar service.
    This will open a browser window for OAuth the first time.
    """
    creds = None
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root
    project_root = os.path.dirname(script_dir)
    
    token_path = os.path.join(project_root, 'token.pickle')
    credentials_path = os.path.join(project_root, 'credentials.json')
    
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(
                    f"credentials.json not found at {credentials_path}. Please download OAuth credentials from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('calendar', 'v3', credentials=creds)

def parse_time(time_str: str) -> tuple:
    """
    Parse time string like "9:00 AM", "11 AM", "19:30" to (hour, minute)
    
    Args:
        time_str: Time string in various formats
    
    Returns:
        tuple: (hour, minute) in 24-hour format
    """
    try:
        time_clean = time_str.upper().replace(" ", "")
        
        if "AM" in time_clean or "PM" in time_clean:
            # 12-hour format
            time_part = time_clean.replace("AM", "").replace("PM", "")
            if ":" in time_part:
                hour, minute = map(int, time_part.split(":"))
            else:
                hour = int(time_part)
                minute = 0
            
            # Convert to 24-hour
            if "PM" in time_clean and hour != 12:
                hour += 12
            elif "AM" in time_clean and hour == 12:
                hour = 0
        else:
            # 24-hour format
            if ":" in time_clean:
                hour, minute = map(int, time_clean.split(":"))
            else:
                hour = int(time_clean)
                minute = 0
        
        return (hour, minute)
    except:
        # Default to 9 AM if parsing fails
        return (9, 0)


def create_study_reminders(
    course_name: str,
    total_weeks: int,
    study_schedule: list,
    start_date: str,
    reminder_time: str = "20:00",
    timezone: str = "America/Los_Angeles"
) -> dict:
    """
    Creates Google Calendar reminders and study session events.
    
    IMPORTANT: start_date should be the date of the FIRST study session.
    
    Args:
        course_name: Name of the course
        total_weeks: How many weeks the course will take
        study_schedule: List of dicts, e.g.:
            [
                {"day": "Friday", "start_time": "9:00 AM", "duration_hours": 2.75},
                {"day": "Saturday", "start_time": "9:00 AM", "duration_hours": 2.75},
                {"day": "Sunday", "start_time": "9:00 AM", "duration_hours": 2.75}
            ]
        start_date: Date of the FIRST study session (YYYY-MM-DD format)
        reminder_time: When to send reminder (HH:MM format, default "20:00" = 8 PM)
        timezone: IANA timezone (default "America/Los_Angeles")
    
    Returns:
        Dictionary with status and created calendar events
    """
    
    # ═══════════════════════════════════════════════════════
    # 🔧 DEBUG: Print what the agent passed to this function
    # ═══════════════════════════════════════════════════════
    print("\n" + "="*70)
    print("🔧 DEBUG: create_study_reminders called with:")
    print("="*70)
    print(f"📚 course_name: {course_name}")
    print(f"📅 total_weeks: {total_weeks}")
    print(f"🗓️  study_schedule: {study_schedule}")
    print(f"📍 start_date: {start_date}")
    print(f"⏰ reminder_time: {reminder_time}")
    print(f"🌍 timezone: {timezone}")
    print("="*70 + "\n")
    
    try:
        # Get authenticated Calendar service
        service = get_calendar_service()
        
        # Parse start date
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        print(f"✅ Start date: {start_datetime.strftime('%A, %B %d, %Y')}")
        
        # Parse reminder time (HH:MM format)
        try:
            reminder_hour, reminder_minute = map(int, reminder_time.split(":"))
            if not (0 <= reminder_hour <= 23 and 0 <= reminder_minute <= 59):
                raise ValueError("Invalid time")
        except:
            # Default to 8 PM if invalid format
            reminder_hour, reminder_minute = 20, 0
        
        print(f"✅ Reminder time: {reminder_hour}:{reminder_minute:02d}\n")
        
        # Day name to number mapping (Monday=0, Sunday=6)
        day_map = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
            "Friday": 4, "Saturday": 5, "Sunday": 6
        }
        
        # Get the day of week for the start date
        start_day_of_week = start_datetime.weekday()
        start_day_name = list(day_map.keys())[start_day_of_week]
        
        print(f"📌 Start date is a {start_day_name}")
        print(f"📌 Study schedule has: {[s['day'] for s in study_schedule]}\n")
        
        # Find which session in the schedule matches the start date
        matching_session_idx = None
        for idx, session in enumerate(study_schedule):
            if session['day'] == start_day_name:
                matching_session_idx = idx
                break
        
        if matching_session_idx is None:
            raise ValueError(
                f"Start date is {start_day_name}, but schedule doesn't include {start_day_name}. "
                f"Schedule has: {[s['day'] for s in study_schedule]}"
            )
        
        print(f"✅ Matched with session #{matching_session_idx + 1}: {start_day_name}\n")
        
        events_created = []
        current_date = start_datetime
        
        # For each week
        for week_num in range(total_weeks):
            print(f"\n📆 Week {week_num + 1}:")
            
            # Process sessions starting from matching one, then continuing in order
            for i in range(len(study_schedule)):
                # Calculate which session to process
                session_idx = (matching_session_idx + i) % len(study_schedule)
                session = study_schedule[session_idx]
                
                study_day = session["day"]
                study_time_str = session["start_time"]
                duration_hours = session["duration_hours"]
                
                # For the very first session, use start_datetime
                if week_num == 0 and i == 0:
                    study_date = start_datetime
                else:
                    # Calculate next occurrence of this day
                    target_day_num = day_map[study_day]
                    current_day_num = current_date.weekday()
                    
                    # Days until next occurrence
                    days_ahead = (target_day_num - current_day_num) % 7
                    if days_ahead == 0:
                        days_ahead = 7  # Next week, same day
                    
                    study_date = current_date + timedelta(days=days_ahead)
                
                # Update current_date for next iteration
                current_date = study_date
                
                print(f"  📖 {study_day} study session:")
                print(f"     Study date: {study_date.strftime('%Y-%m-%d (%A)')}")
                print(f"     Study time: {study_time_str}")
                print(f"     Duration: {duration_hours} hours")
                
                # Parse study time
                study_hour, study_minute = parse_time(study_time_str)
                
                # CREATE REMINDER EVENT
                reminder_datetime = study_date - timedelta(days=1)
                reminder_datetime = reminder_datetime.replace(
                    hour=reminder_hour,
                    minute=reminder_minute,
                    second=0
                )
                
                study_datetime = study_date.replace(
                    hour=study_hour,
                    minute=study_minute,
                    second=0
                )
                reminder_end = study_datetime - timedelta(hours=1)
                
                print(f"     Reminder: {reminder_datetime.strftime('%A, %b %d at %I:%M %p')} → {reminder_end.strftime('%I:%M %p')}")
                
                reminder_day_name = list(day_map.keys())[reminder_datetime.weekday()]
                study_end = study_datetime + timedelta(hours=duration_hours)
                
                reminder_event = {
                    'summary': f'📚 Reminder: Study {course_name} Tomorrow!',
                    'description': f'Hey! Tomorrow is {study_day} - time for your Week {week_num + 1} study session!\n\n📅 Study Time: {study_time_str} - {study_end.strftime("%I:%M %p")}\n⏱️ Duration: {duration_hours} hours\n\n🚀 Get ready to learn!',
                    'start': {
                        'dateTime': reminder_datetime.isoformat(),
                        'timeZone': timezone,
                    },
                    'end': {
                        'dateTime': reminder_end.isoformat(),
                        'timeZone': timezone,
                    },
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'popup', 'minutes': 0},
                            {'method': 'email', 'minutes': 0},
                        ],
                    },
                    'colorId': '9',
                }
                
                created_reminder = service.events().insert(calendarId='primary', body=reminder_event).execute()
                print(f"     ✅ Reminder created")
                
                # CREATE STUDY SESSION EVENT
                study_event = {
                    'summary': f'📖 Study: {course_name} - Week {week_num + 1}',
                    'description': f'Week {week_num + 1} study session for {course_name}\n\n⏱️ {duration_hours} hours\n\n🎯 Focus and learn! You\'ve got this! 💪',
                    'start': {
                        'dateTime': study_datetime.isoformat(),
                        'timeZone': timezone,
                    },
                    'end': {
                        'dateTime': study_end.isoformat(),
                        'timeZone': timezone,
                    },
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'popup', 'minutes': 15},
                        ],
                    },
                    'colorId': '10',
                }
                
                created_study = service.events().insert(calendarId='primary', body=study_event).execute()
                print(f"     ✅ Study session created\n")
                
                # Store both events
                events_created.append({
                    "week": week_num + 1,
                    "study_day": study_day,
                    "reminder_date": reminder_datetime.strftime("%Y-%m-%d"),
                    "reminder_day": reminder_day_name,
                    "reminder_start_time": reminder_datetime.strftime("%I:%M %p"),
                    "reminder_end_time": reminder_end.strftime("%I:%M %p"),
                    "study_date": study_date.strftime("%Y-%m-%d"),
                    "study_start_time": study_datetime.strftime("%I:%M %p"),
                    "study_end_time": study_end.strftime("%I:%M %p"),
                    "study_duration": f"{duration_hours} hours",
                    "timezone": timezone,
                    "reminder_link": created_reminder.get('htmlLink'),
                    "study_link": created_study.get('htmlLink'),
                    "reminder_event_id": created_reminder.get('id'),
                    "study_event_id": created_study.get('id')
                })
        
        # Format output
        schedule_by_week = {}
        for event in events_created:
            week = event['week']
            if week not in schedule_by_week:
                schedule_by_week[week] = []
            schedule_by_week[week].append(
                f"  📅 {event['study_day']} {event['study_date']}:\n"
                f"    • Reminder: {event['reminder_day']} {event['reminder_start_time']} - {event['reminder_end_time']}\n"
                f"    • Study: {event['study_start_time']} - {event['study_end_time']} ({event['study_duration']})"
            )
        
        schedule_preview = "\n".join([
            f"Week {week}:\n" + "\n".join(details)
            for week, details in schedule_by_week.items()
        ])
        
        total_events = len(events_created) * 2
        
        print("\n" + "="*70)
        print(f"✅ SUCCESS: Created {total_events} calendar events!")
        print("="*70 + "\n")
        
        return {
            "status": "success",
            "message": f"✅ Created {total_events} calendar events ({len(events_created)} reminders + {len(events_created)} study sessions)!",
            "events": events_created,
            "schedule_preview": schedule_preview,
            "summary": {
                "total_weeks": total_weeks,
                "sessions_per_week": len(study_schedule),
                "total_reminders": len(events_created),
                "total_study_sessions": len(events_created),
                "total_events": total_events,
                "first_reminder": events_created[0]["reminder_date"] if events_created else None,
                "last_study_session": events_created[-1]["study_date"] if events_created else None,
                "timezone": timezone,
                "calendar_link": "https://calendar.google.com"
            }
        }
        
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        return {"status": "error", "message": str(e)}
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": f"Failed to create calendar events: {str(e)}"}


# Create the ADK FunctionTool
calendar_tool = FunctionTool(create_study_reminders)
