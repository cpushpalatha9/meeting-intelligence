import uuid

from services.auth_service import register_user, authenticate
from services.database_service import init_database, save_meeting, get_meeting
from services.export_service import meeting_csv, meeting_pdf


def test_auth_and_owner_access():
    init_database()

    email = f"qa_{uuid.uuid4().hex[:8]}@example.com"

    ok, message = register_user(
        "QA User",
        email,
        "password123"
    )

    assert ok, message

    user = authenticate(email, "password123")

    assert user is not None

    meeting_id = save_meeting(
        "QA Meeting",
        "test transcript",
        "test summary",
        owner_id=user["id"]
    )

    meeting = get_meeting(meeting_id, user["id"])

    assert meeting is not None
    assert meeting["title"] == "QA Meeting"


def test_exports():
    meeting = {
        "id": 1,
        "title": "QA",
        "created_at": "today",
        "language": "en",
        "summary": "summary",
        "key_points": [],
        "decisions": [],
        "action_items": [],
        "participants": [],
        "deadlines": [],
        "priorities": []
    }

    assert meeting_csv(meeting)
    assert meeting_pdf(meeting).startswith(b"%PDF")