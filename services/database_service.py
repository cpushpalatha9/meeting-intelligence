import json
import sqlite3
import os

from datetime import datetime


DATABASE_DIR = "database"

DATABASE_PATH = os.path.join(
    DATABASE_DIR,
    "meetings.db"
)


def get_connection():

    # Create database folder if it doesn't exist
    os.makedirs(
        DATABASE_DIR,
        exist_ok=True
    )

    return sqlite3.connect(
        DATABASE_PATH
    )


def init_database():

    # Make sure database directory exists
    os.makedirs(
        DATABASE_DIR,
        exist_ok=True
    )

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS meetings (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            transcript TEXT NOT NULL,

            summary TEXT,

            key_points TEXT,

            decisions TEXT,

            action_items TEXT,

            participants TEXT,

            created_at TEXT
        )
        """
    )

    connection.commit()

    connection.close()


def save_meeting(
    title,
    transcript,
    result,
    participants,
    action_items
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO meetings (
            title,
            transcript,
            summary,
            key_points,
            decisions,
            action_items,
            participants,
            created_at
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,

        (
            title,
            transcript,
            result.summary,
            json.dumps(
                result.key_points
            ),
            json.dumps(
                result.decisions
            ),
            json.dumps(
                action_items
            ),
            json.dumps(
                participants
            ),
            datetime.now().isoformat()
        )
    )

    connection.commit()

    meeting_id = cursor.lastrowid

    connection.close()

    return meeting_id


def get_all_meetings():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            title,
            summary,
            created_at

        FROM meetings

        ORDER BY id DESC
        """
    )

    meetings = cursor.fetchall()

    connection.close()

    return meetings


def get_meeting(meeting_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *

        FROM meetings

        WHERE id = ?
        """,

        (meeting_id,)
    )

    meeting = cursor.fetchone()

    connection.close()

    return meeting