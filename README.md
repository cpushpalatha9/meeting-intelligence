# 🧠 Meeting Intelligence System

An AI-powered Meeting Intelligence System that automatically converts
meeting audio, video, or transcripts into structured and actionable
meeting information.

The system combines **Faster-Whisper** for speech-to-text transcription,
**Google Gemini** for intelligent meeting analysis, **Pydantic** for
structured data validation, **SQLite** for persistence, **Streamlit**
for the user interface, and **FastAPI** for REST API access.

------------------------------------------------------------------------

## 📌 Project Overview

Meetings contain valuable information such as discussion points,
decisions, tasks, responsibilities, and deadlines. Manually identifying
and documenting this information can be time-consuming and error-prone.

The Meeting Intelligence System automates this process by transforming
unstructured meeting conversations into structured meeting intelligence.

### Core capabilities

-   🎙️ Audio/video meeting transcription
-   📝 Transcript processing
-   🧠 AI-powered meeting analysis using Google Gemini
-   📌 Meeting summarization
-   🔑 Key point extraction
-   ✅ Decision extraction
-   📋 Action item extraction
-   👥 Participant identification
-   🎯 Responsibility mapping
-   📅 Deadline extraction
-   🚦 Priority and status tracking
-   💾 SQLite persistence
-   📚 Meeting history
-   🚀 FastAPI REST API
-   🖥️ Streamlit web interface

------------------------------------------------------------------------

# ✨ Key Features

## 🎙️ Audio and Video Processing

The system accepts meeting recordings and uses Faster-Whisper to convert
spoken content into text.

Typical supported formats include:

-   MP3
-   WAV
-   MP4
-   M4A

## 📝 Automatic Transcription

Faster-Whisper converts spoken meeting content into a textual transcript
and detects the language.

## 🧠 AI-Powered Meeting Analysis

Google Gemini analyzes the transcript and produces structured meeting
intelligence using a reusable prompt.

The prompt instructs the model to use only information supported by the
transcript and avoid inventing missing information.

## 📌 Meeting Summarization

Generates a concise factual summary of the meeting.

## 🔑 Key Point Extraction

Extracts important discussion points from the meeting.

## ✅ Decision Extraction

Identifies actual decisions while avoiding treating suggestions and
opinions as decisions.

## 📋 Action Item Extraction

Extracts genuine tasks and records:

-   Task
-   Assignee
-   Deadline
-   Priority
-   Status

## 👥 Participant Identification

Identifies participants explicitly available in the transcript and
avoids duplicate or invented participants.

## 🎯 Responsibility Mapping

Links responsibilities to the correct participant.

Example:

``` text
Ravi  → API Integration
Priya → UI Testing
```

## 📅 Deadline Extraction

Extracts deadlines when supported by the transcript, such as Thursday,
Friday, tomorrow evening, or next Monday.

## 🚦 Priority and Status

Supported priorities:

-   High
-   Medium
-   Low

Supported statuses:

-   Pending
-   In Progress
-   Completed

## 💾 SQLite Persistence

Processed meetings are stored in SQLite for future access.

## 📚 Meeting History

Previously processed meetings can be selected and reviewed from the
Streamlit Meeting History page.

## 🚀 REST API

FastAPI provides programmatic access to the meeting-processing pipeline.

------------------------------------------------------------------------

# 🏗️ System Architecture

``` text
                         ┌──────────────────────┐
                         │        User          │
                         └──────────┬───────────┘
                                    │
                   ┌────────────────┴────────────────┐
                   │                                 │
                   ▼                                 ▼
          ┌─────────────────┐               ┌─────────────────┐
          │    Streamlit    │               │     FastAPI     │
          │       UI        │               │       API       │
          └────────┬────────┘               └────────┬────────┘
                   │                                 │
                   └────────────────┬────────────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Audio / Video /      │
                         │ Existing Transcript  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Faster-Whisper     │
                         │    Transcription     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Transcript Validation│
                         │ & Long Text Handling │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Google Gemini     │
                         │    LLM Processing    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Structured JSON   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Pydantic Validation  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                  ┌────────────────────────────────────┐
                  │       Meeting Intelligence         │
                  │ Summary • Key Points • Decisions   │
                  │ Actions • Participants • Deadlines │
                  │ Responsibilities • Priority/Status │
                  └────────────────┬───────────────────┘
                                   │
                                   ▼
                         ┌──────────────────────┐
                         │       SQLite         │
                         │      Database        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Meeting History    │
                         └──────────────────────┘
```

