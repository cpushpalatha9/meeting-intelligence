from collections import Counter
from datetime import datetime

def meeting_metrics(meeting):
    transcript = meeting.get('transcript','') or ''
    actions = meeting.get('action_items',[]) or []
    participants = meeting.get('participants',[]) or []
    decisions = meeting.get('decisions',[]) or []
    words = len(transcript.split())
    statuses = Counter((a.get('status') or 'Unknown') if isinstance(a,dict) else 'Unknown' for a in actions)
    priorities = Counter((a.get('priority') or 'Unspecified') if isinstance(a,dict) else 'Unspecified' for a in actions)
    return {'word_count':words,'action_count':len(actions),'participant_count':len(participants),'decision_count':len(decisions),'status_breakdown':dict(statuses),'priority_breakdown':dict(priorities)}
