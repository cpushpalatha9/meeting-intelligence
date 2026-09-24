import html
import os
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from services.database_service import (
    init_database,
    save_meeting,
    get_all_meetings,
    get_meeting,
)
from services.ingestion_service import (
    validate_uploaded_file,
    validate_transcript,
)
from services.preprocessing_service import preprocess_text
from services.sentiment_service import analyze_sentiment
from services.transcription_service import WhisperTranscriptionService
from services.meeting_service import clean_action_items, clean_participants
from services.llm_service import (
    LLMService,
    GeminiQuotaError,
    GeminiTemporaryError,
    GeminiPermanentError,
)
from services.indexing_service import MeetingIndexingService
from services.search_service import SearchService
from services.rag_service import RAGService
from services.accuracy_service import calculate_wer


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

load_dotenv(override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")

st.set_page_config(
    page_title="Meeting Intelligence | Command Center",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_database()


# ============================================================
# THEME / DESIGN SYSTEM
# ============================================================

st.html(
    """
    <style>
    :root {
        --mi-indigo: #6366f1;
        --mi-blue: #0ea5e9;
        --mi-violet: #8b5cf6;
        --mi-green: #22c55e;
        --mi-amber: #f59e0b;
        --mi-red: #ef4444;
        --mi-border: rgba(100,116,139,.18);
        --mi-muted: rgba(100,116,139,.78);
    }

    .block-container {
        max-width: 1480px;
        padding-top: 1.15rem;
        padding-bottom: 3.5rem;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid var(--mi-border);
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1.1rem;
    }

    /* ---------- BRAND ---------- */

    .brand {
        padding: 10px 2px 18px 2px;
    }

    .brand-mark {
        display: inline-flex;
        width: 42px;
        height: 42px;
        align-items: center;
        justify-content: center;
        border-radius: 13px;
        margin-bottom: 10px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        font-size: 1.2rem;
        box-shadow: 0 10px 25px rgba(99,102,241,.28);
    }

    .brand-title {
        font-size: 1.12rem;
        font-weight: 850;
        letter-spacing: -.025em;
    }

    .brand-sub {
        margin-top: 3px;
        color: var(--mi-muted);
        font-size: .76rem;
    }

    /* ---------- HERO ---------- */

    .hero {
        position: relative;
        overflow: hidden;
        padding: 38px 40px;
        margin-bottom: 24px;
        border: 1px solid rgba(255,255,255,.10);
        border-radius: 28px;
        color: white;
        background:
            radial-gradient(circle at 88% 18%, rgba(139,92,246,.46), transparent 25%),
            radial-gradient(circle at 12% 110%, rgba(14,165,233,.30), transparent 32%),
            linear-gradient(135deg, #0b1120 0%, #172554 54%, #312e81 100%);
        box-shadow: 0 24px 60px rgba(15,23,42,.20);
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 260px;
        height: 260px;
        right: -100px;
        bottom: -120px;
        border-radius: 50%;
        background: rgba(255,255,255,.05);
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 11px;
        margin-bottom: 14px;
        border: 1px solid rgba(255,255,255,.17);
        border-radius: 999px;
        background: rgba(255,255,255,.075);
        color: rgba(255,255,255,.88);
        font-size: .70rem;
        font-weight: 800;
        letter-spacing: .09em;
        text-transform: uppercase;
    }

    .hero h1 {
        position: relative;
        z-index: 2;
        max-width: 900px;
        margin: 0;
        font-size: clamp(2rem, 4vw, 3.05rem);
        line-height: 1.02;
        letter-spacing: -.045em;
    }

    .hero p {
        position: relative;
        z-index: 2;
        max-width: 850px;
        margin: 14px 0 0 0;
        color: rgba(255,255,255,.76);
        font-size: 1rem;
        line-height: 1.65;
    }

    /* ---------- METRICS ---------- */

    .metric-card {
        min-height: 126px;
        padding: 20px;
        border: 1px solid var(--mi-border);
        border-radius: 19px;
        background: rgba(148,163,184,.035);
        box-shadow: 0 7px 24px rgba(15,23,42,.035);
    }

    .metric-icon {
        font-size: 1.05rem;
        opacity: .8;
    }

    .metric-label {
        margin-top: 9px;
        color: var(--mi-muted);
        font-size: .70rem;
        font-weight: 800;
        letter-spacing: .09em;
        text-transform: uppercase;
    }

    .metric-value {
        margin-top: 5px;
        font-size: 1.78rem;
        font-weight: 850;
        letter-spacing: -.04em;
    }

    .metric-sub {
        margin-top: 2px;
        color: var(--mi-muted);
        font-size: .75rem;
    }

    /* ---------- SECTION HEADERS ---------- */

    .section-title {
        margin-top: 29px;
        margin-bottom: 5px;
        font-size: 1.20rem;
        font-weight: 850;
        letter-spacing: -.025em;
    }

    .section-subtitle {
        margin-bottom: 13px;
        color: var(--mi-muted);
        font-size: .82rem;
    }

    /* ---------- FEATURE CARDS ---------- */

    .feature-card {
        min-height: 168px;
        padding: 21px;
        border: 1px solid var(--mi-border);
        border-radius: 19px;
        background: rgba(148,163,184,.025);
        transition: transform .18s ease, box-shadow .18s ease;
    }

    .feature-number {
        color: var(--mi-indigo);
        font-size: .68rem;
        font-weight: 850;
        letter-spacing: .12em;
    }

    .feature-title {
        margin-top: 7px;
        font-size: 1.02rem;
        font-weight: 800;
    }

    .feature-text {
        margin-top: 8px;
        color: var(--mi-muted);
        font-size: .80rem;
        line-height: 1.55;
    }

    /* ---------- INSIGHT ---------- */

    .insight-card {
        padding: 21px 23px;
        border: 1px solid rgba(99,102,241,.17);
        border-left: 4px solid var(--mi-indigo);
        border-radius: 17px;
        background: rgba(99,102,241,.055);
        line-height: 1.72;
    }

    /* ---------- PIPELINE ---------- */

    .pipeline-wrap {
        display: flex;
        align-items: stretch;
        gap: 7px;
        overflow-x: auto;
        padding: 5px 0 10px 0;
    }

    .pipeline-step {
        flex: 1;
        min-width: 125px;
        padding: 15px 12px;
        border: 1px solid var(--mi-border);
        border-radius: 16px;
        background: rgba(148,163,184,.025);
        text-align: center;
    }

    .pipeline-num {
        color: var(--mi-indigo);
        font-size: .67rem;
        font-weight: 850;
        letter-spacing: .09em;
    }

    .pipeline-label {
        margin-top: 5px;
        font-size: .82rem;
        font-weight: 800;
    }

    .pipeline-desc {
        margin-top: 3px;
        color: var(--mi-muted);
        font-size: .68rem;
    }

    .pipeline-arrow {
        align-self: center;
        color: var(--mi-muted);
        font-weight: 800;
    }

    /* ---------- SOURCE CARDS ---------- */

    .source-card {
        padding: 16px 18px;
        margin: 8px 0;
        border: 1px solid var(--mi-border);
        border-radius: 15px;
        background: rgba(148,163,184,.025);
    }

    .source-meta {
        margin-bottom: 7px;
        color: var(--mi-muted);
        font-size: .69rem;
        font-weight: 750;
        letter-spacing: .04em;
        text-transform: uppercase;
    }

    /* ---------- STATUS ---------- */

    .status {
        display: inline-flex;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: .70rem;
        font-weight: 800;
    }

    .status-ok {
        background: rgba(34,197,94,.10);
        color: #16a34a;
    }

    .status-warn {
        background: rgba(245,158,11,.11);
        color: #d97706;
    }

    .status-info {
        background: rgba(14,165,233,.10);
        color: #0284c7;
    }

    /* ---------- SMALL TEXT ---------- */

    .muted {
        color: var(--mi-muted);
        font-size: .80rem;
    }

    .pill {
        display: inline-block;
        padding: 5px 9px;
        margin: 2px 4px 2px 0;
        border-radius: 999px;
        background: rgba(99,102,241,.10);
        color: var(--mi-indigo);
        font-size: .70rem;
        font-weight: 750;
    }

    .empty-state {
        padding: 34px 22px;
        border: 1px dashed rgba(100,116,139,.28);
        border-radius: 18px;
        text-align: center;
        color: var(--mi-muted);
    }

    .empty-icon {
        font-size: 2rem;
        margin-bottom: 8px;
    }

    .stButton > button {
        border-radius: 11px;
        font-weight: 750;
    }
    </style>
    """
)


# ============================================================
# CACHED SERVICES
# ============================================================

@st.cache_resource(show_spinner=False)
def get_whisper_service():
    return WhisperTranscriptionService(
        model_size=WHISPER_MODEL
    )


@st.cache_resource(show_spinner=False)
def get_indexing_service():
    return MeetingIndexingService()


@st.cache_resource(show_spinner=False)
def get_search_service():
    return SearchService()


@st.cache_resource(show_spinner=False)
def get_rag_service():
    return RAGService()


# ============================================================
# UI HELPERS
# ============================================================

def esc(value):
    return html.escape(str(value or ""))


def metric_card(label, value, sub="", icon="◈"):
    st.html(
        f"""
        <div class="metric-card">
            <div class="metric-icon">{esc(icon)}</div>
            <div class="metric-label">{esc(label)}</div>
            <div class="metric-value">{esc(value)}</div>
            <div class="metric-sub">{esc(sub)}</div>
        </div>
        """
    )


def section_title(title, subtitle=None):
    st.html(
        f'<div class="section-title">{esc(title)}</div>'
    )
    if subtitle:
        st.html(
            f'<div class="section-subtitle">{esc(subtitle)}</div>'
        )


def status_badge(text, kind="info"):
    st.html(
        f'<span class="status status-{kind}">{esc(text)}</span>'
    )


def index_meeting(meeting_id):
    try:
        return get_indexing_service().index_meeting(
            meeting_id
        )
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
        }


def display_sources(sources):
    if not sources:
        st.info("No retrieved evidence was returned.")
        return

    section_title(
        "Retrieved evidence",
        "The answer is grounded in these meeting repository chunks.",
    )

    for i, source in enumerate(sources, 1):
        similarity = float(
            source.get("similarity", 0) or 0
        )
        st.html(
            f"""
            <div class="source-card">
                <div class="source-meta">
                    SOURCE {i} · MEETING #{esc(source.get('meeting_id'))}
                    · {esc(source.get('meeting_title', 'Meeting'))}
                    · CHUNK {esc(source.get('chunk_id'))}
                    · RELEVANCE {similarity:.3f}
                </div>
                <div>{esc(source.get('document', ''))}</div>
            </div>
            """
        )


def empty_state(icon, title, message):
    st.html(
        f"""
        <div class="empty-state">
            <div class="empty-icon">{esc(icon)}</div>
            <strong>{esc(title)}</strong>
            <div class="muted">{esc(message)}</div>
        </div>
        """
    )


def render_intelligence(intelligence, sentiment, language):
    intelligence = intelligence or {}
    sentiment = sentiment or {}

    action_items = clean_action_items(
        intelligence.get("action_items", [])
    )
    participants = clean_participants(
        intelligence.get("participants", [])
    )

    section_title(
        "Executive intelligence",
        "Structured meeting intelligence generated from the transcript.",
    )

    st.html(
        f"""
        <div class="insight-card">
            {esc(intelligence.get('summary', 'No summary available.'))}
        </div>
        """
    )

    st.write("")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Language", language or "Unknown", icon="◉")
    with c2:
        metric_card(
            "Sentiment",
            sentiment.get("label", "neutral").title(),
            "VADER",
            icon="◌",
        )
    with c3:
        metric_card(
            "Action Items",
            len(action_items),
            "Extracted work items",
            icon="✓",
        )
    with c4:
        metric_card(
            "Participants",
            len(participants),
            "Detected people",
            icon="●",
        )

    left, right = st.columns(2)

    with left:
        section_title("Key points")
        points = intelligence.get("key_points", []) or []
        if points:
            for item in points:
                st.markdown(f"• {item}")
        else:
            st.caption("No key points detected.")

        section_title("Decisions")
        decisions = intelligence.get("decisions", []) or []
        if decisions:
            for item in decisions:
                st.markdown(f"• {item}")
        else:
            st.caption("No explicit decisions detected.")

    with right:
        section_title("Deadlines & priorities")
        deadlines = intelligence.get("deadlines", []) or []
        priorities = intelligence.get("priorities", []) or []

        if deadlines:
            st.markdown("**Deadlines**")
            for item in deadlines:
                st.html(
                    f'<span class="pill">{esc(item)}</span>'
                )
        else:
            st.caption("No explicit deadlines detected.")

        if priorities:
            st.markdown("**Priorities**")
            for item in priorities:
                st.html(
                    f'<span class="pill">{esc(item)}</span>'
                )
        else:
            st.caption("No explicit priorities detected.")

    section_title(
        "Action items",
        "Ownership, deadline, priority and status extracted from the meeting.",
    )
    if action_items:
        st.dataframe(
            action_items,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No action items detected.")

    section_title("Participants & responsibilities")
    if participants:
        st.dataframe(
            participants,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No participants detected.")

    section_title(
        "Sentiment analysis",
        "VADER polarity distribution for the meeting transcript.",
    )

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        metric_card("Positive", f"{sentiment.get('positive', 0):.3f}")
    with s2:
        metric_card("Negative", f"{sentiment.get('negative', 0):.3f}")
    with s3:
        metric_card("Neutral", f"{sentiment.get('neutral', 0):.3f}")
    with s4:
        metric_card("Compound", f"{sentiment.get('compound', 0):.3f}")

    st.bar_chart(
        {
            "Positive": sentiment.get("positive", 0),
            "Negative": sentiment.get("negative", 0),
            "Neutral": sentiment.get("neutral", 0),
        }
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.html(
        """
        <div class="brand">
            <div class="brand-mark">🎙️</div>
            <div class="brand-title">Meeting Intelligence</div>
            <div class="brand-sub">AI meeting command center</div>
        </div>
        """
    )

    page = st.radio(
        "Workspace",
        [
            "Dashboard",
            "Process Meeting",
            "Meeting Repository",
            "Semantic Search",
            "Ask Meeting AI",
            "Accuracy Testing",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.caption("PIPELINE")
    st.caption("🎤 Ingest → 📝 Transcribe → 🧠 Analyze")
    st.caption("💾 Store → 🔎 Retrieve → 💬 Answer")

    st.divider()

    st.caption("MILESTONES")
    st.caption("✓ M1 · Ingestion · NLP · Sentiment")
    st.caption("✓ M2 · LLM · Actions · Participants")
    st.caption("✓ M3 · Embeddings · Search · RAG")

    st.divider()

    st.caption(f"Gemini · {GEMINI_MODEL}")
    st.caption(f"Whisper · {WHISPER_MODEL}")


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":
    meetings = get_all_meetings()

    total_meetings = len(meetings)
    total_actions = sum(
        len(m.get("action_items", []))
        for m in meetings
    )
    total_decisions = sum(
        len(m.get("decisions", []))
        for m in meetings
    )

    participants = set()
    for meeting in meetings:
        for participant in meeting.get("participants", []):
            if isinstance(participant, dict):
                name = participant.get("name", "")
            else:
                name = str(participant)
            if name:
                participants.add(name)

    try:
        indexed_chunks = get_indexing_service().get_index_status().get(
            "count", 0
        )
    except Exception:
        indexed_chunks = 0

    st.html(
        """
        <div class="hero">
            <div class="hero-badge">● AI-powered meeting operations</div>
            <h1>Meeting Intelligence Command Center</h1>
            <p>
                Transform recordings and transcripts into structured intelligence,
                searchable organizational memory, and evidence-grounded answers.
            </p>
        </div>
        """
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Meetings", total_meetings, "Stored in SQLite", "◉")
    with c2:
        metric_card("Action Items", total_actions, "Extracted work", "✓")
    with c3:
        metric_card("Decisions", total_decisions, "Detected outcomes", "◆")
    with c4:
        metric_card("Indexed Chunks", indexed_chunks, "Semantic memory", "⌁")

    section_title(
        "End-to-end intelligence pipeline",
        "Milestones 1–3 operate as one continuous workflow.",
    )

    steps = [
        ("01", "Ingest", "Audio / text"),
        ("02", "Transcribe", "Whisper"),
        ("03", "Analyze", "NLP + LLM"),
        ("04", "Persist", "SQLite"),
        ("05", "Index", "Embeddings"),
        ("06", "Retrieve", "ChromaDB"),
        ("07", "Answer", "RAG"),
    ]

    pipeline = '<div class="pipeline-wrap">'
    for i, (number, label, desc) in enumerate(steps):
        pipeline += f"""
        <div class="pipeline-step">
            <div class="pipeline-num">{number}</div>
            <div class="pipeline-label">{esc(label)}</div>
            <div class="pipeline-desc">{esc(desc)}</div>
        </div>
        """
        if i < len(steps) - 1:
            pipeline += '<div class="pipeline-arrow">→</div>'
    pipeline += '</div>'
    st.html(pipeline)

    section_title(
        "Capability map",
        "A professional view of the completed project scope.",
    )

    capabilities = [
        ("M1", "Smart ingestion", "Audio/video upload, transcript input, validation and local speech-to-text."),
        ("M1", "NLP & sentiment", "Normalization, tokenization support, noise filtering and VADER sentiment scoring."),
        ("M2", "Meeting intelligence", "Summary, key points, decisions, action items and structured participant mapping."),
        ("M2", "Operational tracking", "Assignee, deadline, priority and status for actionable meeting outcomes."),
        ("M3", "Semantic memory", "Transcript chunking, embeddings, metadata and persistent ChromaDB indexing."),
        ("M3", "Evidence-grounded AI", "Semantic retrieval followed by RAG answers with visible source evidence."),
    ]

    cols = st.columns(3)
    for i, (milestone, title, text) in enumerate(capabilities):
        with cols[i % 3]:
            st.html(
                f"""
                <div class="feature-card">
                    <div class="feature-number">{milestone}</div>
                    <div class="feature-title">{esc(title)}</div>
                    <div class="feature-text">{esc(text)}</div>
                </div>
                """
            )

    section_title("System readiness")
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        status_badge("Database ready", "ok")
    with r2:
        status_badge(
            "Gemini key configured" if GEMINI_API_KEY else "Gemini key missing",
            "ok" if GEMINI_API_KEY else "warn",
        )
    with r3:
        status_badge("Whisper available", "ok")
    with r4:
        status_badge("Vector memory ready", "ok")

    section_title("Recent meetings")

    if not meetings:
        empty_state(
            "🎙️",
            "No meetings yet",
            "Open Process Meeting to create your first intelligence record.",
        )
    else:
        for meeting in meetings[:6]:
            with st.container(border=True):
                a, b, c = st.columns([5, 2, 1])
                with a:
                    st.markdown(f"**{meeting['title']}**")
                    st.caption(
                        (meeting.get("summary") or "No summary available.")[:240]
                    )
                with b:
                    st.caption(f"Meeting #{meeting['id']}")
                    st.caption(str(meeting.get("created_at", "")))
                with c:
                    st.metric(
                        "Actions",
                        len(meeting.get("action_items", [])),
                    )


# ============================================================
# PROCESS MEETING
# ============================================================

elif page == "Process Meeting":
    st.markdown("# Process a Meeting")
    st.caption(
        "Run ingestion → transcription → NLP → structured intelligence → persistence → semantic indexing."
    )

    title = st.text_input(
        "Meeting title",
        placeholder="e.g. Product Sprint Planning — September 24",
    )

    input_mode = st.radio(
        "Input source",
        [
            "🎙️ Audio / Video Recording",
            "📄 Existing Transcript",
        ],
        horizontal=True,
    )

    uploaded_file = None
    manual_transcript = ""

    if input_mode == "🎙️ Audio / Video Recording":
        uploaded_file = st.file_uploader(
            "Upload meeting recording",
            type=[
                "mp3", "wav", "m4a", "mp4", "webm",
                "ogg", "flac", "aac",
            ],
            help="The recording is transcribed locally with Faster-Whisper.",
        )

        if uploaded_file:
            st.audio(uploaded_file)
            st.caption(
                f"{uploaded_file.name} · {uploaded_file.size / 1024 / 1024:.2f} MB"
            )
    else:
        manual_transcript = st.text_area(
            "Meeting transcript",
            height=300,
            placeholder="Paste the complete meeting transcript here...",
        )

    if st.button(
        "🚀 Process Meeting End-to-End",
        type="primary",
        use_container_width=True,
    ):
        try:
            if not title.strip():
                st.error("Please enter a meeting title.")
                st.stop()

            transcript = ""
            language = "unknown"

            with st.status(
                "Running the meeting intelligence pipeline...",
                expanded=True,
            ) as status:
                # M1 — ingestion / transcription
                st.write("### Milestone 1 · Ingestion")

                if input_mode == "🎙️ Audio / Video Recording":
                    if uploaded_file is None:
                        raise ValueError("Please upload a recording.")

                    validate_uploaded_file(uploaded_file)
                    st.write("✓ Recording validated")

                    suffix = Path(uploaded_file.name).suffix or ".wav"
                    temp_path = None
                    try:
                        with tempfile.NamedTemporaryFile(
                            delete=False,
                            suffix=suffix,
                        ) as temp_file:
                            temp_file.write(uploaded_file.getbuffer())
                            temp_path = temp_file.name

                        st.write("🎧 Transcribing with Faster-Whisper...")
                        transcript, language = (
                            get_whisper_service().transcribe_file(temp_path)
                        )
                    finally:
                        if temp_path:
                            try:
                                os.remove(temp_path)
                            except OSError:
                                pass
                else:
                    language = "manual"
                    transcript = manual_transcript.strip()

                valid, message = validate_transcript(transcript)
                if not valid:
                    raise ValueError(message)

                st.write(
                    f"✓ Transcript validated · {len(transcript.split())} words"
                )

                # M1 — NLP / sentiment
                st.write("### Milestone 1 · NLP & Sentiment")
                processed_text = preprocess_text(transcript)
                sentiment = analyze_sentiment(transcript)
                st.write("✓ Preprocessing completed")
                st.write(
                    f"✓ VADER sentiment: `{sentiment.get('label', 'neutral')}`"
                )

                # M2 — LLM intelligence
                st.write("### Milestone 2 · Meeting Intelligence")
                if not GEMINI_API_KEY:
                    raise ValueError(
                        "GEMINI_API_KEY is missing. Add it to .env."
                    )

                intelligence = LLMService().process_long_transcript(
                    transcript
                )
                intelligence["action_items"] = clean_action_items(
                    intelligence.get("action_items", [])
                )
                intelligence["participants"] = clean_participants(
                    intelligence.get("participants", [])
                )

                st.write("✓ Structured summary generated")
                st.write("✓ Decisions and action items extracted")
                st.write("✓ Participants and responsibilities mapped")

                # Persistence
                st.write("### Persistence")
                meeting_id = save_meeting(
                    title=title.strip(),
                    transcript=transcript,
                    summary=intelligence.get("summary", ""),
                    key_points=intelligence.get("key_points", []),
                    decisions=intelligence.get("decisions", []),
                    action_items=intelligence.get("action_items", []),
                    participants=intelligence.get("participants", []),
                    deadlines=intelligence.get("deadlines", []),
                    priorities=intelligence.get("priorities", []),
                    language=language,
                    sentiment=sentiment,
                    processed_text=processed_text,
                )
                st.write(f"✓ Saved to SQLite as meeting #{meeting_id}")

                # M3 — semantic indexing
                st.write("### Milestone 3 · Semantic Memory")
                indexing = index_meeting(meeting_id)
                if indexing.get("success"):
                    st.write(
                        f"✓ Indexed {indexing.get('chunks_indexed', 0)} transcript chunks"
                    )
                else:
                    st.write(
                        "⚠ Meeting saved, but vector indexing needs attention."
                    )

                status.update(
                    label="Meeting pipeline completed",
                    state="complete",
                )

            st.success(
                f"Meeting #{meeting_id} is now available in the repository, search and RAG workspace."
            )

            render_intelligence(
                intelligence,
                sentiment,
                language,
            )

            section_title("Transcript")
            with st.expander("Open complete transcript", expanded=False):
                st.text_area(
                    "Transcript",
                    transcript,
                    height=340,
                    disabled=True,
                    label_visibility="collapsed",
                )

            section_title("Processed NLP text")
            with st.expander("Open normalized transcript", expanded=False):
                st.text_area(
                    "Processed text",
                    processed_text,
                    height=250,
                    disabled=True,
                    label_visibility="collapsed",
                )

        except GeminiQuotaError as exc:
            st.error(str(exc))
            st.warning(
                "Gemini generation quota is unavailable. This is a project/model quota condition, not a Whisper or transcript failure."
            )
        except GeminiTemporaryError as exc:
            st.error(str(exc))
        except GeminiPermanentError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error("Meeting processing failed.")
            st.exception(exc)


# ============================================================
# MEETING REPOSITORY
# ============================================================

elif page == "Meeting Repository":
    st.markdown("# Meeting Repository")
    st.caption(
        "Historical meeting memory containing transcripts, decisions, action items and participant responsibilities."
    )

    meetings = get_all_meetings()

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Meetings", len(meetings), "SQLite records")
    with c2:
        metric_card(
            "Action Items",
            sum(len(m.get("action_items", [])) for m in meetings),
            "Tracked work",
        )
    with c3:
        try:
            count = get_indexing_service().get_index_status().get("count", 0)
        except Exception:
            count = 0
        metric_card("Indexed Chunks", count, "ChromaDB memory")

    search_term = st.text_input(
        "Filter repository",
        placeholder="Search by meeting title or summary...",
    )

    if search_term.strip():
        term = search_term.lower()
        meetings = [
            m for m in meetings
            if term in m.get("title", "").lower()
            or term in m.get("summary", "").lower()
        ]

    if not meetings:
        empty_state(
            "📚",
            "No matching meetings",
            "Process a meeting or change the repository filter.",
        )

    for meeting in meetings:
        with st.container(border=True):
            a, b, c = st.columns([5, 2, 1.2])
            with a:
                st.markdown(f"### {meeting['title']}")
                st.caption(
                    f"Meeting #{meeting['id']} · {meeting.get('created_at', '')} · Language: {meeting.get('language', 'unknown')}"
                )
                st.write(
                    (meeting.get("summary") or "No summary available.")[:420]
                )
            with b:
                st.metric(
                    "Actions",
                    len(meeting.get("action_items", [])),
                )
                st.metric(
                    "Participants",
                    len(meeting.get("participants", [])),
                )
            with c:
                if st.button(
                    "↻ Re-index",
                    key=f"reindex_{meeting['id']}",
                    use_container_width=True,
                ):
                    result = index_meeting(meeting["id"])
                    if result.get("success"):
                        st.success(
                            f"{result.get('chunks_indexed', 0)} chunks"
                        )
                    else:
                        st.error(
                            result.get("error", "Indexing failed.")
                        )

            with st.expander("Open meeting details"):
                left, right = st.columns(2)
                with left:
                    st.markdown("**Decisions**")
                    decisions = meeting.get("decisions", [])
                    if decisions:
                        for item in decisions:
                            st.markdown(f"• {item}")
                    else:
                        st.caption("No decisions recorded.")

                    st.markdown("**Deadlines**")
                    for item in meeting.get("deadlines", []) or []:
                        st.markdown(f"• {item}")

                with right:
                    st.markdown("**Action items**")
                    if meeting.get("action_items"):
                        st.dataframe(
                            meeting["action_items"],
                            use_container_width=True,
                            hide_index=True,
                        )
                    else:
                        st.caption("No action items recorded.")

                st.markdown("**Transcript**")
                st.text_area(
                    "Transcript",
                    meeting.get("transcript", ""),
                    height=280,
                    disabled=True,
                    key=f"repo_transcript_{meeting['id']}",
                    label_visibility="collapsed",
                )


# ============================================================
# SEMANTIC SEARCH
# ============================================================

elif page == "Semantic Search":
    st.markdown("# Semantic Search")
    st.caption(
        "Search historical meetings by meaning using embeddings and ChromaDB."
    )

    query = st.text_input(
        "Search your meeting memory",
        placeholder="e.g. What deadline was agreed for the API integration?",
    )

    c1, c2 = st.columns(2)
    with c1:
        top_k = st.slider(
            "Number of results",
            1,
            10,
            5,
        )
    with c2:
        meeting_id = st.number_input(
            "Meeting ID · 0 = all meetings",
            min_value=0,
            step=1,
            value=0,
        )

    if st.button(
        "🔎 Search Meeting Memory",
        type="primary",
        use_container_width=True,
    ):
        if not query.strip():
            st.warning("Enter a search question first.")
        else:
            try:
                results = get_search_service().search(
                    query.strip(),
                    top_k=top_k,
                    meeting_id=meeting_id or None,
                )

                if not results:
                    empty_state(
                        "🔎",
                        "No relevant context",
                        "Try another question or index the meeting repository.",
                    )
                else:
                    status_badge(
                        f"{len(results)} relevant chunk(s) found",
                        "ok",
                    )
                    display_sources(results)
            except Exception as exc:
                st.error("Semantic search failed.")
                st.exception(exc)


# ============================================================
# ASK MEETING AI / RAG
# ============================================================

elif page == "Ask Meeting AI":
    st.markdown("# Ask Meeting AI")
    st.caption(
        "Ask questions over your historical meeting repository. Retrieval happens first; answers are grounded in retrieved evidence."
    )

    question = st.text_area(
        "Your meeting question",
        height=130,
        placeholder=(
            "Who owns the API integration, what is the deadline, and what decision was made?"
        ),
    )

    c1, c2 = st.columns(2)
    with c1:
        top_k = st.slider(
            "Retrieved context chunks",
            1,
            8,
            5,
        )
    with c2:
        meeting_id = st.number_input(
            "Meeting ID · 0 = all meetings",
            min_value=0,
            step=1,
            value=0,
        )

    if st.button(
        "🤖 Ask Meeting AI",
        type="primary",
        use_container_width=True,
    ):
        if not question.strip():
            st.warning("Enter a question first.")
        else:
            try:
                with st.spinner(
                    "Retrieving evidence and generating an answer..."
                ):
                    result = get_rag_service().answer(
                        question.strip(),
                        top_k=top_k,
                        meeting_id=meeting_id or None,
                    )

                mode = result.get("mode", "unknown")
                if mode == "gemini":
                    status_badge("AI-grounded answer", "ok")
                elif mode == "local_fallback":
                    status_badge("Retrieval fallback", "warn")
                else:
                    status_badge(mode.replace("_", " "), "info")

                section_title("Answer")
                st.html(
                    f"""
                    <div class="insight-card">
                        {esc(result.get('answer', 'No answer available.'))}
                    </div>
                    """
                )

                display_sources(
                    result.get("sources", [])
                )

            except Exception as exc:
                st.error("Meeting AI failed.")
                st.exception(exc)


# ============================================================
# ACCURACY TESTING
# ============================================================

elif page == "Accuracy Testing":
    st.markdown("# Transcription Accuracy Lab")
    st.caption(
        "Compare a verified reference transcript with the Whisper transcript using Word Error Rate."
    )

    reference = st.text_area(
        "Reference transcript",
        height=220,
        placeholder="Paste the human-verified transcript...",
    )

    hypothesis = st.text_area(
        "Whisper transcript",
        height=220,
        placeholder="Paste the transcript generated by Whisper...",
    )

    if st.button(
        "📊 Calculate Transcription Accuracy",
        type="primary",
        use_container_width=True,
    ):
        if not reference.strip() or not hypothesis.strip():
            st.warning(
                "Provide both the reference and Whisper transcripts."
            )
        else:
            result = calculate_wer(
                reference,
                hypothesis,
            )

            c1, c2, c3 = st.columns(3)
            with c1:
                metric_card(
                    "Word Error Rate",
                    f"{result['wer']:.2%}",
                    "Lower is better",
                )
            with c2:
                metric_card(
                    "Estimated Accuracy",
                    f"{result['accuracy']:.2%}",
                    "Derived from WER",
                )
            with c3:
                metric_card(
                    "Reference Words",
                    result["reference_words"],
                    "Verified transcript",
                )

            st.json(result)
