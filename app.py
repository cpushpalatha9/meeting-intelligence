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
    page_title="AI-Career Intelligence Platform",
    page_icon="🧠",
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
        --ai-primary: #0f766e;
        --ai-primary-dark: #115e59;
        --ai-accent: #b58b3c;
        --ai-accent-soft: #f4ead4;
        --ai-ink: #18332D;
        --ai-muted: #6b7280;
        --ai-border: rgba(24,24,27,.10);
        --ai-surface: rgba(255,255,255,.88);
        --ai-dark: #18332D;
    }

    /* ============================================================
       FINAL TYPOGRAPHY + ACCESSIBILITY POLISH
       Light Emerald + Champagne Gold — high contrast, not black
       ============================================================ */

    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stSidebar"], .stApp {
        font-family: "Inter", "Aptos", "Segoe UI", system-ui, -apple-system,
                     BlinkMacSystemFont, sans-serif;
        color: #18332D;
    }

    /* Keep Streamlit's normal text readable on the light theme. */
    .stMarkdown, .stCaption, [data-testid="stCaptionContainer"],
    [data-testid="stText"], label, p, li {
        color: #42564F;
    }

    /* Remove the leaked Material-icon text that can appear in the
       sidebar collapse control on some Streamlit/browser combinations. */
    [data-testid="stSidebarCollapseButton"] {
        position: relative;
        z-index: 20;
    }

    [data-testid="stSidebarCollapseButton"] button {
        width: 34px !important;
        height: 34px !important;
        min-height: 34px !important;
        padding: 0 !important;
        overflow: hidden !important;
        color: #0F766E !important;
        background: rgba(15,118,110,.06) !important;
        border: 1px solid rgba(15,118,110,.10) !important;
        border-radius: 10px !important;
        font-size: 0 !important;
    }

    [data-testid="stSidebarCollapseButton"] button * {
        font-size: 0 !important;
    }

    [data-testid="stSidebarCollapseButton"] button::after {
        content: "‹";
        display: block;
        font-family: "Segoe UI", sans-serif;
        font-size: 22px !important;
        line-height: 30px;
        font-weight: 700;
        color: #0F766E;
    }

    /* Prevent horizontal overflow/scrolling inside the sidebar. */
    [data-testid="stSidebar"] .block-container,
    [data-testid="stSidebarContent"] {
        overflow-x: hidden !important;
    }

    [data-testid="stSidebar"] {
        overflow-x: hidden !important;
    }

    /* Stronger hierarchy while retaining emerald/gold rather than
       turning every word black. */
    h1, h2, h3, h4 {
        color: #18332D;
        font-family: "Inter", "Aptos", "Segoe UI", system-ui, sans-serif;
    }

    .ai-hero h1 {
        color: #18332D;
        text-shadow: 0 1px 0 rgba(255,255,255,.55);
    }

    .ai-gradient {
        background: linear-gradient(
            90deg,
            #168A6A 0%,
            #4F9F88 22%,
            #B58B3C 55%,
            #7C6940 78%,
            #18332D 100%
        );
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        -webkit-text-fill-color: transparent;
        text-shadow: none;
    }

    .ai-hero-description,
    .page-description,
    .workspace-text,
    .ai-module-text,
    .ai-record-summary,
    .repo-summary,
    .search-console-text,
    .ai-insight-text {
        color: #4E625B;
    }

    .ai-sidebar-label {
        color: #72857E;
    }

    .ai-sidebar-status {
        color: #42564F;
    }

    .ai-brand-caption {
        color: #657871;
    }

    .ai-brand-name {
        color: #18332D;
    }

    .ai-chip,
    .ai-command,
    .page-badge {
        color: #38564D;
    }

    .ai-kpi-label,
    .repo-stat-label,
    .step-detail,
    .repo-meta {
        color: #657871;
    }

    .ai-kpi-value,
    .ai-module-title,
    .ai-flow-title,
    .ai-record-title,
    .repo-title,
    .repo-stat-value,
    .search-console-title,
    .page-title,
    .workspace-title,
    .step-name {
        color: #18332D;
    }

    /* Streamlit controls */
    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input,
    .stSelectbox [data-baseweb="select"],
    .stMultiSelect [data-baseweb="select"] {
        color: #18332D !important;
        background: #FFFFFF !important;
    }

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #7A8B85 !important;
    }

    .stButton > button {
        color: #18332D;
    }

    .stButton > button[kind="primary"] {
        color: #FFFFFF !important;
    }

    /* Tables and expandable areas remain readable on the light theme. */
    [data-testid="stDataFrame"] {
        color: #18332D;
    }

    [data-testid="stExpander"] summary {
        color: #18332D !important;
        font-weight: 750;
    }

    /* Never allow pale text inside our premium cards. */
    .ai-module *,
    .ai-kpi *,
    .ai-record *,
    .repo-card *,
    .workspace-card *,
    .search-result *,
    .search-console *,
    .ai-insight * {
        text-shadow: none;
    }

    .block-container {
        max-width: 1500px;
        padding-top: .75rem;
        padding-bottom: 4rem;
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at 8% 0%, rgba(181,139,60,.055), transparent 23%),
            radial-gradient(circle at 95% 5%, rgba(35,132,104,.055), transparent 22%),
            #F7FAF8;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #F1F9F5 100%);
        border-right: 1px solid rgba(24,51,45,.09);
        box-shadow: 8px 0 28px rgba(24,51,45,.035);
    }

    [data-testid="stSidebar"] * {
        color: #42564F;
    }

    [data-testid="stSidebar"] .block-container {
        padding: 1.05rem .85rem 2rem;
    }

    .ai-brand { padding: 8px 8px 22px; }

    .ai-brand-icon {
        width: 52px;
        height: 52px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 15px;
        background: linear-gradient(135deg, #0f766e, #134e4a);
        box-shadow: 0 14px 30px rgba(15,118,110,.24);
        font-size: 1.35rem;
    }

    .ai-brand-name {
        margin-top: 13px;
        color: #18332D;
        font-size: 1.02rem;
        font-weight: 900;
        letter-spacing: -.035em;
        line-height: 1.1;
    }

    .ai-brand-name span { color: #9A762B; }

    .ai-brand-caption {
        margin-top: 6px;
        color: #80918B;
        font-size: .68rem;
        line-height: 1.55;
    }

    .ai-sidebar-label {
        margin: 18px 8px 8px;
        color: #8A9A94;
        font-size: .59rem;
        font-weight: 850;
        letter-spacing: .14em;
        text-transform: uppercase;
    }

    .ai-sidebar-status {
        margin: 18px 3px 0;
        padding: 13px;
        border: 1px solid rgba(24,51,45,.08);
        border-radius: 15px;
        background: rgba(35,132,104,.045);
        color: #52645E;
        font-size: .66rem;
        line-height: 1.65;
    }

    .ai-online { color: #6ee7b7; font-weight: 850; }

    [data-testid="stSidebar"] [role="radiogroup"] {
        width: 100% !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label {
        color: #42564F !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label p {
        color: #42564F !important;
    }

    [data-testid="stSidebar"] .stCaption {
        color: #657871 !important;
    }

    /* Premium charcoal / ivory hero */
    .ai-hero {
        position: relative;
        overflow: hidden;
        min-height: 360px;
        padding: 46px 48px;
        border-radius: 30px;
        color: #18332D;
        background:
            radial-gradient(circle at 85% 18%, rgba(181,139,60,.16), transparent 23%),
            radial-gradient(circle at 98% 100%, rgba(35,132,104,.14), transparent 29%),
            linear-gradient(135deg, #F1F9F5 0%, #FFFFFF 52%, #EAF6F0 100%);
        box-shadow: 0 28px 70px rgba(15,23,42,.18);
    }

    .ai-hero-grid {
        position: absolute;
        inset: 0;
        opacity: .075;
        background-image:
            linear-gradient(rgba(35,132,104,.12) 1px, transparent 1px),
            linear-gradient(90deg, rgba(35,132,104,.12) 1px, transparent 1px);
        background-size: 42px 42px;
        mask-image: linear-gradient(to bottom right, black, transparent 78%);
    }

    .ai-hero-orb {
        position: absolute;
        right: 8%;
        top: 13%;
        width: 205px;
        height: 205px;
        border: 1px solid rgba(181,139,60,.28);
        border-radius: 50%;
        box-shadow:
            0 0 0 22px rgba(181,139,60,.035),
            0 0 0 48px rgba(181,139,60,.018),
            inset 0 0 50px rgba(35,132,104,.10);
    }

    .ai-hero-orb::after {
        content: "✦";
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #9A762B;
        font-size: 2.8rem;
        text-shadow: 0 0 28px rgba(214,189,130,.45);
    }

    .ai-hero-content {
        position: relative;
        z-index: 3;
        max-width: 830px;
    }

    .ai-hero-status {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 11px;
        border: 1px solid rgba(24,51,45,.10);
        border-radius: 999px;
        background: rgba(35,132,104,.045);
        color: #587069;
        font-size: .63rem;
        font-weight: 850;
        letter-spacing: .10em;
        text-transform: uppercase;
    }

    .ai-hero-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #6ee7b7;
        box-shadow: 0 0 0 5px rgba(110,231,183,.08);
    }

    .ai-hero h1 {
        margin: 20px 0 0;
        font-size: clamp(2.35rem,5vw,4.35rem);
        line-height: .95;
        letter-spacing: -.065em;
        font-weight: 950;
    }

    .ai-gradient {
        background: linear-gradient(90deg, #0F766E 0%, #B58B3C 48%, #18332D 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        -webkit-text-fill-color: transparent;
    }

    .ai-hero-description {
        max-width: 720px;
        margin-top: 19px;
        color: #61746D;
        font-size: .93rem;
        line-height: 1.7;
    }

    .ai-chip {
        padding: 8px 12px;
        border: 1px solid rgba(255,255,255,.10);
        border-radius: 999px;
        background: rgba(35,132,104,.045);
        color: #4D635B;
        font-size: .67rem;
        font-weight: 750;
    }

    .ai-command-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 15px 0 20px;
        padding: 10px;
        border: 1px solid var(--ai-border);
        border-radius: 17px;
        background: rgba(255,255,255,.78);
        box-shadow: 0 8px 25px rgba(15,23,42,.03);
    }

    .ai-command {
        padding: 8px 11px;
        border-radius: 10px;
        background: rgba(15,118,110,.055);
        color: #4b5563;
        font-size: .66rem;
        font-weight: 800;
    }

    .ai-command strong { color: var(--ai-primary); }

    .ai-kpi {
        position: relative;
        overflow: hidden;
        min-height: 145px;
        padding: 20px;
        border: 1px solid var(--ai-border);
        border-radius: 21px;
        background: var(--ai-surface);
        box-shadow: 0 12px 32px rgba(15,23,42,.04);
    }

    .ai-kpi::before {
        content: "";
        position: absolute;
        right: -35px;
        bottom: -45px;
        width: 125px;
        height: 125px;
        border-radius: 50%;
        background: rgba(181,139,60,.055);
    }

    .ai-kpi-icon {
        width: 37px;
        height: 37px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        background: rgba(35,132,104,.085);
        color: var(--ai-primary);
        font-size: .95rem;
    }

    .ai-kpi-live {
        color: var(--ai-primary);
        font-size: .58rem;
        font-weight: 900;
        letter-spacing: .08em;
    }

    .ai-kpi-label {
        margin-top: 14px;
        color: var(--ai-muted);
        font-size: .62rem;
        font-weight: 900;
        letter-spacing: .10em;
        text-transform: uppercase;
    }

    .ai-kpi-value {
        margin-top: 4px;
        font-size: 1.95rem;
        font-weight: 950;
        letter-spacing: -.06em;
    }

    .ai-kpi-sub {
        margin-top: 5px;
        color: #81928C;
        font-size: .66rem;
    }

    .ai-section {
        display: flex;
        align-items: end;
        justify-content: space-between;
        gap: 18px;
        margin: 32px 0 13px;
    }

    .ai-section-label {
        color: var(--ai-primary);
        font-size: .59rem;
        font-weight: 900;
        letter-spacing: .14em;
        text-transform: uppercase;
    }

    .ai-section-title {
        margin-top: 3px;
        font-size: 1.22rem;
        font-weight: 950;
        letter-spacing: -.04em;
        color: var(--ai-ink);
    }

    .ai-section-sub {
        max-width: 650px;
        color: var(--ai-muted);
        font-size: .72rem;
        line-height: 1.55;
        text-align: right;
    }

    .ai-module {
        min-height: 190px;
        padding: 21px;
        border: 1px solid var(--ai-border);
        border-radius: 21px;
        background: rgba(255,255,255,.92);
        box-shadow: 0 9px 28px rgba(15,23,42,.03);
    }

    .ai-module-icon {
        width: 42px;
        height: 42px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 13px;
        background: linear-gradient(135deg,rgba(35,132,104,.10),rgba(181,139,60,.085));
        font-size: 1.05rem;
    }

    .ai-module-title {
        margin-top: 13px;
        font-size: .91rem;
        font-weight: 900;
        color: var(--ai-ink);
    }

    .ai-module-text {
        margin-top: 6px;
        color: var(--ai-muted);
        font-size: .71rem;
        line-height: 1.6;
    }

    .ai-module-footer {
        margin-top: 13px;
        color: var(--ai-primary);
        font-size: .62rem;
        font-weight: 850;
    }

    .ai-flow {
        display: flex;
        align-items: stretch;
        gap: 7px;
        overflow-x: auto;
        padding: 2px 0 8px;
    }

    .ai-flow-node {
        flex: 1;
        min-width: 130px;
        padding: 17px 12px;
        border: 1px solid var(--ai-border);
        border-radius: 17px;
        background: rgba(255,255,255,.78);
        text-align: center;
    }

    .ai-flow-number { color: var(--ai-primary); font-size: .58rem; font-weight: 900; letter-spacing: .12em; }
    .ai-flow-title { margin-top: 6px; font-size: .76rem; font-weight: 900; }
    .ai-flow-desc { margin-top: 3px; color: var(--ai-muted); font-size: .60rem; }
    .ai-flow-arrow { align-self: center; color: #9ca3af; font-weight: 900; }

    .ai-insight {
        position: relative;
        overflow: hidden;
        min-height: 190px;
        padding: 23px;
        border: 1px solid rgba(35,132,104,.14);
        border-radius: 22px;
        background:
            radial-gradient(circle at 100% 0%,rgba(181,139,60,.095),transparent 38%),
            linear-gradient(135deg,rgba(35,132,104,.055),rgba(181,139,60,.035));
    }

    .ai-insight-label { color: var(--ai-primary); font-size: .60rem; font-weight: 900; letter-spacing: .13em; text-transform: uppercase; }
    .ai-insight-title { margin-top: 7px; font-size: 1.05rem; font-weight: 900; }
    .ai-insight-text { margin-top: 7px; max-width: 850px; color: var(--ai-muted); font-size: .75rem; line-height: 1.65; }

    .ai-record {
        padding: 17px;
        border: 1px solid var(--ai-border);
        border-radius: 18px;
        background: rgba(255,255,255,.92);
    }

    .ai-record-title { font-size: .87rem; font-weight: 900; }
    .ai-record-meta { margin-top: 4px; color: #81928C; font-size: .63rem; }
    .ai-record-summary { margin-top: 8px; color: var(--ai-muted); font-size: .70rem; line-height: 1.55; }

    .ai-status {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 7px 10px;
        border-radius: 999px;
        font-size: .61rem;
        font-weight: 850;
    }

    .ai-status-ok { background: rgba(35,132,104,.09); color: #0f766e; }
    .ai-status-warn { background: rgba(181,139,60,.11); color: #8a6a28; }

    .stButton > button {
        min-height: 42px;
        border-radius: 12px;
        font-weight: 800;
        transition: transform .15s ease, box-shadow .15s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 20px rgba(15,23,42,.08);
    }

    .stTextInput input, .stTextArea textarea, .stNumberInput input { border-radius: 12px; }
    
    /* ============================================================
       EXECUTIVE EMERALD + CHAMPAGNE GOLD — ALL-PAGE UI LAYER
       ============================================================ */

    .page-hero {
        position: relative;
        overflow: hidden;
        margin-bottom: 20px;
        padding: 28px 30px;
        border: 1px solid rgba(35,132,104,.12);
        border-radius: 24px;
        background:
            radial-gradient(circle at 92% 8%, rgba(181,139,60,.12), transparent 25%),
            linear-gradient(135deg, #FFFFFF 0%, #F4FAF7 58%, #E8F5EE 100%);
        box-shadow: 0 15px 40px rgba(15,23,42,.045);
    }

    .page-hero::after {
        content: "";
        position: absolute;
        width: 170px;
        height: 170px;
        right: -55px;
        bottom: -85px;
        border: 1px solid rgba(181,139,60,.22);
        border-radius: 50%;
    }

    .page-kicker {
        color: #0f766e;
        font-size: .59rem;
        font-weight: 900;
        letter-spacing: .15em;
        text-transform: uppercase;
    }

    .page-title {
        margin-top: 6px;
        color: #18332D;
        font-size: 1.8rem;
        font-weight: 950;
        letter-spacing: -.045em;
    }

    .page-description {
        max-width: 820px;
        margin-top: 7px;
        color: #61746D;
        font-size: .77rem;
        line-height: 1.65;
    }

    .page-badges {
        position: relative;
        z-index: 2;
        display: flex;
        flex-wrap: wrap;
        gap: 7px;
        margin-top: 15px;
    }

    .page-badge {
        padding: 6px 9px;
        border: 1px solid rgba(35,132,104,.10);
        border-radius: 999px;
        background: rgba(255,255,255,.78);
        color: #52645E;
        font-size: .61rem;
        font-weight: 800;
    }

    .page-badge.gold {
        border-color: rgba(181,139,60,.16);
        background: rgba(181,139,60,.075);
        color: #866727;
    }

    .workspace-card {
        padding: 21px;
        border: 1px solid rgba(15,23,42,.09);
        border-radius: 20px;
        background: rgba(255,255,255,.94);
        box-shadow: 0 10px 30px rgba(15,23,42,.035);
    }

    .workspace-card-dark {
        color: #18332D;
        border-color: rgba(15,118,110,.13);
        background: linear-gradient(135deg,#F1F9F5,#FFFFFF);
    }

    .workspace-label {
        color: #0f766e;
        font-size: .59rem;
        font-weight: 900;
        letter-spacing: .13em;
        text-transform: uppercase;
    }

    .workspace-card-dark .workspace-label {
        color: #9A762B;
    }

    .workspace-title {
        margin-top: 6px;
        color: #18332D;
        font-size: 1rem;
        font-weight: 900;
    }

    .workspace-card-dark .workspace-title { color: #18332D; }

    .workspace-text {
        margin-top: 6px;
        color: #61746D;
        font-size: .71rem;
        line-height: 1.6;
    }

    .workspace-card-dark .workspace-text {
        color: #61746D;
    }

    .step-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 7px;
        margin: 14px 0 20px;
    }

    .step {
        flex: 1;
        min-width: 115px;
        padding: 12px 13px;
        border: 1px solid rgba(15,23,42,.08);
        border-radius: 14px;
        background: white;
    }

    .step-number {
        color: #b58b3c;
        font-size: .57rem;
        font-weight: 900;
        letter-spacing: .1em;
    }

    .step-name {
        margin-top: 4px;
        color: #18332D;
        font-size: .68rem;
        font-weight: 900;
    }

    .step-detail {
        margin-top: 2px;
        color: #81928C;
        font-size: .58rem;
    }

    .gold-divider {
        height: 1px;
        margin: 18px 0;
        background: linear-gradient(90deg, rgba(181,139,60,.35), rgba(35,132,104,.08), transparent);
    }

    .repo-card {
        padding: 20px;
        margin-bottom: 12px;
        border: 1px solid rgba(15,23,42,.09);
        border-radius: 20px;
        background: rgba(255,255,255,.94);
        box-shadow: 0 9px 27px rgba(15,23,42,.03);
    }

    .repo-title {
        color: #18332D;
        font-size: .96rem;
        font-weight: 900;
    }

    .repo-meta {
        margin-top: 5px;
        color: #81928C;
        font-size: .61rem;
    }

    .repo-summary {
        margin-top: 9px;
        color: #61746D;
        font-size: .72rem;
        line-height: 1.62;
    }

    .repo-stat {
        padding: 11px;
        border-radius: 13px;
        background: #f6f8f7;
        text-align: center;
    }

    .repo-stat-value {
        color: #18332D;
        font-size: 1.05rem;
        font-weight: 900;
    }

    .repo-stat-label {
        margin-top: 2px;
        color: #81928C;
        font-size: .57rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: .07em;
    }

    .search-console {
        padding: 22px;
        border: 1px solid rgba(35,132,104,.12);
        border-radius: 21px;
        background: linear-gradient(135deg,rgba(35,132,104,.055),rgba(181,139,60,.035));
    }

    .search-console-title {
        color: #18332D;
        font-size: .98rem;
        font-weight: 900;
    }

    .search-console-text {
        margin-top: 5px;
        color: #61746D;
        font-size: .70rem;
        line-height: 1.6;
    }

    .search-result {
        position: relative;
        padding: 18px 19px;
        margin-top: 10px;
        border: 1px solid rgba(15,23,42,.08);
        border-radius: 18px;
        background: white;
    }

    .search-result-index {
        color: #b58b3c;
        font-size: .58rem;
        font-weight: 900;
        letter-spacing: .11em;
    }

    .search-result-meta {
        margin-top: 5px;
        color: #0f766e;
        font-size: .61rem;
        font-weight: 800;
    }

    .search-result-text {
        margin-top: 9px;
        color: #52645E;
        font-size: .73rem;
        line-height: 1.65;
    }

    .ai-console {
        position: relative;
        overflow: hidden;
        padding: 27px;
        margin-bottom: 17px;
        border-radius: 23px;
        color: #18332D;
        background: linear-gradient(135deg,#F1F9F5,#FFFFFF 62%,#E8F5EE);
    }

    .ai-console::after {
        content: "✦";
        position: absolute;
        right: 32px;
        top: 20px;
        color: rgba(214,189,130,.25);
        font-size: 4rem;
    }

    .ai-console-label {
        color: #9A762B;
        font-size: .59rem;
        font-weight: 900;
        letter-spacing: .15em;
        text-transform: uppercase;
    }

    .ai-console-title {
        margin-top: 6px;
        font-size: 1.35rem;
        font-weight: 950;
        letter-spacing: -.04em;
    }

    .ai-console-text {
        max-width: 760px;
        margin-top: 7px;
        color: #52645E;
        font-size: .74rem;
        line-height: 1.65;
    }

    .answer-card {
        padding: 23px;
        border: 1px solid rgba(35,132,104,.12);
        border-radius: 21px;
        background: white;
        box-shadow: 0 10px 30px rgba(15,23,42,.035);
    }

    .answer-label {
        color: #0f766e;
        font-size: .59rem;
        font-weight: 900;
        letter-spacing: .13em;
        text-transform: uppercase;
    }

    .answer-body {
        margin-top: 10px;
        color: #344054;
        font-size: .82rem;
        line-height: 1.75;
    }

    .evidence-banner {
        padding: 13px 15px;
        border-left: 3px solid #b58b3c;
        border-radius: 10px;
        background: #FCFAF4;
        color: #61746D;
        font-size: .68rem;
        line-height: 1.55;
    }

    .accuracy-console {
        padding: 23px;
        border: 1px solid rgba(35,132,104,.12);
        border-radius: 22px;
        background: linear-gradient(135deg,#F1F9F5,#fffdf8);
    }

    .accuracy-title {
        color: #18332D;
        font-size: 1rem;
        font-weight: 900;
    }

    .accuracy-text {
        margin-top: 5px;
        color: #61746D;
        font-size: .71rem;
        line-height: 1.6;
    }

    .quality-card {
        min-height: 130px;
        padding: 19px;
        border: 1px solid rgba(15,23,42,.09);
        border-radius: 18px;
        background: white;
    }

    .quality-label {
        color: #81928C;
        font-size: .59rem;
        font-weight: 850;
        letter-spacing: .09em;
        text-transform: uppercase;
    }

    .quality-value {
        margin-top: 8px;
        color: #18332D;
        font-size: 1.55rem;
        font-weight: 950;
        letter-spacing: -.05em;
    }

    .quality-note {
        margin-top: 4px;
        color: #0f766e;
        font-size: .62rem;
        font-weight: 800;
    }

    .process-input-card {
        padding: 22px;
        border: 1px solid rgba(15,23,42,.09);
        border-radius: 21px;
        background: white;
    }

    .process-mode {
        padding: 12px 14px;
        border: 1px solid rgba(35,132,104,.10);
        border-radius: 13px;
        background: #F1F9F5;
        color: #52645E;
        font-size: .67rem;
        font-weight: 800;
    }

    /* More polished expanders/tables without altering their behavior. */
    [data-testid="stExpander"] {
        border-radius: 16px !important;
        border-color: rgba(15,23,42,.08) !important;
    }

    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
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
        <div class="ai-kpi">
            <div class="ai-kpi-top">
                <div class="ai-kpi-icon">{esc(icon)}</div>
                <div class="ai-kpi-live">● LIVE</div>
            </div>
            <div class="ai-kpi-label">{esc(label)}</div>
            <div class="ai-kpi-value">{esc(value)}</div>
            <div class="ai-kpi-sub">{esc(sub)}</div>
        </div>
        """
    )


def section_title(title, subtitle=None):
    st.html(
        f"""
        <div class="ai-section">
            <div>
                <div class="ai-section-label">AI INTELLIGENCE MODULE</div>
                <div class="ai-section-title">{esc(title)}</div>
            </div>
            {f'<div class="ai-section-sub">{esc(subtitle)}</div>' if subtitle else ''}
        </div>
        """
    )



def status_badge(text, kind="info"):
    mapped = "ok" if kind == "ok" else "warn" if kind == "warn" else "ok"
    st.html(
        f'<span class="ai-status ai-status-{mapped}">● {esc(text)}</span>'
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
        <div class="ai-brand">
            <div class="ai-brand-icon">🧠</div>
            <div class="ai-brand-name">AI-Career<br><span>Intelligence Platform</span></div>
            <div class="ai-brand-caption">
                Your intelligent command center for professional knowledge,
                insights and action.
            </div>
        </div>
        """
    )

    st.html('<div class="ai-sidebar-label">COMMAND CENTER</div>')

    page = st.radio(
        "Workspace",
        [
            "Dashboard",
            "Process Intelligence",
            "Intelligence Repository",
            "Intelligence Search",
            "Ask Career AI",
            "Accuracy Lab",
        ],
        label_visibility="collapsed",
    )

    st.html('<div class="ai-sidebar-label">AI ENGINE</div>')

    st.html(
        f"""
        <div class="ai-sidebar-status">
            <span class="ai-online">● SYSTEM ONLINE</span><br>
            Gemini · {esc(GEMINI_MODEL)}<br>
            Whisper · {esc(WHISPER_MODEL)}<br>
            Vector Memory · ChromaDB<br>
            Retrieval · RAG
        </div>
        """
    )

    st.html('<div class="ai-sidebar-label">INTELLIGENCE FLOW</div>')
    st.caption("🎙 Capture  →  📝 Transcribe")
    st.caption("🧠 Analyze  →  💾 Store")
    st.caption("⌁ Retrieve  →  ✦ Answer")

    st.html('<div class="ai-sidebar-label">PLATFORM</div>')
    st.caption("M1 · Ingestion + NLP")
    st.caption("M2 · AI Intelligence")
    st.caption("M3 · Semantic Memory")


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
        indexed_chunks = get_indexing_service().get_index_status().get("count", 0)
    except Exception:
        indexed_chunks = 0

    # ---------- HERO ----------
    st.html(
        """
        <div class="ai-hero">
            <div class="ai-hero-grid"></div>
            <div class="ai-hero-orb"></div>
            <div class="ai-hero-content">
                <div class="ai-hero-status">
                    <span class="ai-hero-dot"></span>
                    AI CAREER INTELLIGENCE · LIVE WORKSPACE
                </div>
                <h1>AI-Career<br><span class="ai-gradient">Intelligence Platform</span></h1>
                <div class="ai-hero-description">
                    A unified intelligence workspace that transforms professional
                    conversations and knowledge into structured insights,
                    searchable memory, actionable outcomes and AI-assisted decisions.
                </div>
                <div class="ai-hero-buttons">
                    <span class="ai-chip">✦ Generative AI</span>
                    <span class="ai-chip">⌁ Semantic Memory</span>
                    <span class="ai-chip">◈ Intelligence Analytics</span>
                    <span class="ai-chip">✓ Action Intelligence</span>
                </div>
            </div>
        </div>
        """
    )

    # ---------- COMMAND BAR ----------
    st.html(
        """
        <div class="ai-command-bar">
            <span class="ai-command"><strong>01</strong> CAPTURE</span>
            <span class="ai-command"><strong>02</strong> UNDERSTAND</span>
            <span class="ai-command"><strong>03</strong> STRUCTURE</span>
            <span class="ai-command"><strong>04</strong> REMEMBER</span>
            <span class="ai-command"><strong>05</strong> RETRIEVE</span>
            <span class="ai-command"><strong>06</strong> ACT</span>
        </div>
        """
    )

    # ---------- KPI GRID ----------
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Knowledge Records", total_meetings, "Processed intelligence", "◈")
    with c2:
        metric_card("Action Signals", total_actions, "Work items detected", "✓")
    with c3:
        metric_card("Decision Signals", total_decisions, "Outcomes identified", "◆")
    with c4:
        metric_card("Semantic Memory", indexed_chunks, "Indexed knowledge chunks", "⌁")

    # ---------- EXECUTIVE INSIGHT ----------
    section_title(
        "Career intelligence overview",
        "A unified command layer connecting captured knowledge, AI reasoning and searchable organizational memory.",
    )

    st.html(
        """
        <div class="ai-insight">
            <div class="ai-insight-label">✦ EXECUTIVE INTELLIGENCE</div>
            <div class="ai-insight-title">From raw information to actionable intelligence.</div>
            <div class="ai-insight-text">
                Capture conversations and source knowledge, analyze them with AI,
                preserve structured outcomes, and retrieve relevant evidence when
                a decision or follow-up requires context.
            </div>
        </div>
        """
    )

    # ---------- INTELLIGENCE MODULES ----------
    section_title(
        "Intelligence modules",
        "The platform is organized around four product-level intelligence capabilities.",
    )

    modules = [
        ("🧠", "Knowledge Intelligence",
         "Capture transcripts and professional knowledge, then convert unstructured information into structured records.",
         "CAPTURE → STRUCTURE"),
        ("🎯", "Action Intelligence",
         "Extract decisions, responsibilities, deadlines, priorities and follow-up work from analyzed content.",
         "INSIGHT → ACTION"),
        ("⌁", "Semantic Memory",
         "Build persistent vector memory so historical knowledge can be discovered through meaning rather than keywords.",
         "MEMORY → RETRIEVAL"),
        ("✦", "Career AI",
         "Ask natural-language questions and generate evidence-grounded answers using retrieved intelligence.",
         "QUESTION → ANSWER"),
    ]

    module_cols = st.columns(4)
    for i, (icon, title, description, footer) in enumerate(modules):
        with module_cols[i]:
            st.html(
                f"""
                <div class="ai-module">
                    <div class="ai-module-icon">{icon}</div>
                    <div class="ai-module-title">{esc(title)}</div>
                    <div class="ai-module-text">{esc(description)}</div>
                    <div class="ai-module-footer">{esc(footer)} →</div>
                </div>
                """
            )

    # ---------- INTELLIGENCE FLOW ----------
    section_title(
        "Intelligence operating model",
        "One continuous flow from source information to evidence-grounded answers.",
    )

    steps = [
        ("01", "Capture", "Audio / text"),
        ("02", "Transcribe", "Whisper"),
        ("03", "Analyze", "NLP + LLM"),
        ("04", "Structure", "Insights"),
        ("05", "Remember", "ChromaDB"),
        ("06", "Retrieve", "Semantic"),
        ("07", "Answer", "RAG"),
    ]

    flow = '<div class="ai-flow">'
    for i, (number, label, desc) in enumerate(steps):
        flow += f"""
        <div class="ai-flow-node">
            <div class="ai-flow-number">{number}</div>
            <div class="ai-flow-title">{esc(label)}</div>
            <div class="ai-flow-desc">{esc(desc)}</div>
        </div>
        """
        if i < len(steps) - 1:
            flow += '<div class="ai-flow-arrow">→</div>'
    flow += "</div>"
    st.html(flow)

    # ---------- PLATFORM READINESS ----------
    section_title(
        "Platform health",
        "Live status of the intelligence infrastructure currently connected to the dashboard.",
    )

    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.html('<div class="ai-module"><span class="ai-status ai-status-ok">● DATABASE READY</span><div class="ai-module-title">Persistent storage</div><div class="ai-module-text">SQLite intelligence repository is available.</div></div>')
    with r2:
        if GEMINI_API_KEY:
            st.html('<div class="ai-module"><span class="ai-status ai-status-ok">● AI READY</span><div class="ai-module-title">Gemini connected</div><div class="ai-module-text">LLM processing layer is configured.</div></div>')
        else:
            st.html('<div class="ai-module"><span class="ai-status ai-status-warn">● ACTION NEEDED</span><div class="ai-module-title">Gemini key</div><div class="ai-module-text">Configure GEMINI_API_KEY in the environment.</div></div>')
    with r3:
        st.html('<div class="ai-module"><span class="ai-status ai-status-ok">● WHISPER READY</span><div class="ai-module-title">Speech intelligence</div><div class="ai-module-text">Local transcription engine is available.</div></div>')
    with r4:
        st.html('<div class="ai-module"><span class="ai-status ai-status-ok">● MEMORY READY</span><div class="ai-module-title">Vector retrieval</div><div class="ai-module-text">ChromaDB semantic memory is available.</div></div>')

    # ---------- CAPABILITY MATRIX ----------
    section_title(
        "Capability matrix",
        "A concise view of what the platform can currently process and retrieve.",
    )

    capabilities = [
        ("M1", "Smart ingestion", "Audio/video upload, transcript input, validation and local speech-to-text."),
        ("M1", "NLP intelligence", "Normalization, preprocessing, noise filtering and VADER sentiment analysis."),
        ("M2", "Structured intelligence", "Summary, key points, decisions, action items and participant mapping."),
        ("M2", "Operational tracking", "Ownership, deadline, priority and status extraction for follow-up work."),
        ("M3", "Semantic memory", "Chunking, embeddings, metadata and persistent ChromaDB indexing."),
        ("M3", "Evidence-grounded AI", "Semantic retrieval followed by RAG answers with visible source evidence."),
    ]

    cap_cols = st.columns(3)
    for i, (milestone, title, text) in enumerate(capabilities):
        with cap_cols[i % 3]:
            st.html(
                f"""
                <div class="ai-module">
                    <span class="ai-status ai-status-ok">{esc(milestone)}</span>
                    <div class="ai-module-title">{esc(title)}</div>
                    <div class="ai-module-text">{esc(text)}</div>
                </div>
                """
            )

    # ---------- RECENT RECORDS ----------
    section_title(
        "Recent intelligence records",
        "Your latest processed knowledge records.",
    )

    if not meetings:
        empty_state(
            "🧠",
            "Intelligence workspace is ready",
            "Open Process Intelligence to create your first intelligence record.",
        )
    else:
        for meeting in meetings[:6]:
            with st.container(border=True):
                a, b, c = st.columns([5, 2, 1])
                with a:
                    st.html(
                        f"""
                        <div class="ai-record">
                            <div class="ai-record-title">{esc(meeting.get('title', 'Untitled record'))}</div>
                            <div class="ai-record-meta">INTELLIGENCE RECORD · #{esc(meeting.get('id'))}</div>
                            <div class="ai-record-summary">{esc((meeting.get('summary') or 'No summary available.')[:260])}</div>
                        </div>
                        """
                    )
                with b:
                    st.caption(str(meeting.get("created_at", "")))
                    status_badge("Processed", "ok")
                with c:
                    st.metric(
                        "Actions",
                        len(meeting.get("action_items", [])),
                    )


# ============================================================
# PROCESS MEETING
# ============================================================

elif page == "Process Intelligence":
    st.html(
        """
        <div class="page-hero">
            <div class="page-kicker">01 · INTELLIGENCE WORKSPACE</div>
            <div class="page-title">Process Intelligence</div>
            <div class="page-description">
                Transform an audio recording or transcript into structured intelligence,
                persistent memory and evidence-ready knowledge through one continuous pipeline.
            </div>
            <div class="page-badges">
                <span class="page-badge">🎙 Whisper</span>
                <span class="page-badge">✦ Gemini</span>
                <span class="page-badge">⌁ ChromaDB</span>
                <span class="page-badge gold">✓ SQLite</span>
            </div>
        </div>
        """
    )

    st.html(
        """
        <div class="step-strip">
            <div class="step"><div class="step-number">01</div><div class="step-name">INGEST</div><div class="step-detail">Audio / text</div></div>
            <div class="step"><div class="step-number">02</div><div class="step-name">TRANSCRIBE</div><div class="step-detail">Whisper</div></div>
            <div class="step"><div class="step-number">03</div><div class="step-name">UNDERSTAND</div><div class="step-detail">NLP + LLM</div></div>
            <div class="step"><div class="step-number">04</div><div class="step-name">PERSIST</div><div class="step-detail">SQLite</div></div>
            <div class="step"><div class="step-number">05</div><div class="step-name">REMEMBER</div><div class="step-detail">Embeddings</div></div>
        </div>
        """
    )

    title = st.text_input(
        "Intelligence record title",
        placeholder="e.g. Product Sprint Planning — September 24",
    )

    input_mode = st.radio(
        "Input source",
        ["🎙️ Audio / Video Recording", "📄 Existing Transcript"],
        horizontal=True,
    )

    st.html(
        f"""
        <div class="process-input-card">
            <div class="workspace-label">SOURCE CONFIGURATION</div>
            <div class="workspace-title">Choose how intelligence enters the platform.</div>
            <div class="workspace-text">
                Recordings are transcribed locally with Faster-Whisper.
                Existing transcripts can be processed directly through the same downstream pipeline.
            </div>
        </div>
        """
    )

    uploaded_file = None
    manual_transcript = ""

    if input_mode == "🎙️ Audio / Video Recording":
        uploaded_file = st.file_uploader(
            "Upload meeting recording",
            type=["mp3", "wav", "m4a", "mp4", "webm", "ogg", "flac", "aac"],
            help="The recording is transcribed locally with Faster-Whisper.",
        )

        if uploaded_file:
            st.audio(uploaded_file)
            st.html(
                f"""
                <div class="evidence-banner">
                    <strong>Source ready</strong> · {esc(uploaded_file.name)}
                    · {uploaded_file.size / 1024 / 1024:.2f} MB
                </div>
                """
            )
    else:
        manual_transcript = st.text_area(
            "Source transcript",
            height=300,
            placeholder="Paste the complete meeting transcript here...",
        )

    st.html(
        """
        <div class="gold-divider"></div>
        """
    )

    if st.button(
        "🚀 Run Intelligence Pipeline",
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
                "Running the intelligence pipeline...",
                expanded=True,
            ) as status:
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

                st.write(f"✓ Transcript validated · {len(transcript.split())} words")

                st.write("### Milestone 1 · NLP & Sentiment")
                processed_text = preprocess_text(transcript)
                sentiment = analyze_sentiment(transcript)
                st.write("✓ Preprocessing completed")
                st.write(f"✓ VADER sentiment: `{sentiment.get('label', 'neutral')}`")

                st.write("### Milestone 2 · Meeting Intelligence")
                if not GEMINI_API_KEY:
                    raise ValueError("GEMINI_API_KEY is missing. Add it to .env.")

                intelligence = LLMService().process_long_transcript(transcript)
                intelligence["action_items"] = clean_action_items(
                    intelligence.get("action_items", [])
                )
                intelligence["participants"] = clean_participants(
                    intelligence.get("participants", [])
                )

                st.write("✓ Structured summary generated")
                st.write("✓ Decisions and action items extracted")
                st.write("✓ Participants and responsibilities mapped")

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

                st.write("### Milestone 3 · Semantic Memory")
                indexing = index_meeting(meeting_id)
                if indexing.get("success"):
                    st.write(f"✓ Indexed {indexing.get('chunks_indexed', 0)} transcript chunks")
                else:
                    st.write("⚠ Meeting saved, but vector indexing needs attention.")

                status.update(
                    label="Intelligence pipeline completed",
                    state="complete",
                )

            st.success(
                f"Meeting #{meeting_id} is now available across repository, search and RAG."
            )

            render_intelligence(intelligence, sentiment, language)

            section_title("Transcript", "Original source captured by the platform.")
            with st.expander("Open complete transcript", expanded=False):
                st.text_area(
                    "Transcript",
                    transcript,
                    height=340,
                    disabled=True,
                    label_visibility="collapsed",
                )

            section_title("Processed NLP text", "Normalized text used by the analysis layer.")
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

elif page == "Intelligence Repository":
    meetings = get_all_meetings()

    st.html(
        """
        <div class="page-hero">
            <div class="page-kicker">02 · KNOWLEDGE VAULT</div>
            <div class="page-title">Intelligence Repository</div>
            <div class="page-description">
                A persistent knowledge vault for transcripts, decisions, action items,
                participants and semantic memory — designed for fast review and retrieval.
            </div>
            <div class="page-badges">
                <span class="page-badge">SQLite Records</span>
                <span class="page-badge">Structured Intelligence</span>
                <span class="page-badge gold">ChromaDB Memory</span>
            </div>
        </div>
        """
    )

    total_actions = sum(len(m.get("action_items", [])) for m in meetings)
    total_participants = sum(len(m.get("participants", [])) for m in meetings)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Knowledge Records", len(meetings), "SQLite intelligence")
    with c2:
        metric_card("Action Signals", total_actions, "Tracked work")
    with c3:
        metric_card("People Detected", total_participants, "Participant evidence")
    with c4:
        try:
            count = get_indexing_service().get_index_status().get("count", 0)
        except Exception:
            count = 0
        metric_card("Semantic Chunks", count, "Vector memory")

    st.html(
        """
        <div class="workspace-card">
            <div class="workspace-label">REPOSITORY CONTROL</div>
            <div class="workspace-title">Find, inspect and re-index your intelligence records.</div>
            <div class="workspace-text">
                Search by title or summary, open the full intelligence payload,
                and refresh semantic indexing whenever the knowledge base changes.
            </div>
        </div>
        """
    )

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
            "No matching intelligence records",
            "Process a meeting or change the repository filter.",
        )

    for meeting in meetings:
        with st.container(border=True):
            a, b, c = st.columns([5, 2.1, 1.2])

            with a:
                st.html(
                    f"""
                    <div class="repo-card">
                        <div class="repo-title">{esc(meeting.get('title', 'Untitled record'))}</div>
                        <div class="repo-meta">
                            RECORD #{esc(meeting.get('id'))}
                            · {esc(meeting.get('created_at', ''))}
                            · LANGUAGE {esc(meeting.get('language', 'unknown')).upper()}
                        </div>
                        <div class="repo-summary">
                            {esc((meeting.get('summary') or 'No summary available.')[:420])}
                        </div>
                    </div>
                    """
                )

            with b:
                st.html(
                    f"""
                    <div class="repo-stat">
                        <div class="repo-stat-value">{len(meeting.get('action_items', []))}</div>
                        <div class="repo-stat-label">Actions</div>
                    </div>
                    <br>
                    <div class="repo-stat">
                        <div class="repo-stat-value">{len(meeting.get('participants', []))}</div>
                        <div class="repo-stat-label">Participants</div>
                    </div>
                    """
                )

            with c:
                if st.button(
                    "↻ Re-index",
                    key=f"reindex_{meeting['id']}",
                    use_container_width=True,
                ):
                    result = index_meeting(meeting["id"])
                    if result.get("success"):
                        st.success(f"{result.get('chunks_indexed', 0)} chunks")
                    else:
                        st.error(result.get("error", "Indexing failed."))

            with st.expander("Open intelligence record"):
                left, right = st.columns(2)

                with left:
                    section_title("Decisions")
                    decisions = meeting.get("decisions", [])
                    if decisions:
                        for item in decisions:
                            st.markdown(f"• {item}")
                    else:
                        st.caption("No decisions recorded.")

                    section_title("Deadlines")
                    deadlines = meeting.get("deadlines", []) or []
                    if deadlines:
                        for item in deadlines:
                            st.markdown(f"• {item}")
                    else:
                        st.caption("No deadlines recorded.")

                with right:
                    section_title("Action items")
                    if meeting.get("action_items"):
                        st.dataframe(
                            meeting["action_items"],
                            use_container_width=True,
                            hide_index=True,
                        )
                    else:
                        st.caption("No action items recorded.")

                section_title("Transcript")
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

elif page == "Intelligence Search":
    st.html(
        """
        <div class="page-hero">
            <div class="page-kicker">03 · SEMANTIC DISCOVERY</div>
            <div class="page-title">Intelligence Search</div>
            <div class="page-description">
                Search your historical knowledge by meaning rather than exact keywords.
                Embeddings and ChromaDB retrieve the most relevant evidence for each query.
            </div>
            <div class="page-badges">
                <span class="page-badge">⌁ Embeddings</span>
                <span class="page-badge">◈ ChromaDB</span>
                <span class="page-badge gold">Evidence Retrieval</span>
            </div>
        </div>
        """
    )

    st.html(
        """
        <div class="search-console">
            <div class="search-console-title">Semantic Intelligence Console</div>
            <div class="search-console-text">
                Ask naturally — the system converts your question into a semantic query,
                searches indexed transcript chunks and returns ranked evidence.
            </div>
        </div>
        """
    )

    query = st.text_input(
        "Search your intelligence memory",
        placeholder="e.g. What deadline was agreed for the API integration?",
    )

    c1, c2 = st.columns(2)
    with c1:
        top_k = st.slider("Number of results", 1, 10, 5)
    with c2:
        meeting_id = st.number_input(
            "Record ID · 0 = all records",
            min_value=0,
            step=1,
            value=0,
        )

    if st.button(
        "⌁ Search Semantic Memory",
        type="primary",
        use_container_width=True,
    ):
        if not query.strip():
            st.warning("Enter a search question first.")
        else:
            try:
                with st.spinner("Searching semantic memory..."):
                    results = get_search_service().search(
                        query.strip(),
                        top_k=top_k,
                        meeting_id=meeting_id or None,
                    )

                if not results:
                    empty_state(
                        "⌁",
                        "No relevant context",
                        "Try another question or index the meeting repository.",
                    )
                else:
                    status_badge(f"{len(results)} relevant chunk(s) found", "ok")

                    section_title(
                        "Ranked evidence",
                        "Results are ordered by semantic relevance.",
                    )

                    for i, result in enumerate(results, 1):
                        similarity = float(result.get("similarity", 0) or 0)
                        st.html(
                            f"""
                            <div class="search-result">
                                <div class="search-result-index">EVIDENCE {i:02d} · RELEVANCE {similarity:.3f}</div>
                                <div class="search-result-meta">
                                    MEETING #{esc(result.get('meeting_id'))}
                                    · {esc(result.get('meeting_title', 'Meeting'))}
                                    · CHUNK {esc(result.get('chunk_id'))}
                                </div>
                                <div class="search-result-text">
                                    {esc(result.get('document', ''))}
                                </div>
                            </div>
                            """
                        )
            except Exception as exc:
                st.error("Semantic search failed.")
                st.exception(exc)


# ============================================================
# ASK MEETING AI / RAG
# ============================================================

elif page == "Ask Career AI":
    st.html(
        """
        <div class="ai-console">
            <div class="ai-console-label">✦ GENERATIVE INTELLIGENCE</div>
            <div class="ai-console-title">Ask Career AI</div>
            <div class="ai-console-text">
                Ask questions across your historical intelligence repository.
                Retrieval happens first, then the answer is generated from the evidence returned by semantic memory.
            </div>
        </div>
        """
    )

    st.html(
        """
        <div class="evidence-banner">
            <strong>Evidence-first AI</strong> · Answers are grounded in retrieved repository context.
            Use the evidence cards below the response to verify where the answer came from.
        </div>
        """
    )

    question = st.text_area(
        "Your intelligence question",
        height=145,
        placeholder=(
            "Who owns the API integration, what is the deadline, and what decision was made?"
        ),
    )

    c1, c2 = st.columns(2)
    with c1:
        top_k = st.slider("Retrieved context chunks", 1, 8, 5)
    with c2:
        meeting_id = st.number_input(
            "Record ID · 0 = all records",
            min_value=0,
            step=1,
            value=0,
        )

    if st.button(
        "✦ Ask Career AI",
        type="primary",
        use_container_width=True,
    ):
        if not question.strip():
            st.warning("Enter a question first.")
        else:
            try:
                with st.spinner("Retrieving evidence and generating an answer..."):
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

                section_title(
                    "AI response",
                    "Generated from the retrieved intelligence context.",
                )

                st.html(
                    f"""
                    <div class="answer-card">
                        <div class="answer-label">✦ CAREER AI RESPONSE</div>
                        <div class="answer-body">{esc(result.get('answer', 'No answer available.'))}</div>
                    </div>
                    """
                )

                display_sources(result.get("sources", []))

            except Exception as exc:
                st.error("Career AI failed.")
                st.exception(exc)


# ============================================================
# ACCURACY TESTING
# ============================================================

elif page == "Accuracy Lab":
    st.html(
        """
        <div class="page-hero">
            <div class="page-kicker">05 · QUALITY ASSURANCE</div>
            <div class="page-title">Accuracy Lab</div>
            <div class="page-description">
                Evaluate Whisper transcription quality against a verified reference
                using Word Error Rate and derived transcription accuracy.
            </div>
            <div class="page-badges">
                <span class="page-badge">Whisper QA</span>
                <span class="page-badge">WER Analysis</span>
                <span class="page-badge gold">Quality Evidence</span>
            </div>
        </div>
        """
    )

    st.html(
        """
        <div class="accuracy-console">
            <div class="accuracy-title">Transcription Quality Console</div>
            <div class="accuracy-text">
                Paste a verified reference and the generated Whisper transcript.
                The lab measures word-level divergence and provides a simple accuracy view.
            </div>
        </div>
        """
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
        "◈ Calculate Transcription Accuracy",
        type="primary",
        use_container_width=True,
    ):
        if not reference.strip() or not hypothesis.strip():
            st.warning("Provide both the reference and Whisper transcripts.")
        else:
            result = calculate_wer(reference, hypothesis)

            section_title(
                "Quality snapshot",
                "Lower WER indicates closer alignment with the verified reference.",
            )

            q1, q2, q3, q4 = st.columns(4)
            with q1:
                st.html(
                    f"""
                    <div class="quality-card">
                        <div class="quality-label">WORD ERROR RATE</div>
                        <div class="quality-value">{result['wer']:.2%}</div>
                        <div class="quality-note">Lower is better</div>
                    </div>
                    """
                )
            with q2:
                st.html(
                    f"""
                    <div class="quality-card">
                        <div class="quality-label">ESTIMATED ACCURACY</div>
                        <div class="quality-value">{result['accuracy']:.2%}</div>
                        <div class="quality-note">Derived from WER</div>
                    </div>
                    """
                )
            with q3:
                st.html(
                    f"""
                    <div class="quality-card">
                        <div class="quality-label">REFERENCE WORDS</div>
                        <div class="quality-value">{result['reference_words']}</div>
                        <div class="quality-note">Verified source</div>
                    </div>
                    """
                )
            with q4:
                st.html(
                    f"""
                    <div class="quality-card">
                        <div class="quality-label">HYPOTHESIS WORDS</div>
                        <div class="quality-value">{result.get('hypothesis_words', '—')}</div>
                        <div class="quality-note">Whisper output</div>
                    </div>
                    """
                )

            section_title("Detailed evaluation", "Raw evaluator output for validation and reporting.")
            st.json(result)

st.html("""
<style>
    /* Final light emerald + gold premium typography / contrast polish */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        font-family: "Aptos", "Segoe UI", "Inter", system-ui, -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #18332D;
    }
    .block-container, .ai-hero, .page-hero, .workspace-card, .repo-card, .answer-card, .search-console, .accuracy-console, .process-input-card {
        font-family: "Aptos", "Segoe UI", "Inter", system-ui, -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    .ai-brand-name, .ai-hero h1, .page-title, .workspace-title, .repo-title, .search-console-title, .accuracy-title, .quality-value, .ai-console-title {
        font-family: "Segoe UI", "Aptos Display", "Inter", system-ui, sans-serif !important;
        color: #18332D !important;
        text-shadow: 0 1px 0 rgba(255,255,255,.55);
    }
    .ai-brand-name span { color: #A77A20 !important; }
    .ai-hero h1 { font-weight: 950 !important; letter-spacing: -.055em !important; }
    .ai-gradient {
        background: linear-gradient(90deg, #0F766E 0%, #A77A20 52%, #18332D 100%) !important;
        -webkit-background-clip: text !important;
        background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        color: transparent !important;
    }
    .ai-hero-description, .page-description, .workspace-text, .repo-summary, .search-console-text, .search-result-text, .accuracy-text, .answer-body {
        color: #42564F !important;
    }
    .ai-chip, .ai-command, .page-badge, .process-mode, .step-detail, .repo-meta, .repo-stat-label, .quality-label {
        color: #52645E !important;
    }
    .ai-sidebar-status { color: #52645E !important; }
    .ai-online { color: #0F766E !important; }
    .ai-console {
        color: #18332D !important;
        background: linear-gradient(135deg, #F1F9F5 0%, #FFFFFF 62%, #E8F5EE 100%) !important;
        border: 1px solid rgba(15,118,110,.12);
        box-shadow: 0 14px 34px rgba(24,51,45,.07);
    }
    .ai-console-title { color: #18332D !important; }
    .ai-console-text { color: #52645E !important; }
    .workspace-card-dark {
        color: #18332D !important;
        background: linear-gradient(135deg,#F1F9F5,#FFFFFF) !important;
        border-color: rgba(15,118,110,.13) !important;
    }
    .workspace-card-dark .workspace-title { color: #18332D !important; }
    .workspace-card-dark .workspace-text { color: #52645E !important; }
    [data-testid="stSidebar"] * { font-family: "Aptos", "Segoe UI", "Inter", system-ui, sans-serif !important; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color: #42564F; }
    .stButton > button { font-family: "Aptos", "Segoe UI", "Inter", system-ui, sans-serif !important; font-weight: 750 !important; letter-spacing: -.01em; }
    .stTextInput input, .stTextArea textarea, .stNumberInput input, [data-baseweb="select"] * { font-family: "Aptos", "Segoe UI", "Inter", system-ui, sans-serif !important; color: #18332D !important; }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder { color: #81928C !important; opacity: 1 !important; }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #168A6A, #0F766E) !important;
        border: 1px solid #0F766E !important;
        color: #FFFFFF !important;
        box-shadow: 0 8px 20px rgba(15,118,110,.16);
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #0F766E, #0B625A) !important;
        box-shadow: 0 10px 24px rgba(15,118,110,.22);
    }
    .stButton > button:not([kind="primary"]) {
        border-color: rgba(181,139,60,.24) !important;
        color: #496159 !important;
        background: #FFFFFF !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        border-color: #B58B3C !important;
        color: #7D6128 !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border-color: transparent !important;
        color: #42564F !important;
        text-align: left;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(35,132,104,.07) !important;
        border-color: rgba(35,132,104,.10) !important;
        color: #0F766E !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: rgba(15,118,110,.45) !important;
        box-shadow: 0 0 0 2px rgba(15,118,110,.08) !important;
    }

    /* ============================================================
       FINAL CONTROL CONTRAST FIX
       ============================================================ */

    /* Primary emerald buttons: always use readable white text/icons. */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-weight: 750 !important;
        text-shadow: none !important;
    }

    .stButton > button[kind="primary"] *,
    .stButton > button[data-testid="baseButton-primary"] * {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    /* Some Streamlit versions put the button label inside a paragraph. */
    .stButton > button[kind="primary"] p,
    .stButton > button[data-testid="baseButton-primary"] p,
    .stButton > button[kind="primary"] span,
    .stButton > button[data-testid="baseButton-primary"] span {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    /* Gold hover/focus treatment while preserving the emerald button. */
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border-color: #B58B3C !important;
        box-shadow: 0 8px 22px rgba(15,118,110,.18) !important;
    }

    /* Native sliders: emerald track/accent instead of Streamlit red. */
    [data-testid="stSlider"] [role="slider"] {
        background: #0F766E !important;
        border-color: #0F766E !important;
    }

    [data-testid="stSlider"] div[data-baseweb="slider"] [data-testid="stSliderThumb"] {
        background: #0F766E !important;
        border-color: #B58B3C !important;
    }

    /* Number-input +/- controls stay readable and premium. */
    [data-testid="stNumberInput"] button {
        color: #0F766E !important;
        background: #F1F9F5 !important;
        border-color: rgba(15,118,110,.12) !important;
    }

    [data-testid="stNumberInput"] button:hover {
        color: #B58B3C !important;
        background: #E7F5EE !important;
    }

    /* Search/AI action labels should never inherit muted text. */
    .stButton > button {
        font-family: "Inter", "Aptos", "Segoe UI", system-ui, sans-serif !important;
        letter-spacing: .01em;
    }

</style>
""")
