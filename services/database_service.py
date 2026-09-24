import json, sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "database"
DB_DIR.mkdir(exist_ok=True)
DATABASE_PATH = DB_DIR / "meetings.db"

def get_connection():
    c=sqlite3.connect(str(DATABASE_PATH), check_same_thread=False)
    c.row_factory=sqlite3.Row
    return c

def init_database():
    with get_connection() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS meetings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        transcript TEXT,
        summary TEXT,
        key_points TEXT,
        decisions TEXT,
        action_items TEXT,
        participants TEXT,
        deadlines TEXT,
        priorities TEXT,
        language TEXT,
        sentiment TEXT,
        processed_text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

def _j(v): return json.dumps(v if v is not None else [], ensure_ascii=False)
def _u(v):
    try: return json.loads(v) if v else []
    except: return []

def save_meeting(title, transcript, summary, key_points=None, decisions=None, action_items=None, participants=None, deadlines=None, priorities=None, language="unknown", sentiment=None, processed_text=""):
    init_database()
    with get_connection() as c:
        cur=c.execute("""INSERT INTO meetings(title,transcript,summary,key_points,decisions,action_items,participants,deadlines,priorities,language,sentiment,processed_text)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",(title,transcript,summary,_j(key_points),_j(decisions),_j(action_items),_j(participants),_j(deadlines),_j(priorities),language,_j(sentiment or {}),processed_text))
        return cur.lastrowid

def _row(r):
    if not r:return None
    return {"id":r["id"],"title":r["title"],"transcript":r["transcript"] or "","summary":r["summary"] or "",
    "key_points":_u(r["key_points"]),"decisions":_u(r["decisions"]),"action_items":_u(r["action_items"]),
    "participants":_u(r["participants"]),"deadlines":_u(r["deadlines"]),"priorities":_u(r["priorities"]),
    "language":r["language"],"sentiment":_u(r["sentiment"]),"processed_text":r["processed_text"] or "","created_at":r["created_at"]}

def get_all_meetings():
    init_database()
    with get_connection() as c: return [_row(r) for r in c.execute("SELECT * FROM meetings ORDER BY id DESC").fetchall()]

def get_meeting(meeting_id):
    init_database()
    with get_connection() as c: return _row(c.execute("SELECT * FROM meetings WHERE id=?",(meeting_id,)).fetchone())
