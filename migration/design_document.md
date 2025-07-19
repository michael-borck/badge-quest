# 🧠 AI Reflection Badge System

**System Design Document**

---

## 1. 🎯 Purpose & Overview

This system supports a habit-forming, AI-enhanced reflection workflow for students, designed to integrate seamlessly into Blackboard. It provides:

* Validation of weekly reflections (word count, readability, sentiment)
* Duplicate detection (reuse within or between students)
* Unique verifiable codes for each reflection ("passport stamps")
* Badge progression based on cumulative weekly submissions
* Immediate feedback and delayed badge updates to Blackboard Grade Centre

This approach balances automation, engagement, and privacy.

---

## 2. 🧰 System Components

| Component                | Description                                                                                                                |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| **Blackboard Frontend**  | HTML+JS form embedded in Blackboard to submit reflections and get feedback (via `/stamp`).                                 |
| **Flask Backend**        | Python server that handles validation, code generation, and progress tracking.                                             |
| **SQLite Database**      | Stores hashed reflections, associated student IDs, and week IDs. Enables duplicate detection.                              |
| **Badge CSV Script**     | Standalone script (`download_badges.py`) that collects badge progress from the API and generates a Grade Centre–ready CSV. |
| **Badge Rubric Display** | Markdown/HTML accordion listing emoji-based badge levels. Embedded in LMS.                                                 |
| **Progress Endpoint**    | Lets students view their current badge status based on submissions.                                                        |

---

## 3. 🔌 Flask API Endpoints

| Endpoint                                | Method | Description                                                                                                                                     |
| --------------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `/stamp`                                | `POST` | **Main submission endpoint.** Accepts `student_id`, `week_id`, and `text`. Validates and stores reflection. Returns feedback and current badge. |
| `/progress/<student_id>`                | `GET`  | **Progress endpoint.** Returns number of weeks completed and badge level. Used for verification and CSV generation.                             |
| `/badgeboard/<student_id>` *(optional)* | `GET`  | **Dashboard view.** (Optional HTML page showing summary of progress and badge level.)                                                           |
| `/admin/echo` *(optional)*              | `GET`  | **Basic sanity check.** Returns a JSON response to verify that the API is online.                                                               |

---

## 4. ♻️ Workflow Overview

### Submission Cycle (Student)

1. Student opens embedded form in Blackboard.
2. Enters:

   * `Student ID`
   * `Week ID` (e.g. "Week03")
   * Reflection `Text`
3. Form sends data to `/stamp`
4. Server checks:

   * Word Count >= 100
   * Flesch Reading Ease >= 50
   * Sentiment Analysis (polarity > 0)
   * Reflection uniqueness (hash comparison)
5. If valid:

   * Code is generated (base64 or hash)
   * Week stored for that student
   * Badge level determined and returned
6. Response includes:

   * Code (string)
   * Readability, sentiment, word count
   * Weeks completed
   * Current badge level

### Weekly Grade Centre Update (Instructor)

1. Instructor prepares `student_ids.txt`
2. Runs `download_badges.py`

   * Hits `/progress/<student_id>` for each
   * Retrieves badge level and week count
   * Generates `badge_upload.csv`
3. Uploads `badge_upload.csv` to Grade Centre
4. Students see emoji badges in "My Grades"

---

## 5. 🛡️ Privacy & Security

* Only stores anonymised data: student ID and hashed reflection text
* No names, emails, or actual text retained
* No third-party services used (everything processed server-side)
* Public endpoints (`/progress`) show **only** per-user data
* Code generation uses salt to prevent reverse lookup

---

## 6. 📊 Badge Levels & Rubric

| Weeks | Badge | Title        |
| ----- | ----- | ------------ |
| 1     | 🧪    | AI Dabbler   |
| 3     | 🪶    | AI Explorer  |
| 5     | 🧠    | AI Thinker   |
| 7     | 🛡️   | AI Warrior   |
| 10    | 🛠️   | AI Builder   |
| 12    | 🗣️   | AI Explainer |
| 14+   | 🏆    | AI Mastery   |

These badges are shown after submission, and updated weekly in Blackboard.

---

## 7. 🔧 Deployment Notes

| Resource         | Recommendation                                                                 |
| ---------------- | ------------------------------------------------------------------------------ |
| Flask App        | VPS-hosted, HTTPS secured                                                      |
| Blackboard       | Embed HTML form using "Item" or "Module Page" content blocks                   |
| CSV Upload       | Use Grade Centre > Work Offline > Upload to import `badge_upload.csv` weekly   |
| Student Feedback | Delivered immediately via `/stamp` response; badge shown in "My Grades" weekly |

---

## 8. 🚀 Future Extensions

| Feature                 | Status                                                                     |
| ----------------------- | -------------------------------------------------------------------------- |
| `/badgeboard/<id>` page | Optional for individual badge summary views                                |
| Dashboard analytics     | Possible addition for staff insights                                       |
| Auto Grade Centre sync  | LTI integration or Blackboard API option (currently manual upload)         |
| AI-generated feedback   | Future enhancement using GPT to reflect on writing style or critical depth |

---
