# AgentLearn
Multi-agent course recommendation system with Google Calendar integration. Built using Google ADK &amp; Gemini 2.0 Flash. Features: intelligent course search &amp; ranking, personalized learning path generation with flexible scheduling, automated calendar reminders, and memory persistence. Helps learners discover courses and stay committed to their goals.
## Problem Statement

Finding and sticking to online courses is challenging. Learners face course overload when searching through hundreds of options, spend hours on manual planning, experience low completion rates (85% of enrolled students never finish), and lack accountability structures. AgentLearn automates the entire learning journey from discovery to daily accountability.

---

## Why Multi-Agent Architecture?

Agents are the right solution because this problem requires multi-step reasoning, dynamic tool orchestration, and conversational flexibility that traditional systems can't provide. The workflow involves multiple distinct stages—gathering preferences, searching courses, ranking results, generating personalized schedules, and automating calendar events—each requiring different capabilities and context. A multi-agent architecture allows breaking this complexity into specialized sub-agents, where each focuses on one task exceptionally well while the root agent orchestrates the flow based on user intent. Agents can also dynamically decide which tools to use (web search vs. calendar API) based on conversation context, rather than following rigid scripts. This enables natural, adaptive conversations where users can change their mind or modify preferences at any point. Most importantly, the system transforms vague learning intentions into concrete, scheduled actions. By automating calendar setup, the system eliminates the planning friction that causes most people to abandon courses, turning hours of manual work into a single conversation.

---

## Features

**Intelligent Course Discovery**
- Multi-platform search across Coursera, Udemy, edX, and YouTube
- Natural language understanding for queries like "I want to learn Python as a beginner for free"
- Multi-criteria ranking based on relevance, quality indicators, budget alignment, level fit, and duration

**Personalized Learning Paths**
- Extracts actual course duration from search results
- Calculates realistic timeline based on user's weekly availability
- Creates week-by-week breakdown with specific topics per session
- Adapts to any schedule pattern (weekends, weekday evenings, custom days)

**Automated Calendar Integration**
- One-click Google Calendar synchronization
- Smart reminder events starting day before at preferred time
- Color-coded events: blue for reminders, green for study sessions
- Natural language date parsing ("this Saturday", "next Monday", specific dates)

**Conversational Memory**
- Remembers user preferences across sessions using Vertex AI Memory Bank
- No need to repeat information in subsequent conversations
- Maintains context of past course selections and schedules

---

## System Architecture

**Root Agent**: Main orchestrator handling conversation flow and delegating to specialized sub-agents

**CourseFinderPipeline** (Sequential Agent):
- Preference Collector: Gathers user requirements (topic, level, budget, format) through natural conversation
- Search Agent: Uses web search to find relevant courses across platforms
- Ranking Agent: Evaluates and ranks courses using multi-criteria analysis, presents top 3-5 recommendations with reasoning

**Learning Path Generator**: Creates personalized week-by-week study schedules based on course duration and user's time availability

**Calendar Agent**: Automates Google Calendar integration by creating study session blocks and reminder notifications

The sub-agents work together in a sequential pipeline for course discovery, then individually for path generation and calendar setup. Memory persistence is handled through Vertex AI Memory Bank.

---

## Demo Workflow

**Course Discovery (1-2 minutes)**

User: "I want to learn Python as a beginner for free"

System searches web, finds 8-10 courses, ranks them by relevance, quality, and user fit, then shows top 5 courses with platform, duration, price, and direct links.

**Learning Path Creation (1-2 minutes)**

User: "I'll take Python for Everybody"

System extracts course duration (e.g., 40 hours), asks about weekly availability, calculates timeline (total_hours ÷ weekly_hours = weeks_needed with buffer), asks for preferred study days and times, calculates hours per session, then creates personalized 8-week schedule with week-by-week breakdown and realistic milestones.

**Calendar Automation (2-3 minutes)**

User: "Yes, add to calendar"

System reads learning path schedule, asks for start date (accepts natural language), asks for timezone (converts "Pacific" to America/Los_Angeles), asks for reminder time (e.g., "8 PM"), verifies calculated dates with user, then creates calendar events.

For an 8-week course with 2 study days per week, creates 16 reminder events (blue, starting day before at preferred time, ending 1 hour before study session) and 16 study session events (green, blocking actual study time with 15-minute advance popup). Total: 32 calendar events automatically created.

**Ongoing Support**

System remembers course selection and schedule. User can check progress, adjust timeline, or get recommendations for next course. Memory persists across sessions for continuity.

---

## Tech Stack

**Core Framework**: Google Agent Development Kit (ADK) for multi-agent orchestration, Gemini 2.0 Flash for natural language understanding and reasoning

**Agent Architecture**: LlmAgent for conversational agents (root, preference_collector, ranking, learning_path, calendar), SequentialAgent for CourseFinderPipeline, FunctionTool for custom Google Calendar API integration

**APIs and Services**: Google Calendar API for event creation, Web Search Tool (built-in ADK) for course discovery, Vertex AI Memory Bank for persistent memory across conversations

**Authentication**: OAuth 2.0 for secure Google Calendar access with token management

**Development Tools**: Python 3.9+, python-dotenv for environment variable management, Google Cloud Platform for project hosting

**Key Implementation Decisions**: Sequential agents for course discovery pipeline ensure logical flow, custom calendar tool with sophisticated date calculation logic handles flexible schedules, memory callback automatically saves conversations to Memory Bank, preload memory tool loads context before queries, natural language parsing in calendar agent handles diverse date/time formats.