------------------------------------------------------------------------

# 🔄 End-to-End Processing Workflow

``` text
Upload Meeting Audio/Video
            ↓
Receive Uploaded File
            ↓
Faster-Whisper Transcription
            ↓
Generate Transcript
            ↓
Validate Transcript
            ↓
Split Long Transcript if Required
            ↓
Send Transcript to Google Gemini
            ↓
Generate Structured JSON
            ↓
Clean AI Response
            ↓
Validate using Pydantic
            ↓
Clean Participants and Action Items
            ↓
Generate Meeting Intelligence
            ↓
Save to SQLite
            ↓
Display Results in Streamlit
            ↓
Store in Meeting History
```

------------------------------------------------------------------------

# 🛠️ Technology Stack

  Technology         Purpose
  ------------------ ------------------------------
  Python             Core programming language
  Streamlit          Web user interface
  FastAPI            REST API service
  Google Gemini      AI-powered meeting analysis
  Faster-Whisper     Speech-to-text transcription
  Pydantic           Structured output validation
  SQLite             Data persistence
  python-dotenv      Environment configuration
  Uvicorn            FastAPI server
  Python Multipart   File upload handling

------------------------------------------------------------------------

# 📂 Project Structure

``` text
meeting-intelligence/
│
├── prompts/
│   ├── __init__.py
│   └── meeting_prompt.py
│
├── schemas/
│   ├── __init__.py
│   └── meeting_schema.py
│
├── services/
│   ├── __init__.py
│   ├── database_service.py
│   ├── llm_service.py
│   ├── meeting_service.py
│   └── transcription_service.py
│
├── app.py
├── api.py
├── requirements.txt
├── test_llm.py
├── .gitignore
└── README.md
```

------------------------------------------------------------------------

# 📦 Module Description

### `app.py`

Main Streamlit application responsible for:

-   User interface
-   Audio/video upload
-   Transcript input
-   Meeting processing
-   Result visualization
-   Meeting history

### `api.py`

FastAPI REST API providing:

``` text
GET /
POST /process-meeting
```

### `services/transcription_service.py`

Handles Faster-Whisper model loading, audio/video transcription,
language detection, and transcription validation.

### `services/llm_service.py`

Handles:

-   Transcript validation
-   Prompt generation
-   Gemini API communication
-   JSON cleaning
-   Pydantic validation
-   Retry handling
-   Long transcript chunking
-   Result merging

### `services/meeting_service.py`

Handles:

-   Participant cleaning
-   Duplicate removal
-   Action-item normalization
-   Priority normalization
-   Status normalization
-   Responsibility cleanup

### `services/database_service.py`

Handles SQLite initialization, meeting storage, and meeting retrieval.

### `schemas/meeting_schema.py`

Contains the Pydantic models:

``` text
MeetingIntelligence
ActionItem
Participant
```

### `prompts/meeting_prompt.py`

Contains the reusable meeting-analysis prompt and extraction rules.

------------------------------------------------------------------------

# ⚙️ Installation

## Prerequisites

-   Python 3.x
-   Git
-   Internet connection
-   Google Gemini API key

## 1. Clone the Repository

``` bash
git clone https://github.com/cpushpalatha9/meeting-intelligence.git
cd meeting-intelligence
```

## 2. Create a Virtual Environment

Windows:

``` powershell
python -m venv venv
.env\Scripts\Activate.ps1
```

## 3. Install Dependencies

``` powershell
pip install -r requirements.txt
```

------------------------------------------------------------------------

# 🔑 Environment Configuration

Create a `.env` file in the project root:

``` text
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-3.5-flash
WHISPER_MODEL=small
```

### Environment Variables

  Variable           Description
  ------------------ ---------------------------------------------
  `GEMINI_API_KEY`   Google Gemini API authentication key
  `GEMINI_MODEL`     Gemini model used for meeting analysis
  `WHISPER_MODEL`    Faster-Whisper model used for transcription

