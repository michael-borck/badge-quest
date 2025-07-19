import csv
import sqlite3
from collections import defaultdict
from pathlib import Path

# Configuration
DB_FILE = "reflections.db"
OUTPUT_CSV = "badge_upload.csv"

# Badge Levels (thresholds → badge)
BADGE_LEVELS = [
    (1, "🧪 AI Dabbler"),
    (3, "🥾 AI Explorer"),
    (5, "🧠 AI Thinker"),
    (7, "🛡️ AI Warrior"),
    (10, "🛠️ AI Builder"),
    (12, "🗣️ AI Explainer"),
    (14, "🏆 AI Mastery"),
]


def assign_badge(count):
    """Return the badge that matches the number of completed weeks"""
    for threshold, badge in reversed(BADGE_LEVELS):
        if count >= threshold:
            return badge
    return ""


# Aggregate completed weeks per student
student_weeks = defaultdict(set)

if Path(DB_FILE).exists():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT student_id, week_id FROM reflections")
        for student_id, week_id in c.fetchall():
            student_weeks[student_id].add(week_id)
else:
    print(f"⚠️ Database not found: {DB_FILE}")

# Write badge CSV
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Student ID", "Completed Weeks", "Badge"])
    for student_id, weeks in student_weeks.items():
        count = len(weeks)
        badge = assign_badge(count)
        writer.writerow([student_id, count, badge])

print(f"✅ Badge summary saved to {OUTPUT_CSV}")
