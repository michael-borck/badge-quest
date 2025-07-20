# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BadgeQuest is a gamified reflection system for Learning Management Systems that transforms student reflections into achievements through badge progression and micro-credentials. It's built as a Flask application with SQLite database, designed for easy LMS integration.

## Development Commands

```bash
# Testing
pytest                                    # Run all tests with coverage
pytest tests/test_validators.py          # Run specific test file
pytest -k "test_validate_reflection"     # Run specific test
pytest -v                                # Verbose output

# Code Quality
ruff format .                            # Format all Python files
ruff check .                             # Lint code
basedpyright                            # Type checking

# Build & Package
uv build                                 # Build distribution packages
uv run twine upload dist/*              # Upload to PyPI

# Development Server
badgequest init-db                       # Initialize database
badgequest run-server --debug           # Start Flask dev server
badgequest run-server --host 0.0.0.0 --port 5000  # Production-like

# CLI Tools
badgequest extract-lms blackboard --course-id AI101  # Get LMS form
badgequest generate-progress --students students.txt --course AI101  # Progress CSV
badgequest generate-weekly-forms --schedule schedule.json  # Create week forms
badgequest example-config                # Generate example course config
```

## Architecture & Key Design Decisions

### Configuration Loading Flow
The system uses a hierarchical configuration approach:
1. **Environment Variables** (.env file) - loaded via python-dotenv
2. **BADGEQUEST_COURSES_FILE** - if set, loads course configurations from JSON file
3. **Default Courses** - hardcoded in config.py as fallback

Critical: The `_load_courses_from_env()` function in config.py handles external course loading. This was recently added to fix hardcoded path issues.

### Database Design
- **reflections** table uses SHA256 fingerprinting for duplicate detection
- Text is stored base64-encoded (not encrypted) in `text_encrypted` field
- Indexes on student_id, course_id, and fingerprint for performance
- SQLite for development/small deployments, PostgreSQL-ready

### Validation Pipeline
1. **ReflectionValidator** checks word count, readability (Flesch score), sentiment
2. **SimilarityChecker** prevents near-duplicates using Levenshtein distance
3. **ReflectionProcessor** generates unique codes and fingerprints
4. All thresholds are configurable per course

### Badge & Micro-Credential System
- **BadgeSystem**: Week-based progression (1→3→5→7→10→12→14+ weeks)
- **MicroCredentialSystem**: Theme-based achievements requiring multiple submissions
- Both systems are course-configurable with custom progressions

### API Response Pattern
All endpoints return consistent JSON with validation metrics:
```json
{
  "valid": true/false,
  "code": "unique-code",
  "word_count": 150,
  "readability": 65.5,
  "sentiment": 0.3,
  "weeks_completed": 5,
  "current_badge": "🧠 Thinker",
  "micro_credentials_earned": 2
}
```

## Common Development Tasks

### Adding a New Validator
1. Add validation method to `validators.py`
2. Update `validate()` method to include new check
3. Add corresponding test in `test_validators.py`
4. Update API response in `app.py` if needed

### Adding a New Micro-Credential
1. Define in course configuration JSON under `micro_credentials`
2. System automatically picks up from config
3. Test with theme_id in POST /stamp request

### Modifying Badge Levels
1. Update course configuration in BADGEQUEST_COURSES_FILE
2. Or modify DEFAULT_COURSE in config.py for all courses
3. Badge levels support custom emoji and titles

### Testing Configuration Changes
```python
# In tests, use custom config
from badgequest.config import Config
Config.COURSES["test_course"] = {
    "name": "Test Course",
    "min_words": 50,
    "badges": [...]
}
```

## Environment Setup

### Required Environment Variables
```bash
SECRET_KEY=<32-byte-hex>              # For code generation
DATABASE_URL=sqlite:///reflections.db  # Database location
CORS_ORIGINS=https://lms1.edu,https://lms2.edu  # Allowed domains
BADGEQUEST_COURSES_FILE=/path/to/courses.json   # Course configs
```

### Course Configuration Structure
```json
{
  "COURSE_ID": {
    "name": "Course Name",
    "prefix": "CS",
    "min_words": 100,
    "min_readability": 50,
    "min_sentiment": 0,
    "badges": [...],
    "micro_credentials": {
      "credential_id": {
        "name": "Display Name",
        "emoji": "🏆",
        "themes": ["theme1", "theme2"],
        "min_submissions": 2
      }
    }
  }
}
```

## Deployment Considerations

### VPS Deployment
- Use systemd service with Gunicorn
- Caddy/Nginx reverse proxy recommended
- Database file needs www-data permissions
- CORS must match LMS domain exactly

### LMS Integration
- Blackboard: Embed HTML form with JavaScript
- Forms submit cross-domain via CORS
- Weekly CSV exports for grade upload
- Pre-configured forms reduce student errors

## Critical Implementation Details

### Flesch Readability Score
- **Higher = Easier** to read (not harder!)
- Default threshold: 50 (fairly easy)
- Score of 30-50 = difficult, 60-70 = standard
- Non-English speakers may score lower

### Similarity Detection
- Uses Levenshtein ratio (0-1 scale)
- Default threshold: 0.8 (80% similar)
- Compares against all previous submissions
- Exact duplicates caught by fingerprint first

### Code Generation
- HMAC-based with SECRET_KEY
- Includes timestamp for uniqueness
- 12-character alphanumeric codes
- Used for verification and grade tracking

## Recent Changes & Known Issues

### Version 0.3.1
- Fixed BADGEQUEST_COURSES_FILE environment variable loading
- Removed hardcoded /opt/badgequest paths
- Fixed version mismatch between __init__.py and pyproject.toml

### Known Limitations
- No real encryption (base64 only)
- No built-in authentication
- SQLite locks with concurrent writes
- Manual CSV upload for grades

## Testing Strategy

### Unit Tests Cover
- Validation logic (word count, readability, sentiment)
- Badge progression calculations
- Similarity detection algorithms
- Micro-credential awarding logic
- Configuration loading

### Manual Testing Required
- CORS functionality with actual LMS
- JavaScript form behavior
- CSV export formatting
- Database migrations

## File Organization

### Core Application (`src/badgequest/`)
- `app.py` - Flask routes and application factory
- `models.py` - Database operations and schema
- `config.py` - Configuration management
- `validators.py` - Reflection validation logic
- `badges.py` - Badge level calculations
- `microcredentials.py` - Theme-based achievements
- `similarity.py` - Duplicate detection
- `cli.py` - Command-line interface

### Templates (`templates/`)
- `lms/` - LMS integration forms
- `lms/weekly/` - Pre-configured weekly forms
- Form templates include embedded JavaScript

### Key Dependencies
- Flask 3.0+ (web framework)
- TextBlob (sentiment analysis)
- TextStat (readability metrics)
- python-Levenshtein (similarity)
- Click (CLI framework)
- python-dotenv (environment management)