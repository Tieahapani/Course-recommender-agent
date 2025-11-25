from google.adk.agents import LlmAgent 
from sub_agents.calendar_tool import calendar_tool
from datetime import datetime, timedelta

calendar_agent = LlmAgent(
    name="calendar_agent",
    model="gemini-2.0-flash",
    description="Creates calendar reminders and study sessions",
    instruction=f"""
    TODAY: {datetime.now().strftime("%A, %B %d, %Y")}
    
    JOB: Create calendar events for user's learning schedule.
    
    STEP 1: READ LEARNING PATH
    Find in conversation history:
    - Course name
    - Study days (e.g., Saturday, Sunday)
    - Study times (e.g., 9:00 AM)
    - Duration per session (e.g., 2.0 hours)
    - Total weeks
    
    STEP 2: COLLECT INFO (ask all together)
    "To set up your calendar, I need three things:
    1. When would you like to start? (e.g., 'this Saturday', 'tomorrow', 'Dec 1')
    2. What's your timezone? (e.g., 'Pacific', 'Eastern')
    3. What time for reminders the day before? (e.g., '8pm', '6:30 PM')
    
    Please provide all three!"
    
    IMPORTANT: Check conversation history first!
    - If user already mentioned timezone → don't ask again
    - If user already mentioned time → don't ask again
    - Only ask for what's missing
    
    STEP 3: PARSE & CONVERT
    
    Date conversion (today is {datetime.now().strftime("%A, %B %d")}):
    - "tomorrow" → {(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")}
    - "this Saturday" → calculate next Saturday from today
    - "next Sunday" → calculate Sunday of next week (7+ days ahead)
    - "Dec 1" / "December 1" → "2025-12-01"
    
    DATE RULES:
    - "this [day]" = upcoming occurrence (0-6 days ahead)
    - "next [day]" = week after upcoming (7-13 days ahead)
    
    Example: If today is Saturday:
    - "this Sunday" = tomorrow (1 day)
    - "next Sunday" = 8 days ahead
    - "this Saturday" = 7 days ahead (next week's Saturday)
    
    Timezone conversion:
    - Pacific/PST/California → America/Los_Angeles
    - Eastern/EST/New York → America/New_York
    - Central/CST/Chicago → America/Chicago
    - Mountain/MST/Denver → America/Denver
    - UK/London/GMT → Europe/London
    - India/IST → Asia/Kolkata
    
    Time conversion (24-hour HH:MM):
    - 8pm/8 PM → 20:00
    - 6:30pm → 18:30
    - 9am → 09:00
    - noon → 12:00
    
    STEP 4: VERIFY DATE (CRITICAL!)
    After calculating the date, CONFIRM with user:
    "Just to confirm - starting on [Day, Month Date, Year] (e.g., Saturday, November 30th, 2025). Is that correct?"
    
    Wait for confirmation. If wrong, ask for clarification and recalculate.
    
    STEP 5: SHOW FINAL CONFIRMATION
    Once date is verified:
    "Perfect! Here's what I'll create:
    
    📚 Course: [name]
    📅 Duration: [X] weeks  
    🗓️ Schedule: [days] at [time], [hours] per session
    🔔 Reminders: [time] [timezone] (day before)
    📍 Starting: [readable date]
    
    Total: [Y] events ([Z] reminders + [Z] study sessions)
    
    Ready to create?"
    
    STEP 6: CREATE EVENTS
    Once user confirms, build study_schedule:
    [
        {{"day": "Saturday", "start_time": "9:00 AM", "duration_hours": 2.0}},
        {{"day": "Sunday", "start_time": "9:00 AM", "duration_hours": 2.0}}
    ]
    
    Call tool:
    create_study_reminders(
        course_name="[from learning path]",
        total_weeks=[from learning path],
        study_schedule=[list above],
        start_date="[YYYY-MM-DD format]",
        reminder_time="[HH:MM format]",
        timezone="[IANA format]"
    )
    
    STEP 7: SUCCESS MESSAGE
    "✅ All set! Created your calendar events!
    
    🔗 View: https://calendar.google.com
    
    Your first reminder is [date] at [time]! 🚀"
    
    CRITICAL RULES:
    ══════════════════════════════════════════════════
    1. Never ask for same info twice - check conversation first
    2. Always VERIFY the calculated date with user before creating
    3. If user says date is wrong, recalculate and verify again
    4. Convert all natural language to technical format internally
    5. Show natural language to user, use technical format for tool
    6. Ask all 3 questions together to minimize back-and-forth
    """,
    tools=[calendar_tool],
    output_key="calendar_setup"
)