### Security

Never upload `.env` to GitHub. The repository `.gitignore` excludes it.

------------------------------------------------------------------------

# ▶️ Running the Streamlit Application

Activate the virtual environment:

``` powershell
.env\Scripts\Activate.ps1
```

Run:

``` powershell
streamlit run app.py
```

Open:

``` text
http://localhost:8501
```

## Streamlit Pages

### Process Meeting

Users can:

-   Upload audio/video
-   Paste an existing transcript
-   Process the meeting
-   View generated intelligence
-   View structured JSON

### Meeting History

Users can:

-   View previous meetings
-   Select a meeting
-   View its summary
-   View key points
-   View decisions
-   View action items
-   View participants

------------------------------------------------------------------------

# 🚀 Running the FastAPI Service

Open a separate terminal and activate the environment:

``` powershell
.env\Scripts\Activate.ps1
```

Start the server:

``` powershell
python -m uvicorn api:app --reload
```

API address:

``` text
http://127.0.0.1:8000
```

------------------------------------------------------------------------

# 📚 API Documentation

FastAPI Swagger documentation:

``` text
http://127.0.0.1:8000/docs
```

## GET `/`

Checks whether the API is running.

Example response:

``` json
{
  "status": "running",
  "service": "Meeting Intelligence API"
}
```

## POST `/process-meeting`

Processes an uploaded meeting audio/video file.

Input:

``` text
title
audio
```

Processing:

``` text
Audio/Video
    ↓
Faster-Whisper
    ↓
Transcript
    ↓
Google Gemini
    ↓
Pydantic
    ↓
SQLite
```

The response contains the meeting ID, detected language, transcript, and
structured meeting intelligence.

------------------------------------------------------------------------

# 🧪 Testing

The repository contains:

``` text
test_llm.py
```

Run:

``` bash
python test_llm.py
```

This verifies:

-   Gemini API connectivity
-   Prompt processing
-   JSON extraction
-   Pydantic validation
-   Meeting intelligence generation

------------------------------------------------------------------------

# 📝 Sample Meeting Transcript

``` text
Manager: Good morning everyone. Today we are discussing the mobile application launch.

Manager: Our target is to launch the application next Monday. Are there any issues that could affect the launch?

Ravi: The API integration is almost complete. I will finish the remaining API work by Thursday.

Manager: Ravi, please also send me the API status report by tomorrow evening.

Ravi: Sure, I will send the status report by tomorrow evening.

Priya: The UI development is complete. I need to perform the final UI testing.

Manager: When can you complete the testing?

Priya: I can complete the UI testing by Friday and prepare the testing report.

Manager: Good. Please send the testing report to me by Friday evening.

Manager: Okay. Then we have decided to proceed with the mobile application launch next Monday.

Manager: Ravi will complete the API integration and send the API status report. Priya will complete UI testing and submit the testing report.

Manager: Thank you everyone. The meeting is concluded.
```

------------------------------------------------------------------------

# 📊 Expected Output

### Participants

``` text
Manager
Ravi
Priya
```

### Decision

``` text
Proceed with the mobile application launch next Monday.
```

### Action Items

  Task                                Assignee   Deadline           Status
  ----------------------------------- ---------- ------------------ ---------
  Complete API integration            Ravi       Thursday           Pending
  Send API status report              Ravi       Tomorrow evening   Pending
  Complete UI testing                 Priya      Friday             Pending
  Prepare and submit testing report   Priya      Friday evening     Pending

### Responsibilities

``` text
Ravi
- Complete API integration
- Send API status report

Priya
- Complete UI testing
- Prepare testing report
```

------------------------------------------------------------------------

# 🗄️ Database and Persistence

The system uses SQLite.

Database location:

``` text
database/meetings.db
```

Stored information includes:

-   Meeting ID
-   Meeting title
-   Transcript
-   Summary
-   Key points
-   Decisions
-   Action items
-   Participants
-   Creation timestamp

The database file is excluded from GitHub using `.gitignore`.

------------------------------------------------------------------------

# 🧠 Prompt Engineering

The reusable Gemini prompt is designed for reliable meeting intelligence
extraction.

Important rules include:

