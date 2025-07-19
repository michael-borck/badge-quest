# BadgeQuest Documentation

Welcome to the BadgeQuest documentation! BadgeQuest is a gamified reflection system that transforms student reflections into meaningful achievements.

## 📚 Documentation Overview

- **[Deployment Guide](deployment.md)** - Step-by-step instructions for deploying BadgeQuest to production
- **[Configuration Guide](configuration.md)** - How to configure courses, badges, and validation rules
- **[API Reference](api.md)** - Complete API endpoint documentation
- **[LMS Integration](lms-integration.md)** - Guides for integrating with Blackboard, Canvas, and Moodle

## 🚀 Quick Links

- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Course Setup](#course-setup)
- [Troubleshooting](#troubleshooting)

## Installation

```bash
# Using pip
pip install badgequest

# Using uv (recommended)
uv pip install badgequest
```

## Basic Usage

### 1. Initialize Database
```bash
badgequest init-db
```

### 2. Start Server
```bash
badgequest run-server --port 5000
```

### 3. Extract LMS Templates
```bash
badgequest extract-lms blackboard --output form.html
```

### 4. Generate Progress Reports
```bash
badgequest generate-progress --students students.txt --output badges.csv
```

## Course Setup

### 1. Create Course Configuration

```json
{
  "COURSE101": {
    "name": "My Course Name",
    "prefix": "Course",
    "min_words": 100,
    "badges": [
      {"weeks": 1, "emoji": "🌱", "title": "Beginner"},
      {"weeks": 5, "emoji": "🌿", "title": "Growing"},
      {"weeks": 10, "emoji": "🌳", "title": "Expert"}
    ]
  }
}
```

### 2. Load Configuration

```bash
badgequest load-config courses.json
```

### 3. Update LMS Form

Edit the extracted form to use your course ID:
```html
<input id="course_id" type="hidden" value="COURSE101" />
```

## Troubleshooting

### Common Issues

**CORS Errors**
- Update `CORS_ORIGINS` in `.env` with your LMS domain

**Database Locked**
- Ensure only one process accesses SQLite
- Consider PostgreSQL for production

**Invalid Reflections**
- Check word count meets minimum
- Verify readability score
- Ensure text isn't duplicate

### Getting Help

- GitHub Issues: [Report bugs or request features](https://github.com/yourusername/badgequest/issues)
- Discussions: [Ask questions and share ideas](https://github.com/yourusername/badgequest/discussions)

## Architecture Overview

```
BadgeQuest
├── Flask API (REST endpoints)
├── SQLite Database (reflections storage)
├── LMS Integration (HTML/JS forms)
├── CLI Tools (management commands)
└── Badge System (configurable progression)
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](../CONTRIBUTING.md) for details.

## License

BadgeQuest is released under the MIT License. See [LICENSE](../LICENSE) for details.