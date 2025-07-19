# BadgeQuest Configuration Guide

BadgeQuest supports flexible configuration for multiple courses with custom badge systems, validation rules, and themes.

## Environment Variables

Create a `.env` file in your project root:

```bash
# Security
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///reflections.db

# CORS (comma-separated origins)
CORS_ORIGINS=https://blackboard.university.edu,https://canvas.university.edu

# Optional: Custom courses file
BADGEQUEST_COURSES_FILE=/path/to/courses.json
```

## Course Configuration

### Default Configuration

BadgeQuest includes a default configuration that works out of the box:

```json
{
  "default": {
    "name": "Default Course",
    "prefix": "",
    "min_words": 100,
    "min_readability": 50,
    "min_sentiment": 0,
    "max_weeks": 12,
    "badges": [
      {"weeks": 1, "emoji": "🧪", "title": "Dabbler"},
      {"weeks": 3, "emoji": "🥾", "title": "Explorer"},
      {"weeks": 5, "emoji": "🧠", "title": "Thinker"},
      {"weeks": 7, "emoji": "🛡️", "title": "Warrior"},
      {"weeks": 10, "emoji": "🛠️", "title": "Builder"},
      {"weeks": 12, "emoji": "🗣️", "title": "Explainer"},
      {"weeks": 14, "emoji": "🏆", "title": "Mastery"}
    ]
  }
}
```

### Custom Course Configuration

Create a `courses.json` file to define multiple courses:

```json
{
  "AI101": {
    "name": "Introduction to AI",
    "prefix": "AI",
    "min_words": 100,
    "min_readability": 50,
    "min_sentiment": 0,
    "max_weeks": 12,
    "badges": [
      {"weeks": 1, "emoji": "🤖", "title": "Beginner"},
      {"weeks": 3, "emoji": "🧠", "title": "Learner"},
      {"weeks": 5, "emoji": "💡", "title": "Thinker"},
      {"weeks": 7, "emoji": "🔬", "title": "Researcher"},
      {"weeks": 10, "emoji": "🛠️", "title": "Builder"},
      {"weeks": 12, "emoji": "🚀", "title": "Innovator"},
      {"weeks": 14, "emoji": "🏆", "title": "Master"}
    ]
  },
  "PHIL200": {
    "name": "Ethics in Technology",
    "prefix": "Ethics",
    "min_words": 200,
    "min_readability": 45,
    "min_sentiment": -0.2,
    "max_weeks": 14,
    "badges": [
      {"weeks": 1, "emoji": "📚", "title": "Student"},
      {"weeks": 3, "emoji": "🤔", "title": "Questioner"},
      {"weeks": 5, "emoji": "💭", "title": "Philosopher"},
      {"weeks": 7, "emoji": "⚖️", "title": "Ethicist"},
      {"weeks": 10, "emoji": "🎓", "title": "Scholar"},
      {"weeks": 12, "emoji": "🌟", "title": "Sage"},
      {"weeks": 14, "emoji": "🏛️", "title": "Master"}
    ]
  }
}
```

### Configuration Fields

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `name` | string | Display name of the course | Course ID |
| `prefix` | string | Prefix added to badge titles | "" |
| `min_words` | integer | Minimum word count for reflections | 100 |
| `min_readability` | float | Minimum Flesch Reading Ease score | 50 |
| `min_sentiment` | float | Minimum sentiment polarity (-1 to 1) | 0 |
| `max_weeks` | integer | Maximum weeks in the course | 12 |
| `similarity_threshold` | float | Maximum allowed similarity (0-1) | 0.8 |
| `badges` | array | Badge level definitions | See default |

### Badge Definition

Each badge in the `badges` array has:

```json
{
  "weeks": 5,        // Number of weeks required
  "emoji": "🧠",     // Emoji to display
  "title": "Thinker" // Title (prefix will be prepended if set)
}
```

## Using Course Configurations

### 1. In API Endpoints

Pass `course_id` parameter:

```javascript
// In student submission form
fetch("/stamp", {
  method: "POST",
  body: JSON.stringify({
    student_id: "12345",
    week_id: "Week03",
    text: "My reflection...",
    course_id: "AI101"  // Specify course
  })
});

// In progress endpoint
fetch("/progress/12345?course=AI101&format=json");
```

### 2. In CLI Commands

