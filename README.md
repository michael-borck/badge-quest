# BadgeQuest 🏆

<!-- BADGES:START -->
[![edtech](https://img.shields.io/badge/-edtech-4caf50?style=flat-square)](https://github.com/topics/edtech) [![badges](https://img.shields.io/badge/-badges-blue?style=flat-square)](https://github.com/topics/badges) [![education](https://img.shields.io/badge/-education-blue?style=flat-square)](https://github.com/topics/education) [![flask](https://img.shields.io/badge/-flask-000000?style=flat-square)](https://github.com/topics/flask) [![gamification](https://img.shields.io/badge/-gamification-blue?style=flat-square)](https://github.com/topics/gamification) [![learning-analytics](https://img.shields.io/badge/-learning--analytics-blue?style=flat-square)](https://github.com/topics/learning-analytics) [![lms](https://img.shields.io/badge/-lms-blue?style=flat-square)](https://github.com/topics/lms) [![python](https://img.shields.io/badge/-python-3776ab?style=flat-square)](https://github.com/topics/python) [![reflection](https://img.shields.io/badge/-reflection-blue?style=flat-square)](https://github.com/topics/reflection) [![web-app](https://img.shields.io/badge/-web--app-blue?style=flat-square)](https://github.com/topics/web-app)
<!-- BADGES:END -->

> Collect, learn, repeat.

BadgeQuest is a gamified reflection system designed for Learning Management Systems (LMS). It transforms student reflections into meaningful achievements through an engaging badge progression system.

## Features

- **Weekly Reflection Tracking**: Students submit reflections that are validated for quality
- **Smart Validation**: Checks word count, readability, sentiment, and uniqueness
- **Similarity Detection**: Prevents resubmission of previous reflections with minor changes (80% threshold)
- **Badge Progression**: Earn badges from "Dabbler" to "Mastery" based on consistent participation
- **Micro-Credentials**: Theme-based achievements for focused reflection topics (e.g., AI Ethics Explorer, Innovation Champion)
- **LMS Integration**: Ready-to-use HTML forms for Blackboard (Canvas and Moodle coming soon)
- **Instructor Tools**: Generate progress reports for easy grade center uploads
- **Privacy-First**: Only stores anonymized data with hashed reflections
- **Configurable**: Support multiple courses with custom badge themes and micro-credentials

## Quick Start

### Installation

```bash
# Install from PyPI
pip install badge-quest

# Or with uv (recommended)
uv pip install badge-quest
```

### Running the Server

```bash
# Initialize the database
badgequest init-db

# Start the Flask server
badgequest run-server --port 5000
```

### For Instructors

1. Extract the LMS form template:
```bash
badgequest extract-lms blackboard --output form.html
```

2. Generate progress reports:
```bash
badgequest generate-progress --students students.txt --course AI101 --output badges.csv
```

## Configuration

BadgeQuest supports course-specific configurations through environment variables:

```bash
# .env file
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///reflections.db
CORS_ORIGINS=https://your-lms.edu
```

## Badge Levels

The default badge progression:

| Weeks | Badge | Title |
|-------|-------|-------|
| 1 | 🧪 | Dabbler |
| 3 | 🥾 | Explorer |
| 5 | 🧠 | Thinker |
| 7 | 🛡️ | Warrior |
| 10 | 🛠️ | Builder |
| 12 | 🗣️ | Explainer |
| 14+ | 🏆 | Mastery |

### Micro-Credentials

Students can earn theme-based micro-credentials by submitting reflections with specific themes. Example configuration:

```python
"micro_credentials": {
    "ethics_explorer": {
        "name": "AI Ethics Explorer",
        "emoji": "⚖️",
        "description": "Demonstrated strong ethical analysis in AI reflections",
        "themes": ["ethics", "responsibility"],
        "min_submissions": 2
    }
}
```

## API Endpoints

- `POST /stamp` - Submit a reflection (with optional theme_id)
- `GET /progress/<student_id>` - View student progress including micro-credentials
- `GET /verify/<code>` - Verify a reflection code
- `GET /api/micro-credentials/<student_id>` - Get detailed micro-credentials information
- `POST /api/progress/bulk` - Get progress for multiple students including micro-credentials

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/badgequest.git
cd badgequest

# Install with development dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Format code
ruff format .

# Type check
basedpyright
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and feature requests, please use the [GitHub issue tracker](https://github.com/yourusername/badgequest/issues).