"""Database models and operations for BadgeQuest."""

import hashlib
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime

from .config import Config


class Database:
    """Database connection and operations manager."""

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or Config().DATABASE_PATH
        self.init_db()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self) -> None:
        """Initialize the database schema."""
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("""
            CREATE TABLE IF NOT EXISTS reflections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                course_id TEXT NOT NULL DEFAULT 'default',
                fingerprint TEXT NOT NULL,
                week_id TEXT NOT NULL,
                code TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                word_count INTEGER,
                readability REAL,
                sentiment REAL,
                text_encrypted TEXT,
                theme_id TEXT
            )
            """)

            # Create indexes for better performance
            c.execute("""
            CREATE INDEX IF NOT EXISTS idx_student_course
            ON reflections(student_id, course_id)
            """)
            c.execute("""
            CREATE INDEX IF NOT EXISTS idx_fingerprint
            ON reflections(fingerprint)
            """)
            c.execute("""
            CREATE INDEX IF NOT EXISTS idx_code
            ON reflections(code)
            """)

            # Create micro-credentials table
            c.execute("""
            CREATE TABLE IF NOT EXISTS student_micro_credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                course_id TEXT NOT NULL,
                credential_id TEXT NOT NULL,
                earned_date TEXT NOT NULL,
                weeks_completed TEXT NOT NULL,
                UNIQUE(student_id, course_id, credential_id)
            )
            """)

            c.execute("""
            CREATE INDEX IF NOT EXISTS idx_student_credentials
            ON student_micro_credentials(student_id, course_id)
            """)

            conn.commit()

    def add_reflection(
        self,
        student_id: str,
        course_id: str,
        fingerprint: str,
        week_id: str,
        code: str,
        word_count: int,
        readability: float,
        sentiment: float,
        text_encrypted: str | None = None,
        theme_id: str | None = None,
    ) -> None:
        """Add a new reflection to the database."""
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO reflections (
                    student_id, course_id, fingerprint, week_id,
                    code, timestamp, word_count, readability, sentiment, text_encrypted, theme_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    student_id,
                    course_id,
                    fingerprint,
                    week_id,
                    code,
                    datetime.utcnow().isoformat(),
                    word_count,
                    readability,
                    sentiment,
                    text_encrypted,
                    theme_id,
                ),
            )
            conn.commit()

    def check_duplicate(self, fingerprint: str) -> bool:
        """Check if a reflection with the given fingerprint exists."""
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM reflections WHERE fingerprint = ?", (fingerprint,))
            return c.fetchone()[0] > 0

    def get_student_weeks(self, student_id: str, course_id: str) -> list[str]:
        """Get list of completed weeks for a student in a course."""
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """
                SELECT DISTINCT week_id
                FROM reflections
                WHERE student_id = ? AND course_id = ?
                ORDER BY week_id
            """,
                (student_id, course_id),
            )
            return [row[0] for row in c.fetchall()]

    def verify_code(self, code: str) -> dict | None:
        """Verify a reflection code and return its details."""
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """
                SELECT student_id, course_id, week_id, timestamp
                FROM reflections
                WHERE code = ?
            """,
                (code,),
            )
            row = c.fetchone()
            if row:
                return dict(row)
            return None

    def get_all_students_progress(self, course_id: str) -> dict[str, list[str]]:
        """Get progress for all students in a course."""
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """
                SELECT student_id, week_id
                FROM reflections
                WHERE course_id = ?
                ORDER BY student_id, week_id
            """,
                (course_id,),
            )

            progress = {}
            for row in c.fetchall():
                student_id = row[0]
                if student_id not in progress:
                    progress[student_id] = []
                if row[1] not in progress[student_id]:
                    progress[student_id].append(row[1])

            return progress

    def get_student_reflections_encrypted(
        self, student_id: str, course_id: str
    ) -> list[tuple[str, str]]:
        """Get encrypted reflections for a student in a course.

        Returns:
            List of tuples (week_id, encrypted_text)
        """
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """
                SELECT week_id, text_encrypted
                FROM reflections
                WHERE student_id = ? AND course_id = ? AND text_encrypted IS NOT NULL
                ORDER BY timestamp DESC
            """,
                (student_id, course_id),
            )
            return [(row[0], row[1]) for row in c.fetchall()]

    def add_micro_credential(
        self, student_id: str, course_id: str, credential_id: str, weeks_completed: list[str]
    ) -> bool:
        """Award a micro-credential to a student.

        Returns:
            True if newly awarded, False if already exists
        """
        with self.get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    """
                    INSERT INTO student_micro_credentials
                    (student_id, course_id, credential_id, earned_date, weeks_completed)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        student_id,
                        course_id,
                        credential_id,
                        datetime.utcnow().isoformat(),
                        ",".join(weeks_completed),
                    ),
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                # Already has this credential
                return False

    def get_student_micro_credentials(self, student_id: str, course_id: str) -> list[dict]:
        """Get all micro-credentials earned by a student in a course."""
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """
                SELECT credential_id, earned_date, weeks_completed
                FROM student_micro_credentials
                WHERE student_id = ? AND course_id = ?
                ORDER BY earned_date
                """,
                (student_id, course_id),
            )
            return [
                {
                    "credential_id": row[0],
                    "earned_date": row[1],
                    "weeks_completed": row[2].split(",") if row[2] else [],
                }
                for row in c.fetchall()
            ]

    def get_student_theme_weeks(self, student_id: str, course_id: str, theme_id: str) -> list[str]:
        """Get weeks where student completed reflections for a specific theme."""
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """
                SELECT DISTINCT week_id
                FROM reflections
                WHERE student_id = ? AND course_id = ? AND theme_id = ?
                ORDER BY week_id
                """,
                (student_id, course_id, theme_id),
            )
            return [row[0] for row in c.fetchall()]


class ReflectionProcessor:
    """Handles reflection processing and validation."""

    def __init__(self, secret: str | None = None):
        self.secret = secret or Config.SECRET_KEY

    @staticmethod
    def get_fingerprint(text: str) -> str:
        """Generate a fingerprint for the reflection text."""
        return hashlib.sha256(text.strip().lower().encode()).hexdigest()

    def generate_code(self, text: str, week_id: str, student_id: str) -> str:
        """Generate a unique code for the reflection."""
        timestamp = str(int(time.time()))
        raw = f"{text}{week_id}{student_id}{self.secret}{timestamp}"
        return hashlib.sha256(raw.encode()).hexdigest()[:10]
