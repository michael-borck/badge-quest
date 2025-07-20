# BadgeQuest Pre-configured Weekly Forms

This directory contains templates for creating pre-configured weekly reflection forms that significantly reduce student errors and improve the user experience.

## 📁 Files Overview

### Core Templates
- **`week_01_introduction.html`** - Example Week 1 form (general reflection)
- **`week_02_technical.html`** - Example Week 2 form (technical theme)
- **`week_03_ethics.html`** - Example Week 3 form (ethics theme)
- **`catch_up_form.html`** - Form for submitting missed reflections
- **`progress_dashboard.html`** - Student progress viewer

### Supporting Files
- **`badgequest_lib.js`** - Shared JavaScript library with enhanced features
- **`course_schedule.json`** - Course configuration and weekly themes
- **`instructor_guide.md`** - Detailed deployment instructions

## 🚀 Quick Start

1. **Update Server URL**: Edit `badgequest_lib.js` and change:
   ```javascript
   serverUrl: 'https://YOUR_SERVER_URL'  // <- Update this!
   ```

2. **Generate Forms**: Use the CLI to generate all weekly forms:
   ```bash
   badgequest generate-weekly-forms \
     --schedule course_schedule.json \
     --output my_forms \
     --server-url https://badges.myuni.edu
   ```

3. **Deploy to LMS**: Upload forms to your Blackboard/Canvas/Moodle course

## ✨ Key Features

### Error Prevention
- **Pre-filled Values**: Week and theme are hardcoded (no selection errors)
- **Confirmation Dialog**: Shows exactly what will be submitted
- **Already Submitted Warning**: Prevents accidental resubmissions
- **Smart Validation**: Real-time word count and requirement checking

### Enhanced UX
- **Auto-save**: Drafts save every 30 seconds
- **Progress Visibility**: Shows current badge and micro-credentials
- **Theme-specific Prompts**: Guides deeper reflection
- **Mobile Responsive**: Works perfectly on all devices

### Instructor Benefits
- **Zero Configuration**: Students can't select wrong week/theme
- **Better Compliance**: Clear requirements and progress tracking
- **Easy Deployment**: One-time setup per semester
- **Analytics Ready**: Progress dashboard for tracking

## 📊 Form Types

### 1. Weekly Forms (`week_XX_theme.html`)
- One form per week with pre-configured settings
- Theme-specific prompts and guidance
- Micro-credential alerts when applicable
- Badge milestone notifications

### 2. Catch-up Form (`catch_up_form.html`)
- For missed weeks only
- Shows which weeks are already completed
- Validates against already submitted weeks
- Maintains same quality requirements

### 3. Progress Dashboard (`progress_dashboard.html`)
- Visual badge progression
- Micro-credentials earned and in-progress
- Weekly completion grid
- Downloadable progress report

## 🎨 Customization

### Colors by Theme
- General: Blue (#007bff)
- Technical: Purple (#6f42c1)
- Ethics: Red (#dc3545)
- Innovation: Green (#28a745)
- Collaboration: Orange (#fd7e14)

### Modify Prompts
Edit `course_schedule.json` to customize:
```json
{
  "week": 4,
  "prompts": [
    "Your custom prompt here",
    "Another reflection question"
  ]
}
```

## 📈 Student Experience Flow

1. **Week Opens**: Form becomes visible in LMS
2. **Student Clicks**: Direct link to pre-configured form
3. **Auto-fills**: Previous draft loads if exists
4. **Real-time Feedback**: Word count, requirements
5. **Submit**: Confirmation dialog → Success with code
6. **Progress**: Badge and micro-credential updates

## 🔧 Technical Details

### Local Storage Usage
- `badgequest_draft_WeekXX` - Auto-saved drafts
- `badgequest_submitted_WeekXX` - Submission tracking
- `badgequest_visited` - First-time user detection

### Form Validation
- Minimum 100 words (configurable)
- Student ID required
- Reflection text required
- Theme automatically set

### Security
- No sensitive data in localStorage
- Server-side validation required
- CORS properly configured
- HTTPS recommended

## 📚 See Also
- [Instructor Guide](instructor_guide.md) - Detailed deployment instructions
- [BadgeQuest Documentation](https://github.com/yourusername/badgequest)
- [Example Course Schedule](course_schedule.json)