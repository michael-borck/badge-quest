# BadgeQuest 🏆

> Collect, learn, repeat.

BadgeQuest is a gamified reflection system designed for Learning Management Systems (LMS). It transforms student reflections into meaningful achievements through an engaging badge progression system.

## Features

- **Weekly Reflection Tracking**: Students submit reflections that are validated for quality
- **Smart Validation**: Checks word count, readability, sentiment, and uniqueness
- **Similarity Detection**: Prevents resubmission of previous reflections with minor changes (80% threshold)
- **Badge Progression**: Earn badges from "Dabbler" to "Mastery" based on consistent participation
- **LMS Integration**: Ready-to-use HTML forms for Blackboard (Canvas and Moodle coming soon)
- **Instructor Tools**: Generate progress reports for easy grade center uploads
- **Privacy-First**: Only stores anonymized data with hashed reflections
- **Configurable**: Support multiple courses with custom badge themes

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

## API Endpoints

- `POST /stamp` - Submit a reflection
- `GET /progress/<student_id>` - View student progress
- `GET /verify/<code>` - Verify a reflection code

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