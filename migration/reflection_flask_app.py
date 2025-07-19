import hashlib
import sqlite3
import time
from datetime import datetime

import textstat
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
from textblob import TextBlob

app = Flask(__name__)
CORS(app)

DB_FILE = "reflections.db"
SECRET = "my_secret_salt"

BADGE_LEVELS = [
    (1, "🧪 AI Dabbler"),
    (3, "🥾 AI Explorer"),
    (5, "🧠 AI Thinker"),
    (7, "🛡️ AI Warrior"),
    (10, "🛠️ AI Builder"),
    (12, "🗣️ AI Explainer"),
    (14, "🏆 AI Mastery"),
]


def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            fingerprint TEXT NOT NULL,
            week_id TEXT NOT NULL,
            code TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        """)
        conn.commit()


def get_fingerprint(text):
    return hashlib.sha256(text.strip().lower().encode()).hexdigest()


def generate_code(text, week_id, secret=SECRET):
    timestamp = str(int(time.time()))
    raw = text + week_id + secret + timestamp
    return hashlib.sha256(raw.encode()).hexdigest()[:10]


def assign_badge(count):
    for threshold, badge in reversed(BADGE_LEVELS):
        if count >= threshold:
            return badge
    return "❌ No Badge Yet"


@app.route("/stamp", methods=["POST"])
def stamp():
    data = request.get_json()
    text = data.get("text", "").strip()
    week_id = data.get("week_id", "").strip()
    student_id = data.get("student_id", "").strip()

    if not text or not week_id or not student_id:
        return jsonify({"error": "Missing text, week_id, or student_id"}), 400

    word_count = len(text.split())
    readability = textstat.flesch_reading_ease(text)
    sentiment = TextBlob(text).sentiment.polarity

    if word_count < 100 or readability < 50:
        return jsonify(
            {
                "valid": False,
                "reason": "Minimum criteria not met",
                "word_count": word_count,
                "readability": readability,
                "sentiment": sentiment,
            }
        )

    fingerprint = get_fingerprint(text)

    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM reflections WHERE fingerprint = ?", (fingerprint,))
        if c.fetchone()[0] > 0:
            return jsonify(
                {
                    "valid": False,
                    "reason": "Duplicate text submission detected",
                    "word_count": word_count,
                    "readability": readability,
                    "sentiment": sentiment,
                }
            )

        code = generate_code(text, week_id)
        c.execute(
            "INSERT INTO reflections (student_id, fingerprint, week_id, code, timestamp) VALUES (?, ?, ?, ?, ?)",
            (student_id, fingerprint, week_id, code, datetime.utcnow().isoformat()),
        )
        conn.commit()

        # Count total reflections and assign badge
        c.execute("SELECT DISTINCT week_id FROM reflections WHERE student_id = ?", (student_id,))
        weeks = [row[0] for row in c.fetchall()]
        weeks_completed = len(weeks)
        badge = assign_badge(weeks_completed)

    return jsonify(
        {
            "valid": True,
            "code": code,
            "word_count": word_count,
            "readability": readability,
            "sentiment": sentiment,
            "weeks_completed": weeks_completed,
            "current_badge": badge,
            "note": "📌 This badge status will be uploaded to Grade Centre weekly.",
        }
    )


@app.route("/verify/<code>")
def verify(code):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT student_id, week_id, timestamp FROM reflections WHERE code = ?", (code,))
        row = c.fetchone()
        if row:
            return f"✅ Code {code} is valid for {row[1]} by {row[0]} (submitted {row[2]})"
        else:
            return f"❌ Code {code} not found or invalid."


@app.route("/progress/<student_id>")
def progress(student_id):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT DISTINCT week_id FROM reflections WHERE student_id = ?", (student_id,))
        weeks = [row[0] for row in c.fetchall()]
        count = len(weeks)
        badge = assign_badge(count)

    html = f"""
    <html><body style="font-family: Arial; max-width: 600px; margin: auto;">
    <h2>🎓 AI Reflection Journey</h2>
    <p><strong>Student ID:</strong> {student_id}</p>
    <p><strong>Weeks Completed:</strong> {count}</p>
    <p><strong>Current Badge:</strong> {badge}</p>
    <ul>
        {"".join(f"<li>{w}</li>" for w in sorted(weeks))}
    </ul>
    </body></html>
    """
    return render_template_string(html)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
