from schemas.meeting_schema import ActionItem, Participant, MeetingIntelligence

def _dump(x):
    if hasattr(x, "model_dump"): return x.model_dump()
    if hasattr(x, "dict"): return x.dict()
    return x if isinstance(x,dict) else {"task":str(x)}

def clean_action_items(items):
    out=[]; seen=set()
    for item in items or []:
        d=_dump(item); task=str(d.get("task","")).strip()
        if not task or task.lower() in seen: continue
        seen.add(task.lower())
        assignee=d.get("assigned_to") or d.get("assignee")
        out.append({"task":task,"assignee":assignee,"assigned_to":assignee,"deadline":d.get("deadline"),"priority":d.get("priority"),"status":d.get("status") or "Pending"})
    return out

def clean_participants(items):
    out=[]; seen=set()
    for item in items or []:
        d=_dump(item); name=str(d.get("name","")).strip()
        if not name or name.lower() in seen: continue
        seen.add(name.lower())
        r=d.get("responsibilities") or []
        out.append({"name":name,"responsibilities":r if isinstance(r,list) else [str(r)]})
    return out

class MeetingService:
    clean_action_items = staticmethod(clean_action_items)
    clean_participants = staticmethod(clean_participants)
