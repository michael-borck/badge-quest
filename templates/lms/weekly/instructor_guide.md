# BadgeQuest Weekly Forms - Instructor Deployment Guide

## Overview

This guide explains how to deploy pre-configured weekly reflection forms in your LMS (Blackboard, Canvas, or Moodle). These forms significantly reduce student errors by pre-filling week and theme information.

## Benefits of Pre-configured Forms

- **90%+ Error Reduction**: No manual week/theme selection means no selection errors
- **Better Engagement**: Theme-specific prompts guide deeper reflections  
- **Progress Visibility**: Students see their badge progress in real-time
- **Auto-save**: Reflections are saved automatically every 30 seconds
- **Mobile Friendly**: All forms work perfectly on phones and tablets

## Quick Start

### 1. Update Server URL

Before deploying any forms, update the server URL in `badgequest_lib.js`:

```javascript
config: {
    serverUrl: 'https://your-badgequest-server.edu',  // <- Update this!
    // ... other config
}
```

### 2. Deploy Weekly Forms

#### Option A: Individual HTML Files (Recommended)

1. Upload these files to your LMS:
   - `badgequest_lib.js` (shared library - upload once)
   - `course_schedule.json` (course configuration - upload once)
   - `week_XX_[theme].html` (one per week)

2. In Blackboard:
   - Go to your course content area
   - Create Item > File > Browse and select the HTML file
   - Select "Display in New Window"
   - Name it clearly: "Week 1 Reflection Form"

#### Option B: Embed in Content Items

For tighter LMS integration, embed the form HTML directly:

1. Create a new content item
2. Switch to HTML editor mode
3. Paste the form HTML
4. Update the script src to point to your uploaded `badgequest_lib.js`

### 3. Set Up Course Structure

Recommended folder structure in your LMS:

```
📁 Weekly Reflections
  📄 How Reflections Work (overview)
  📁 Weekly Forms
    📄 Week 1: Introduction (week_01_introduction.html)
    📄 Week 2: Machine Learning (week_02_technical.html)
    📄 Week 3: Ethics in AI (week_03_ethics.html)
    ...
  📄 Catch-up Reflections (catch_up_form.html)
  📄 My Progress Dashboard (progress_dashboard.html)
```

## Deployment Schedule

### Pre-semester Setup
1. Upload `badgequest_lib.js` and `course_schedule.json`
2. Create folder structure
3. Upload all weekly forms (but hide future weeks)

### Weekly Tasks
1. **Sunday Night**: Make next week's form visible
2. **Monday Morning**: Send reminder with direct link to form
3. **Friday**: Check submission rates via progress reports

### Example Announcement
```
This week's reflection form is now available!

📝 Week 3: Ethics in AI
Theme: Ethics & Responsibility
Due: Sunday 11:59 PM

[Direct Link to Week 3 Form]

Remember: Completing this week earns your Explorer Badge! 🥾
```

## Customization Options

### 1. Modify Course Schedule

Edit `course_schedule.json` to match your course:

```json
{
  "week": 4,
  "week_id": "Week04",
  "title": "Your Topic Here",
  "theme_id": "innovation",
  "theme_name": "Innovation & Creativity",
  "prompts": [
    "Your custom prompt 1",
    "Your custom prompt 2"
  ]
}
```

### 2. Adjust Themes

Available themes:
- `technical` - Technical Analysis
- `ethics` - Ethics & Responsibility  
- `innovation` - Innovation & Creativity
- `collaboration` - Collaboration & Teamwork
- `critical_thinking` - Critical Thinking
- `""` (empty) - General Reflection

### 3. Customize Appearance

Each form's colors can be modified:
- Week 1: Blue (#007bff) - Introduction
- Week 2: Purple (#6f42c1) - Technical
- Week 3: Red (#dc3545) - Ethics
- Catch-up: Yellow (#ffc107)

## Student Experience Features

### Auto-save
- Drafts save every 30 seconds
- Students can close and return without losing work
- Clear notification when draft is saved

### Progress Tracking
- Real-time badge progress
- Micro-credential alerts
- Visual progress bars

### Smart Validation
- Character/word count with live feedback
- Confirmation before submission
- Clear error messages

### Already Submitted Detection
- Warning if trying to resubmit same week
- Prevents accidental duplicates

## Best Practices

### 1. Communication
- Introduce the system in Week 1
- Explain badges and micro-credentials
- Share the progress dashboard link

### 2. Reminders
- Set up automated weekly reminders
- Include direct links to forms
- Highlight special badges (Week 3, 5, 7, etc.)

### 3. Support
- Create FAQ for common issues
- Provide catch-up form for missed weeks
- Monitor submission rates weekly

## Troubleshooting

### "Server Error" Message
- Check that server URL is updated in `badgequest_lib.js`
- Verify server is running and accessible
- Check CORS settings if needed

### Forms Not Loading
- Ensure all files uploaded (especially `badgequest_lib.js`)
- Check file permissions in LMS
- Try "Display in New Window" option

### Students Can't See Forms
- Verify form is set to visible
- Check date restrictions
- Ensure students have proper role/permissions

## Analytics and Reporting

### Weekly Progress Report
```bash
badgequest generate-progress \
  --students students.txt \
  --course AI101 \
  --output week3_progress.csv
```

### Individual Student Check
Visit: `progress_dashboard.html?student_id=12345678`

### Bulk Operations
Use the `/api/progress/bulk` endpoint for course-wide analytics

## Advanced Features

### Custom Validation Rules
Modify in `badgequest_lib.js`:
```javascript
config: {
    minWords: 150,  // Increase minimum
    maxWords: 1000  // Add maximum
}
```

### Theme Rotation
Some courses benefit from rotating themes:
- Weeks 1-4: Technical focus
- Weeks 5-8: Ethics focus
- Weeks 9-12: Innovation focus

### Integration with Gradebook
The CSV export includes:
- Student ID
- Weeks Completed  
- Current Badge
- Micro-credentials Earned
- Micro-credentials List

## Support

For technical issues:
- Check the [BadgeQuest GitHub](https://github.com/yourusername/badgequest)
- Review server logs
- Contact your IT support team

For pedagogical questions:
- See the included rubric
- Review example reflections
- Consult teaching and learning center

---

Remember: The goal is to make reflections engaging and meaningful while reducing friction for students. These pre-configured forms handle the technical details so students can focus on reflection!