```bash
# Generate progress for specific course
badgequest generate-progress \
  --students students.txt \
  --course AI101 \
  --output ai101_badges.csv

# Extract form for specific course
badgequest extract-lms blackboard \
  --course-id PHIL200 \
  --output philosophy_form.html
```

### 3. In LMS Forms

Update the hidden course field in your HTML form:

```html
<input id="course_id" type="hidden" value="AI101" />
```

## Validation Rules

### Similarity Checking

BadgeQuest now includes intelligent similarity detection to prevent students from reusing previous reflections with minor changes:

- **Exact Duplicate Check**: First checks for identical submissions (copy-paste)
- **Similarity Analysis**: Uses Levenshtein distance to calculate text similarity
- **Configurable Threshold**: Default is 80% (0.8) - reflections must be at least 20% different
- **Per-Student Comparison**: Only compares against the student's own previous submissions

#### How Similarity Works:
- 100% (1.0) = Identical text
- 80% (0.8) = Default threshold - minor changes like fixing typos
- 60% (0.6) = Significant overlap but some new content
- 40% (0.4) = Some similar structure but mostly new content
- 0% (0.0) = Completely different

#### Template Use:
The 80% threshold allows students to:
- Use a consistent reflection structure
- Keep helpful formatting patterns
- Reuse opening/closing phrases
- But requires ~20% new content each week

### Readability Score

The Flesch Reading Ease score ranges from 0-100:
- 90-100: Very easy to read (5th grade)
- 80-89: Easy to read (6th grade)
- 70-79: Fairly easy (7th grade)
- 60-69: Standard (8th-9th grade)
- 50-59: Fairly difficult (10th-12th grade)
- 30-49: Difficult (College)
- 0-29: Very difficult (Graduate)

### Sentiment Analysis

Sentiment polarity ranges from -1 to 1:
- -1: Most negative
- 0: Neutral
- 1: Most positive

Set `min_sentiment` to:
- `0` for neutral or positive reflections
- `-0.2` to allow slightly negative reflections
- `-1` to disable sentiment checking

## Advanced Configuration

### Loading from File

```bash
# Create configuration file
badgequest example-config

# Edit courses_example.json
nano courses_example.json

# Load configuration
badgequest load-config courses_example.json
```

### Environment-Based Configuration

Set the `BADGEQUEST_COURSES_FILE` environment variable:

```bash
export BADGEQUEST_COURSES_FILE=/opt/badgequest/courses.json
```

### Dynamic Configuration

For advanced use cases, you can modify `config.py` to load configurations from:
- Database
- External API
- Configuration management system

## Examples

### Gaming-Themed Course

```json
{
  "GAME101": {
    "name": "Game Design Fundamentals",
    "prefix": "Game",
    "badges": [
      {"weeks": 1, "emoji": "🎮", "title": "Player"},
      {"weeks": 3, "emoji": "🕹️", "title": "Gamer"},
      {"weeks": 5, "emoji": "🎯", "title": "Strategist"},
      {"weeks": 7, "emoji": "🏗️", "title": "Designer"},
      {"weeks": 10, "emoji": "🎨", "title": "Creator"},
      {"weeks": 12, "emoji": "🚀", "title": "Developer"},
      {"weeks": 14, "emoji": "👑", "title": "Master"}
    ]
  }
}
```

### Research-Focused Course

```json
{
  "RES500": {
    "name": "Research Methods",
    "prefix": "",
    "min_words": 300,
    "min_readability": 40,
    "badges": [
      {"weeks": 1, "emoji": "📝", "title": "Note Taker"},
      {"weeks": 3, "emoji": "🔍", "title": "Observer"},
      {"weeks": 5, "emoji": "📊", "title": "Analyst"},
      {"weeks": 7, "emoji": "🔬", "title": "Researcher"},
      {"weeks": 10, "emoji": "📈", "title": "Data Scientist"},
      {"weeks": 12, "emoji": "🎓", "title": "Scholar"},
      {"weeks": 14, "emoji": "🏅", "title": "Expert"}
    ]
  }
}
```

## Best Practices

1. **Consistent Theming**: Keep badge emojis and titles thematically consistent
2. **Progressive Difficulty**: Consider increasing requirements for advanced courses
3. **Clear Progression**: Ensure badge titles show clear progression
4. **Student Communication**: Document badge requirements in course syllabus
5. **Regular Reviews**: Adjust validation rules based on student feedback