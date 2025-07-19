import csv

import requests

# Configuration
INPUT_FILE = "student_ids.txt"  # Each line should have one student ID
OUTPUT_FILE = "badge_upload.csv"  # Output file to upload into Blackboard
FLASK_URL = "http://localhost:5000"  # Your Flask app base URL

# Step 1: Read student IDs from file
with open(INPUT_FILE, encoding="utf-8") as f:
    student_ids = [line.strip() for line in f if line.strip()]

# Step 2: Query each student's progress
rows = []
for sid in student_ids:
    try:
        response = requests.get(f"{FLASK_URL}/progress/{sid}")
        if response.status_code == 200:
            html = response.text
            # Naive HTML parsing (you could improve this with BeautifulSoup if needed)
            completed_line = next(
                (line for line in html.splitlines() if "Weeks Completed:" in line), ""
            )
            badge_line = next((line for line in html.splitlines() if "Current Badge:" in line), "")
            count = "".join(filter(str.isdigit, completed_line))
            badge = badge_line.split(":")[-1].strip("</p> ") if badge_line else ""
            rows.append((sid, count, badge))
        else:
            rows.append((sid, "0", "❌ Not Found"))
    except Exception:
        rows.append((sid, "0", "❌ Error"))

# Step 3: Write to a Blackboard-compatible CSV
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Student ID", "Completed Weeks", "Badge"])
    writer.writerows(rows)

print(f"✅ Badge summary written to {OUTPUT_FILE}")
