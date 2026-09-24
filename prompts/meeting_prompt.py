def build_meeting_prompt(transcript: str) -> str:
    return f"""
You are a professional meeting intelligence analyst.
Analyze the transcript below and return ONLY valid JSON.

Required schema:
{{
  "summary": "concise executive summary",
  "key_points": ["..."],
  "decisions": ["..."],
  "action_items": [
    {{
      "task": "...",
      "assignee": null,
      "assigned_to": null,
      "deadline": null,
      "priority": null,
      "status": "pending"
    }}
  ],
  "participants": [
    {{"name": "...", "responsibilities": ["..."]}}
  ],
  "deadlines": ["..."],
  "priorities": ["..."]
}}

Rules:
- Do not invent facts.
- Use null when assignee/deadline/priority is not explicit.
- Preserve names and dates exactly where possible.
- Action items must be actionable tasks.
- Decisions are explicit decisions, not suggestions.
- Priority should be High, Medium, Low only when supported.
- Status should be Pending, In Progress, Completed only when supported; otherwise Pending.
- Return no markdown.

TRANSCRIPT:
{transcript}
"""

def build_rag_prompt(question: str, context: str) -> str:
    return f"""
Answer the user's question using ONLY the supplied meeting context.
If the context does not contain the answer, say that the meeting repository
does not contain enough evidence. Do not invent information.

QUESTION:
{question}

MEETING CONTEXT:
{context}
"""
