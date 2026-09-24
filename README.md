# AI-Career Intelligence Platform

> An AI-powered intelligence workspace that transforms professional
> conversations into structured insights, searchable semantic memory,
> and evidence-based AI assistance.

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Google
Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Memory-5B21B6?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

------------------------------------------------------------------------

## Table of Contents

1.  [Overview](#1-overview)
2.  [Problem Statement](#2-problem-statement)
3.  [Objectives](#3-objectives)
4.  [Solution](#4-solution)
5.  [Key Features](#5-key-features)
6.  [System Workflow](#6-system-workflow)
7.  [Application Modules](#7-application-modules)
8.  [Architecture](#8-architecture)
9.  [Technology Stack](#9-technology-stack)
10. [Project Structure](#10-project-structure)
11. [Milestone 1](#11-milestone-1--data-ingestion-and-initial-analysis)
12. [Milestone 2](#12-milestone-2--llm-intelligence-and-persistence)
13. [Milestone 3](#13-milestone-3--semantic-memory-and-rag)
14. [AI and NLP Pipeline](#14-ai-and-nlp-pipeline)
15. [Database and Semantic Memory](#15-database-and-semantic-memory)
16. [RAG Pipeline](#16-rag-pipeline)
17. [Error Handling and Resilience](#17-error-handling-and-resilience)
18. [Configuration](#18-configuration)
19. [Installation](#19-installation)
20. [Running the Application](#20-running-the-application)
21. [Running the API](#21-running-the-api)
22. [Usage Guide](#22-usage-guide)
23. [Testing](#23-testing)
24. [Security](#24-security)
25. [Performance Considerations](#25-performance-considerations)
26. [Development Workflow](#26-development-workflow)
27. [Future Enhancements](#27-future-enhancements)
28. [Learning Outcomes](#28-learning-outcomes)
29. [Project Highlights](#29-project-highlights)
30. [Project Status](#30-project-status)
31. [Repository](#31-repository)
32. [Author](#32-author)
33. [License](#33-license)

------------------------------------------------------------------------

# 1. Overview

The **AI-Career Intelligence Platform** is an intelligent meeting and
knowledge-processing platform developed to transform unstructured
professional conversations into structured, searchable, and actionable
information.

The platform combines speech processing, Natural Language Processing,
Generative AI, structured data storage, vector databases, semantic
retrieval, and Retrieval-Augmented Generation.

At its core, the platform follows this pipeline:

``` text
Meeting Audio / Text
        |
        v
Validation & Ingestion
        |
        v
Preprocessing / Transcription
        |
        v
LLM-Based Understanding
        |
        v
Structured Meeting Intelligence
        |
        +--------------------+
        |                    |
        v                    v
   SQLite Database      Embedding Generation
                             |
                             v
                         ChromaDB
                             |
                             v
                      Semantic Retrieval
                             |
                             v
                           RAG
                             |
                             v
                     AI-Assisted Answers
```

The project is implemented cumulatively across three major milestones:

``` text
Milestone 1
Data Ingestion & Initial Analysis
          +
Milestone 2
LLM Intelligence & Persistence
          +
Milestone 3
Semantic Memory & RAG
          =
Integrated AI Intelligence Platform
```

------------------------------------------------------------------------

# 2. Problem Statement

Professional meetings contain important information such as:

-   Decisions
-   Action items
-   Responsibilities
-   Deadlines
-   Priorities
-   Participants
-   Discussion points
-   Follow-up requirements

However, this information is frequently embedded inside long audio
recordings, transcripts, or unstructured notes.

A conventional workflow requires users to manually:

1.  Listen to meeting recordings.
2.  Create or review transcripts.
3.  Summarize discussions.
4.  Identify decisions.
5.  Extract action items.
6.  Assign responsibilities.
7.  Track deadlines.
8.  Search previous meetings.
9.  Reconstruct historical context.

This project addresses the problem by creating an integrated
intelligence pipeline that automatically processes meeting information
and makes the resulting knowledge persistent and searchable.

------------------------------------------------------------------------

# 3. Objectives

The major objectives of the project are:

### 3.1 Automated Transcription

Convert meeting audio into text using Faster-Whisper.

### 3.2 Text Processing

Clean and preprocess raw text before downstream analysis.

### 3.3 Sentiment Analysis

Analyze textual sentiment using VADER.

### 3.4 LLM-Based Intelligence Extraction

Use Google Gemini to transform transcripts into structured meeting
intelligence.

### 3.5 Action Intelligence

Extract action items with available participant, deadline, priority, and
status information.

### 3.6 Participant Mapping

Identify participants and connect them with relevant responsibilities.

### 3.7 Persistent Storage

Store structured meeting intelligence using SQLite and SQLAlchemy.

### 3.8 Semantic Memory

Generate embeddings and store transcript knowledge in ChromaDB.

### 3.9 Semantic Search

Retrieve historical information based on semantic similarity.

### 3.10 Retrieval-Augmented Generation

Provide AI-assisted answers using retrieved historical evidence.

### 3.11 Quality Evaluation

Evaluate transcription quality using Word Error Rate.

------------------------------------------------------------------------

# 4. Solution

The platform provides a unified workflow for transforming professional
conversations into persistent intelligence.

``` text
CAPTURE
   |
   v
UNDERSTAND
   |
   v
STRUCTURE
   |
   v
REMEMBER
   |
   v
RETRIEVE
   |
   v
ACT
```

### Capture

Collect meeting audio or supported textual content.

### Understand

Transcribe and analyze the input.

### Structure

Extract meaningful information such as summaries, decisions,
participants, and action items.

### Remember

Persist structured information in SQLite and semantic information in
ChromaDB.

### Retrieve

Search historical knowledge using semantic retrieval.

### Act

Provide structured action intelligence and AI-assisted answers.

------------------------------------------------------------------------

# 5. Key Features

## 5.1 Multi-Format Ingestion

Supported input workflows include:

-   Audio files
-   TXT files
-   CSV files
-   Manual text
-   Meeting transcripts

Input validation is performed before processing.

------------------------------------------------------------------------

## 5.2 Faster-Whisper Transcription

The transcription service provides:

-   Audio validation
-   Speech-to-text conversion
-   Language detection
-   Transcript generation
-   Transcript validation
-   Transcript persistence

------------------------------------------------------------------------

## 5.3 Text Preprocessing

The preprocessing pipeline can perform:

-   Tokenization
-   Stopword handling
-   Lemmatization
-   Noise filtering
-   Punctuation cleanup
-   Repeated-space cleanup
-   Empty-content validation
-   Length validation

------------------------------------------------------------------------

## 5.4 Sentiment Analysis

VADER is used for sentiment analysis.

The analysis can include:

``` text
Positive Score
Negative Score
Neutral Score
Compound Score
Overall Sentiment
```

Example:

``` text
Positive: 0.42
Negative: 0.08
Neutral: 0.50
Compound: 0.61
Overall: Positive
```

------------------------------------------------------------------------

## 5.5 LLM-Based Meeting Intelligence

The LLM service converts meeting transcripts into structured
information.

The generated intelligence can include:

-   Executive summary
-   Key points
-   Decisions
-   Action items
-   Participants
-   Deadlines
-   Priorities
-   Status

The structured output is validated using Pydantic schemas.

------------------------------------------------------------------------

## 5.6 Action Item Extraction

Action items are represented as structured records.

Typical fields include:

``` text
Task
Assigned Participant
Deadline
Priority
Status
```

This converts conversational work into structured follow-up information.

------------------------------------------------------------------------

## 5.7 Participant Mapping

Participants identified in meeting content can be mapped to relevant
action items and responsibilities.

------------------------------------------------------------------------

## 5.8 Persistent Repository

Processed meetings can be stored in SQLite.

The repository can contain:

-   Meeting metadata
-   Transcript
-   Summary
-   Key points
-   Decisions
-   Action items
-   Participants
-   Processing information

------------------------------------------------------------------------

## 5.9 Vector-Based Semantic Memory

Transcript content is divided into chunks and converted into embeddings.

``` text
Transcript
    |
    v
Chunking
    |
    v
Embeddings
    |
    v
ChromaDB
```

------------------------------------------------------------------------

## 5.10 Semantic Search

The Intelligence Search module allows users to ask natural-language
questions about historical knowledge.

Example:

``` text
What deadline was agreed for the API integration?
```

The system searches indexed transcript chunks based on semantic
similarity.

------------------------------------------------------------------------

## 5.11 Retrieval-Augmented Generation

Ask Career AI combines semantic retrieval with LLM generation.

``` text
Question
   |
   v
Semantic Retrieval
   |
   v
Relevant Evidence
   |
   v
Context Construction
   |
   v
Gemini
   |
   v
AI-Assisted Answer
```

------------------------------------------------------------------------

## 5.12 Accuracy Lab

The Accuracy Lab provides transcription-quality evaluation using Word
Error Rate.

It can display:

-   WER
-   Estimated accuracy
-   Reference word count
-   Hypothesis word count
-   Detailed evaluation output

------------------------------------------------------------------------

# 6. System Workflow

The complete platform workflow is:

``` text
                     USER INPUT
                         |
             +-----------+-----------+
             |                       |
          AUDIO                     TEXT
             |                       |
             v                       v
      Faster-Whisper            Ingestion
             |                       |
             +-----------+-----------+
                         |
                         v
                  TRANSCRIPT
                         |
                         v
                 PREPROCESSING
                         |
                         v
                SENTIMENT ANALYSIS
                         |
                         v
                  GEMINI LLM
                         |
                         v
              STRUCTURED INTELLIGENCE
                         |
        +----------------+----------------+
        |                |                |
        v                v                v
     Summary         Decisions       Action Items
        |                |                |
        +----------------+----------------+
                         |
                         v
                    SQLite
                         |
                         v
                  Transcript Chunks
                         |
                         v
                    Embeddings
                         |
                         v
                     ChromaDB
                         |
                         v
                  Semantic Search
                         |
                         v
                       RAG
                         |
                         v
                  AI Answer
```

------------------------------------------------------------------------

# 7. Application Modules

The Streamlit application is organized into six primary modules.

## 7.1 Dashboard

The Dashboard provides a high-level overview of the intelligence
workspace.

It displays:

-   Knowledge records
-   Action signals
-   Decision signals
-   Semantic memory
-   System status
-   Intelligence pipeline

------------------------------------------------------------------------

## 7.2 Process Intelligence

This is the primary processing workspace.

The workflow is:

``` text
01 CAPTURE
02 UNDERSTAND
03 STRUCTURE
04 REMEMBER
05 RETRIEVE
06 ACT
```

The module connects ingestion, transcription, LLM processing, database
persistence, and indexing.

------------------------------------------------------------------------

## 7.3 Intelligence Repository

The repository provides access to processed meeting records.

Users can inspect:

-   Meeting records
-   Summaries
-   Decisions
-   Action items
-   Participants
-   Indexing status

------------------------------------------------------------------------

## 7.4 Intelligence Search

This module provides semantic search over indexed transcript knowledge.

Users can:

-   Enter a natural-language query
-   Select the number of results
-   Filter by record ID
-   Retrieve ranked evidence

------------------------------------------------------------------------

## 7.5 Ask Career AI

The AI question-answering interface retrieves relevant historical
evidence and uses it as context for the LLM.

The interface can display:

-   AI response
-   Retrieved sources
-   Evidence context
-   Query results

------------------------------------------------------------------------

## 7.6 Accuracy Lab

This module provides transcription-quality evaluation using reference
and generated transcripts.

------------------------------------------------------------------------

# 8. Architecture

## 8.1 High-Level Architecture

``` text
                         +--------------------------+
                         |       STREAMLIT UI       |
                         |--------------------------|
                         | Dashboard                |
                         | Process Intelligence     |
                         | Repository               |
                         | Semantic Search          |
                         | Ask Career AI            |
                         | Accuracy Lab             |
                         +------------+-------------+
                                      |
                                      v
                         +--------------------------+
                         |   APPLICATION SERVICES   |
                         |--------------------------|
                         | Ingestion                |
                         | Transcription            |
                         | Meeting Intelligence     |
                         | LLM Processing           |
                         | Database                 |
                         | Embedding                |
                         | Vector                   |
                         | Indexing                 |
                         | Search                   |
                         | RAG                      |
                         +------------+-------------+
                                      |
                  +-------------------+-------------------+
                  |                                       |
                  v                                       v
        +---------------------+                 +---------------------+
        | SQLite / SQLAlchemy |                 |      ChromaDB       |
        | Structured Memory   |                 |   Semantic Memory   |
        +---------------------+                 +----------+----------+
                                                         |
                                                         v
                                               +---------------------+
                                               | Embedding Service   |
                                               +---------------------+
```

------------------------------------------------------------------------

## 8.2 External AI Components

``` text
Faster-Whisper
      |
      +--> Speech-to-Text

Google Gemini
      |
      +--> Structured Intelligence
      |
      +--> RAG Answer Generation

Gemini Embeddings
      |
      +--> Vector Representations

ChromaDB
      |
      +--> Semantic Memory
```

------------------------------------------------------------------------

# 9. Technology Stack

  Category              Technology
  --------------------- ------------------
  Language              Python
  UI                    Streamlit
  API                   FastAPI
  Speech Recognition    Faster-Whisper
  LLM                   Google Gemini
  Embeddings            Gemini Embedding
  Vector Database       ChromaDB
  Relational Database   SQLite
  ORM                   SQLAlchemy
  Validation            Pydantic
  NLP                   NLTK
  Sentiment             VADER
  Environment           python-dotenv
  Server                Uvicorn
  Testing               Pytest
  Version Control       Git / GitHub

------------------------------------------------------------------------

# 10. Project Structure

``` text
Meeting_Intelligence_System/
│
├── app.py
├── requirements.txt
├── .env
│
├── api/
│   └── ...
│
├── config/
│   └── ...
│
├── services/
│   ├── ingestion_service.py
│   ├── transcription_service.py
│   ├── meeting_service.py
│   ├── llm_service.py
│   ├── database_service.py
│   ├── embedding_service.py
│   ├── vector_service.py
│   ├── indexing_service.py
│   ├── search_service.py
│   ├── rag_service.py
│   └── rag_fallback_service.py
│
├── schemas/
│   └── meeting_schema.py
│
├── prompts/
│   └── ...
│
├── database/
│   └── ...
│
├── vector_store/
│   └── ...
│
├── utils/
│   └── ...
│
├── tests/
│   └── ...
│
└── data/
    └── meeting_uploads/
```

------------------------------------------------------------------------

# 11. Milestone 1 --- Data Ingestion and Initial Analysis

## Objective

Build the foundation for accepting and analyzing meeting-related
content.

## Implemented Capabilities

-   Input validation
-   TXT ingestion
-   CSV ingestion
-   Manual text processing
-   Text preprocessing
-   Tokenization
-   Stopword handling
-   Lemmatization
-   Noise filtering
-   Punctuation handling
-   Sentiment analysis
-   Initial reporting
-   Pipeline integration

## M1 Workflow

``` text
Input
  |
  v
Validation
  |
  v
Preprocessing
  |
  v
Sentiment Analysis
  |
  v
Initial Report
```

------------------------------------------------------------------------

# 12. Milestone 2 --- LLM Intelligence and Persistence

## Objective

Transform transcripts into structured meeting intelligence and persist
the results.

## Implemented Capabilities

-   Gemini LLM integration
-   Prompt engineering
-   Structured JSON generation
-   Pydantic validation
-   Summary generation
-   Key-point extraction
-   Decision extraction
-   Action-item extraction
-   Participant mapping
-   Deadline extraction
-   Priority extraction
-   Database persistence
-   Service integration
-   Retry handling
-   Failure handling

## M2 Workflow

``` text
Transcript
    |
    v
LLM Processing
    |
    v
Structured Intelligence
    |
    +---- Summary
    |
    +---- Key Points
    |
    +---- Decisions
    |
    +---- Action Items
    |
    +---- Participants
    |
    +---- Deadlines
    |
    +---- Priorities
    |
    v
SQLite
```

------------------------------------------------------------------------

# 13. Milestone 3 --- Semantic Memory and RAG

## Objective

Build persistent semantic memory and allow users to retrieve and query
historical meeting knowledge.

## Implemented Capabilities

-   Historical meeting repository
-   Transcript chunking
-   Embedding generation
-   ChromaDB integration
-   Semantic search
-   Ranked evidence retrieval
-   RAG context construction
-   AI question answering
-   Existing service integration
-   Edge-case handling
-   End-to-end integration

## M3 Workflow

``` text
Stored Meeting
      |
      v
Transcript Chunking
      |
      v
Embedding Generation
      |
      v
ChromaDB
      |
      v
Semantic Search
      |
      v
Relevant Evidence
      |
      v
RAG
      |
      v
AI Answer
```

------------------------------------------------------------------------

# 14. AI and NLP Pipeline

## 14.1 Ingestion

Input is validated before processing.

Validation helps detect:

-   Unsupported files
-   Empty content
-   Invalid extensions
-   Invalid input

------------------------------------------------------------------------

## 14.2 Transcription

Audio is processed through Faster-Whisper.

``` text
Audio
  |
  v
Whisper Model
  |
  v
Transcript
```

------------------------------------------------------------------------

## 14.3 Preprocessing

Raw text is normalized before analysis.

``` text
Raw Text
   |
   v
Cleaning
   |
   v
Tokenization
   |
   v
Stopword Handling
   |
   v
Lemmatization
   |
   v
Clean Text
```

------------------------------------------------------------------------

## 14.4 Sentiment

VADER produces sentiment scores.

``` text
Text
 |
 v
VADER
 |
 +--> Positive
 +--> Negative
 +--> Neutral
 +--> Compound
```

------------------------------------------------------------------------

## 14.5 LLM Intelligence

The transcript is passed to Gemini with structured prompts.

The expected result is structured meeting intelligence.

------------------------------------------------------------------------

## 14.6 Schema Validation

Pydantic validates structured output before it is persisted.

This helps prevent malformed data from entering the database.

------------------------------------------------------------------------

# 15. Database and Semantic Memory

The platform uses two complementary storage systems.

## 15.1 SQLite

SQLite stores structured application data.

Example information:

``` text
Meeting
├── Metadata
├── Transcript
├── Summary
├── Key Points
├── Decisions
├── Participants
└── Action Items
```

------------------------------------------------------------------------

## 15.2 ChromaDB

ChromaDB stores semantic representations of transcript chunks.

``` text
Transcript
    |
    v
Chunks
    |
    v
Embeddings
    |
    v
ChromaDB
```

This allows semantic retrieval without relying only on exact keyword
matches.

------------------------------------------------------------------------

# 16. RAG Pipeline

The RAG architecture is:

``` text
                 USER QUESTION
                       |
                       v
              Query Embedding
                       |
                       v
                ChromaDB Search
                       |
                       v
              Relevant Chunks
                       |
                       v
              Context Construction
                       |
                       v
                  Gemini LLM
                       |
                       v
                 AI RESPONSE
                       |
                       v
               Retrieved Sources
```

The retrieved transcript chunks provide historical context for the
answer.

------------------------------------------------------------------------

# 17. Error Handling and Resilience

The application includes resilience mechanisms for external AI services.

## Temporary Failures

The LLM layer can handle temporary service failures through controlled
retries.

Supported strategies include:

-   Retry attempts
-   Exponential backoff
-   Jitter
-   Timeout handling

## Quota Errors

Quota-related errors are handled separately from temporary service
failures to avoid unnecessary repeated requests.

## Permanent Errors

Permanent configuration or request errors are surfaced rather than
repeatedly retried.

## Fallback

A local fallback mechanism allows the application to retain useful
functionality when external AI generation is unavailable.

------------------------------------------------------------------------

# 18. Configuration

Create a `.env` file in the project root.

Example:

``` env
GEMINI_API_KEY=your_gemini_api_key

GEMINI_MODEL=gemini-flash-lite-latest

GEMINI_EMBEDDING_MODEL=gemini-embedding-001

WHISPER_MODEL=small
WHISPER_DEVICE=cpu
WHISPER_COMPUTE_TYPE=int8

CHROMA_PATH=vector_store/chroma_db
```

### Configuration Notes

`GEMINI_API_KEY`

Your Google Gemini API credential.

`GEMINI_MODEL`

The Gemini model used for intelligence generation.

`GEMINI_EMBEDDING_MODEL`

The embedding model used for semantic memory.

`WHISPER_MODEL`

The Faster-Whisper model size.

`WHISPER_DEVICE`

The execution device.

`WHISPER_COMPUTE_TYPE`

The Whisper computation configuration.

`CHROMA_PATH`

The local ChromaDB storage path.

------------------------------------------------------------------------

# 19. Installation

## Prerequisites

Recommended environment:

-   Python 3.11+
-   Git
-   Windows / Linux / macOS
-   Internet connection for external AI services
-   Sufficient RAM for the selected Whisper model

------------------------------------------------------------------------

## Step 1 --- Clone Repository

``` bash
git clone https://github.com/cpushpalatha9/meeting-intelligence.git
```

Enter the project:

``` bash
cd meeting-intelligence
```

------------------------------------------------------------------------

## Step 2 --- Create Virtual Environment

Windows:

``` powershell
python -m venv .venv
```

Activate:

``` powershell
.venv\Scripts\activate
```

Linux/macOS:

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

------------------------------------------------------------------------

## Step 3 --- Install Dependencies

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

## Step 4 --- Configure Environment

Create:

``` text
.env
```

Then add:

``` env
GEMINI_API_KEY=your_gemini_api_key
```

and the remaining project configuration.

------------------------------------------------------------------------

# 20. Running the Application

Start Streamlit:

``` powershell
streamlit run app.py
```

The application will normally be available at:

``` text
http://localhost:8501
```

------------------------------------------------------------------------

# 21. Running the API

If the project API entry point is configured as `api.main`:

``` powershell
uvicorn api.main:app --reload
```

FastAPI then provides the API service on its configured local port.

------------------------------------------------------------------------

# 22. Usage Guide

## Step 1 --- Dashboard

Open the Dashboard and verify:

-   System status
-   Knowledge records
-   Action signals
-   Decision signals
-   Semantic memory

------------------------------------------------------------------------

## Step 2 --- Process Intelligence

Open **Process Intelligence**.

Provide supported meeting content.

The system processes the content through the integrated pipeline.

------------------------------------------------------------------------

## Step 3 --- Transcription

For audio input, Faster-Whisper produces the transcript.

Review the generated transcript.

------------------------------------------------------------------------

## Step 4 --- Intelligence Processing

The transcript is passed to the LLM service.

The system extracts:

-   Summary
-   Key points
-   Decisions
-   Action items
-   Participants
-   Deadlines
-   Priorities

------------------------------------------------------------------------

## Step 5 --- Persistence

The structured intelligence is saved into SQLite.

------------------------------------------------------------------------

## Step 6 --- Semantic Indexing

Transcript chunks are converted into embeddings and indexed in ChromaDB.

------------------------------------------------------------------------

## Step 7 --- Intelligence Repository

Open the repository to inspect stored intelligence.

------------------------------------------------------------------------

## Step 8 --- Intelligence Search

Enter a natural-language question such as:

``` text
What was the deadline for the API integration?
```

The system retrieves relevant semantic evidence.

------------------------------------------------------------------------

## Step 9 --- Ask Career AI

Ask a question using natural language.

The RAG pipeline retrieves relevant historical context and sends the
selected context to the LLM.

------------------------------------------------------------------------

## Step 10 --- Accuracy Lab

Use the Accuracy Lab to compare a generated transcript with a reference
transcript.

------------------------------------------------------------------------

# 23. Testing

Run all tests:

``` powershell
pytest
```

Verbose mode:

``` powershell
pytest -v
```

Specific test:

``` powershell
pytest tests/test_llm.py
```

Recommended testing categories:

``` text
Input Validation
      |
      v
Transcript Validation
      |
      v
Schema Validation
      |
      v
LLM Processing
      |
      v
Database Persistence
      |
      v
Embedding Generation
      |
      v
Vector Search
      |
      v
RAG Retrieval
      |
      v
Error Handling
```

------------------------------------------------------------------------

# 24. Security

## API Keys

Never hard-code API keys in Python source files.

Do not use:

``` python
GEMINI_API_KEY = "secret"
```

Use:

``` env
GEMINI_API_KEY=secret
```

------------------------------------------------------------------------

## Git Ignore

The following should not be committed:

``` gitignore
.env
__pycache__/
*.pyc
*.db
*.sqlite3
vector_store/
```

------------------------------------------------------------------------

## Sensitive Information

Before publishing the repository, verify that it does not contain:

-   API keys
-   Passwords
-   Personal meeting data
-   Private recordings
-   Private transcripts
-   Local database files
-   Generated vector-store files

------------------------------------------------------------------------

# 25. Performance Considerations

## Transcript Size Protection

Large transcripts should be controlled before sending them to the LLM.

## Retrieval-Based Context

RAG uses retrieved chunks instead of passing the entire meeting
repository to the model.

## Persistent Storage

Already processed meetings can be reused.

## Vector Search

ChromaDB provides semantic retrieval over indexed transcript chunks.

## Retry Backoff

Temporary AI service failures are handled using controlled retry
intervals.

------------------------------------------------------------------------

# 26. Development Workflow

Recommended development cycle:

``` text
Modify Code
    |
    v
Run Application
    |
    v
Test Feature
    |
    v
Run Tests
    |
    v
Check Git Status
    |
    v
Commit
    |
    v
Push to GitHub
```

Git commands:

``` bash
git status
git add .
git commit -m "Update AI-Career Intelligence Platform"
git push origin main
```

------------------------------------------------------------------------

# 27. Future Enhancements

The architecture can be extended with additional career-intelligence
capabilities.

Potential future features include:

### Career Intelligence

-   Career Intelligence Score
-   Career Progress Timeline
-   Achievement Tracking
-   Milestone Tracking

### Skill Intelligence

-   Skill Intelligence Map
-   Skill Gap Analyzer
-   Skill Progress Tracking

### Career Matching

-   AI Role Matching
-   Job Description Analysis
-   Evidence-Based Career Recommendations

### Resume Intelligence

-   Resume Analysis
-   Resume Skill Extraction
-   Resume-to-Role Matching
-   Project Evidence Mapping

### AI Career Copilot

-   Evidence-based career Q&A
-   Personalized career roadmap
-   Progress-aware assistance
-   Historical achievement retrieval

### Platform Enhancements

-   Authentication
-   Role-based access control
-   Multi-user support
-   Cloud deployment
-   Calendar integration
-   Email/task integration
-   Advanced analytics
-   Automated evaluation dashboards

These features are future extension areas and should only be described
as implemented after they are actually added to the application.

------------------------------------------------------------------------

# 28. Learning Outcomes

## Artificial Intelligence

The project provides practical exposure to:

-   Natural Language Processing
-   Speech Recognition
-   Sentiment Analysis
-   Generative AI
-   Prompt Engineering
-   LLM Structured Output
-   Embeddings
-   Semantic Search
-   Retrieval-Augmented Generation

## Software Engineering

The project demonstrates:

-   Modular architecture
-   Service-oriented organization
-   Schema validation
-   Database persistence
-   API integration
-   Error handling
-   Retry mechanisms
-   Testing

## Application Development

The implementation uses:

-   Streamlit
-   FastAPI
-   SQLite
-   SQLAlchemy
-   ChromaDB
-   Python
-   Git/GitHub

------------------------------------------------------------------------

# 29. Project Highlights

The project demonstrates an end-to-end AI engineering workflow:

``` text
Raw Meeting Content
        |
        v
Speech / Text Processing
        |
        v
Natural Language Processing
        |
        v
Generative AI
        |
        v
Structured Intelligence
        |
        v
Persistent Storage
        |
        v
Vector Memory
        |
        v
Semantic Retrieval
        |
        v
RAG
        |
        v
AI-Assisted Intelligence
```

Major technical concepts demonstrated:

-   End-to-end AI pipeline design
-   Speech-to-text processing
-   NLP preprocessing
-   Sentiment analysis
-   LLM integration
-   Structured JSON generation
-   Pydantic validation
-   Relational database persistence
-   Vector database integration
-   Semantic search
-   RAG
-   API development
-   Streamlit UI development
-   AI-service resilience
-   Testing
-   Git-based development

------------------------------------------------------------------------

# 30. Project Status

The project integrates the functionality developed across the three
major milestones.

``` text
+--------------------------------------------------+
|                AI-CAREER INTELLIGENCE            |
+--------------------------------------------------+
|                                                  |
|  M1  Data Ingestion & Initial Analysis           |
|                    |                             |
|                    v                             |
|  M2  LLM Intelligence & Persistence             |
|                    |                             |
|                    v                             |
|  M3  Semantic Memory & RAG                       |
|                    |                             |
|                    v                             |
|       Integrated Intelligence Platform           |
|                                                  |
+--------------------------------------------------+
```

The architecture is cumulative.

Future milestones can be added on top of the existing services without
replacing the earlier implementation.

------------------------------------------------------------------------

# 31. Repository

GitHub Repository:

**https://github.com/cpushpalatha9/meeting-intelligence**

------------------------------------------------------------------------

# 32. Author

## C Pushpalatha

Areas of interest:

-   Artificial Intelligence
-   Machine Learning
-   Natural Language Processing
-   Generative AI
-   Python
-   Software Engineering
-   AI Applications

------------------------------------------------------------------------

# 33. License

Choose and add the appropriate license before public distribution.

For example:

``` text
MIT License
```

Only use a license that has intentionally been selected for the
repository.

------------------------------------------------------------------------

# 34. Final Architecture Summary

``` text
                    AI-CAREER INTELLIGENCE PLATFORM
                                  |
          +-----------------------+-----------------------+
          |                                               |
          v                                               v
     STREAMLIT UI                                      FASTAPI
          |                                               |
          +-----------------------+-----------------------+
                                  |
                                  v
                       APPLICATION SERVICES
                                  |
       +-----------+--------------+--------------+-----------+
       |           |              |              |           |
       v           v              v              v           v
   Ingestion  Transcription    LLM          Database     RAG/Search
       |           |              |              |           |
       +-----------+--------------+--------------+-----------+
                                  |
                    +-------------+-------------+
                    |                           |
                    v                           v
                 SQLite                     ChromaDB
            Structured Memory             Vector Memory
                                                |
                                                v
                                        Semantic Retrieval
                                                |
                                                v
                                               RAG
                                                |
                                                v
                                         AI Response
```

------------------------------------------------------------------------

## AI-Career Intelligence Platform

**Capture → Understand → Structure → Remember → Retrieve → Act**

Turning professional conversations into structured intelligence,
persistent memory, semantic evidence, and actionable AI assistance.
