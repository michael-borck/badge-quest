import csv
from collections import defaultdict

# 🎖️ Define badge levels based on number of completed weeks
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
    """Assign the correct badge based on number of completed reflections"""
    for threshold, badge in reversed(BADGE_LEVELS):
        if count >= threshold:
            return badge
    return ""


# 📂 Input file: CSV log of validated reflections (1 row per submission)
INPUT_FILE = "reflections_log.csv"
OUTPUT_FILE = "student_badges.csv"

# 🧮 Count unique weeks per student
student_weeks = defaultdict(set)

with open(INPUT_FILE, newline="", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        student = row["student_id"]
        week = row["week_id"]
        student_weeks[student].add(week)

# 💾 Write output with badges
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as outfile:
    fieldnames = ["student_id", "completed_weeks", "badge"]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    for student, weeks in student_weeks.items():
        count = len(weeks)
        badge = assign_badge(count)
        writer.writerow({"student_id": student, "completed_weeks": count, "badge": badge})

print(f"Badge summary saved to {OUTPUT_FILE}")