-   Use only information supported by the transcript.
-   Do not invent participants.
-   Do not create duplicate participants.
-   Extract genuine action items only.
-   Do not convert general advice or opinions into action items.
-   Link responsibilities to the correct participant.
-   Extract deadlines only when supported.
-   Use standardized priority values.
-   Use standardized status values.
-   Return the required structured JSON format.

------------------------------------------------------------------------

# 🛡️ Validation and Error Handling

## Transcript Validation

Checks that the transcript:

-   Exists
-   Is not empty
-   Contains sufficient content

## JSON Validation

Gemini output is cleaned and parsed as JSON before Pydantic validation.

## Data Normalization

Duplicate participants and action items are removed, while priority and
status values are normalized.

## LLM Retry Handling

Temporary API failures such as:

``` text
429
500
502
503
504
```

can trigger automatic retries.

## Long Transcript Handling

Long transcripts are split into manageable chunks, processed
individually, and merged into a structured result.

------------------------------------------------------------------------

# 🔐 Security Considerations

The project follows basic security practices.

Sensitive and generated files are excluded from GitHub:

``` text
venv/
.env
__pycache__/
*.pyc
database/*.db
```

Never commit:

-   API keys
-   Passwords
-   Tokens
-   Private credentials
-   Local databases containing sensitive information

------------------------------------------------------------------------

# 🌟 Advantages

-   Automates meeting documentation
-   Reduces manual note-taking
-   Converts speech into structured information
-   Generates concise summaries
-   Extracts important discussion points
-   Identifies actionable tasks
-   Maps responsibilities to participants
-   Extracts deadlines
-   Tracks priority and status
-   Stores meetings for future access
-   Handles long transcripts
-   Validates AI-generated data
-   Provides retry handling
-   Provides both Streamlit UI and REST API
-   Uses a modular architecture

------------------------------------------------------------------------

# 💼 Applications

The system can be applied to:

-   Software development meetings
-   Project management meetings
-   Team meetings
-   Client meetings
-   Business meetings
-   Academic discussions
-   Product planning
-   Sprint planning
-   Review meetings
-   Interviews
-   Educational discussions
-   Research meetings

------------------------------------------------------------------------

# 🔮 Future Enhancements

Possible future improvements:

-   🎤 Speaker diarization
-   👤 Automatic speaker identification
-   📅 Calendar integration
-   📧 Email notifications for action items
-   🔔 Automatic deadline reminders
-   ✅ Task-management integration
-   😊 Meeting sentiment analysis
-   🏷️ Topic classification
-   🔎 Search across meetings
-   🔐 User authentication
-   👥 Role-based access control
-   ☁️ Cloud database integration
-   🌐 Cloud deployment
-   📊 Meeting analytics dashboard
-   📈 Meeting trend analysis

------------------------------------------------------------------------

# 🏆 Project Outcome

The Meeting Intelligence System demonstrates a complete end-to-end AI
pipeline for converting unstructured meeting conversations into
structured and actionable information.

The project integrates:

``` text
Speech Recognition
        +
Large Language Model
        +
Prompt Engineering
        +
Structured Data Validation
        +
Data Persistence
        +
Web Interface
        +
REST API
```

The completed system provides an automated solution for meeting
transcription, summarization, key point extraction, decision extraction,
action-item tracking, participant identification, responsibility
mapping, deadline extraction, and meeting history management.

This project demonstrates how modern AI technologies can be combined
with software engineering practices to build a practical Meeting
Intelligence application.

------------------------------------------------------------------------

# 📸 Screenshots

Add screenshots of the working application here.

Recommended screenshots:

1.  Streamlit Process Meeting page
2.  Generated Meeting Intelligence
3.  Meeting History page
4.  FastAPI Swagger documentation

Example:

``` markdown
![Meeting Intelligence Dashboard](screenshots/dashboard.png)

![Meeting History](screenshots/history.png)

![FastAPI Swagger](screenshots/api.png)
```

------------------------------------------------------------------------

# 👩‍💻 Author

**Pushpalatha**

GitHub Repository:

https://github.com/cpushpalatha9/meeting-intelligence

------------------------------------------------------------------------

# 📄 License

This project is developed for educational and academic project
demonstration purposes.
