/**
 * BadgeQuest Enhanced Form Library
 * Provides common functionality for all reflection forms
 */

const BadgeQuest = {
  // Configuration
  config: {
    minWords: 100,
    maxWords: 1000,
    serverUrl: 'https://badgequest.serveur.au',
    storagePrefix: 'badgequest_'
  },

  // Initialize form enhancements
  init: function(weekNumber, weekId, themeId, themeName) {
    this.weekNumber = weekNumber;
    this.weekId = weekId;
    this.themeId = themeId;
    this.themeName = themeName;
    
    // Check if already submitted
    this.checkPreviousSubmission();
    
    // Set up auto-save
    this.setupAutoSave();
    
    // Set up character/word counter
    this.setupCounter();
    
    // Load any saved draft
    this.loadDraft();
  },

  // Check if student already submitted for this week
  checkPreviousSubmission: function() {
    const submitted = localStorage.getItem(this.config.storagePrefix + 'submitted_' + this.weekId);
    if (submitted) {
      const warningDiv = document.createElement('div');
      warningDiv.style.cssText = 'background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; margin-bottom: 15px; border-radius: 5px;';
      warningDiv.innerHTML = '⚠️ <strong>Note:</strong> You have already submitted a reflection for ' + this.weekId + '. Submitting again will not earn additional credit.';
      document.querySelector('#submission-form').prepend(warningDiv);
    }
  },

  // Auto-save draft every 30 seconds
  setupAutoSave: function() {
    const textArea = document.getElementById('reflection');
    let autoSaveTimeout;
    
    textArea.addEventListener('input', () => {
      clearTimeout(autoSaveTimeout);
      autoSaveTimeout = setTimeout(() => {
        this.saveDraft();
      }, 30000); // 30 seconds
    });
    
    // Save on blur
    textArea.addEventListener('blur', () => {
      this.saveDraft();
    });
  },

  // Save draft to localStorage
  saveDraft: function() {
    const text = document.getElementById('reflection').value;
    if (text.trim()) {
      localStorage.setItem(this.config.storagePrefix + 'draft_' + this.weekId, text);
      this.showNotification('Draft saved', 'success', 2000);
    }
  },

  // Load saved draft
  loadDraft: function() {
    const draft = localStorage.getItem(this.config.storagePrefix + 'draft_' + this.weekId);
    if (draft) {
      document.getElementById('reflection').value = draft;
      this.updateCounter();
      this.showNotification('Draft loaded from previous session', 'info', 3000);
    }
  },

  // Clear draft after successful submission
  clearDraft: function() {
    localStorage.removeItem(this.config.storagePrefix + 'draft_' + this.weekId);
  },

  // Set up word/character counter
  setupCounter: function() {
    const textArea = document.getElementById('reflection');
    const counterDiv = document.createElement('div');
    counterDiv.id = 'counter';
    counterDiv.style.cssText = 'text-align: right; font-size: 0.9em; color: #666; margin-top: 5px;';
    textArea.parentNode.insertBefore(counterDiv, textArea.nextSibling);
    
    textArea.addEventListener('input', () => this.updateCounter());
    this.updateCounter();
  },

  // Update word/character count
  updateCounter: function() {
    const text = document.getElementById('reflection').value;
    const words = text.trim().split(/\s+/).filter(w => w.length > 0).length;
    const chars = text.length;
    
    const counterDiv = document.getElementById('counter');
    let color = '#666';
    let message = '';
    
    if (words < this.config.minWords) {
      color = '#dc3545';
      message = ` (minimum ${this.config.minWords} required)`;
    } else if (words > this.config.maxWords) {
      color = '#dc3545';
      message = ` (maximum ${this.config.maxWords} allowed)`;
    } else {
      color = '#28a745';
      message = ' ✓';
    }
    
    counterDiv.innerHTML = `<span style="color: ${color}">${words} words${message}</span> | ${chars} characters`;
  },

  // Enhanced submission with confirmation
  submitReflection: function() {
    const studentId = document.getElementById('student_id').value.trim();
    const text = document.getElementById('reflection').value.trim();
    const resultDiv = document.getElementById('result');
    
    // Validation
    if (!studentId) {
      this.showError('Please enter your Student ID');
      return;
    }
    
    if (!text) {
      this.showError('Please enter your reflection');
      return;
    }
    
    const words = text.split(/\s+/).filter(w => w.length > 0).length;
    if (words < this.config.minWords) {
      this.showError(`Your reflection must be at least ${this.config.minWords} words (currently ${words} words)`);
      return;
    }
    
    // Confirmation dialog
    const confirmMsg = `Submit reflection for:\n\nWeek ${this.weekNumber}: ${this.weekId}\nTheme: ${this.themeName || 'General Reflection'}\nWord count: ${words}\n\nAre you sure you want to submit?`;
    
    if (!confirm(confirmMsg)) {
      return;
    }
    
    // Show loading state
    resultDiv.innerHTML = '<p style="color: #007bff;">⏳ Submitting your reflection...</p>';
    const submitBtn = document.querySelector('button[onclick*="submitReflection"]');
    submitBtn.disabled = true;
    
    // Submit
    fetch(this.config.serverUrl + '/stamp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: studentId,
        week_id: this.weekId,
        text: text,
        course_id: document.getElementById('course_id').value,
        theme_id: this.themeId
      })
    })
    .then(response => response.json())
    .then(data => {
      submitBtn.disabled = false;
      
      if (!data.valid) {
        this.showSubmissionError(data);
      } else {
        this.showSubmissionSuccess(data);
        // Mark as submitted
        localStorage.setItem(this.config.storagePrefix + 'submitted_' + this.weekId, 'true');
        // Clear draft
        this.clearDraft();
        // Clear form
        document.getElementById('reflection').value = '';
        this.updateCounter();
      }
    })
    .catch(err => {
      console.error(err);
      submitBtn.disabled = false;
      resultDiv.innerHTML = '<p style="color: red;">⚠️ Server error. Please try again later.</p>';
    });
  },

  // Show submission error with details
  showSubmissionError: function(data) {
    const resultDiv = document.getElementById('result');
    let html = `
      <div style="background: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px;">
        <p style="color: #721c24; font-weight: bold; margin: 0 0 10px 0;">❌ Submission failed: ${data.reason || 'Unknown error'}</p>
        <ul style="margin: 0; padding-left: 20px;">
          <li>Word count: ${data.word_count} ${data.word_count >= this.config.minWords ? '✓' : '✗'}</li>
          <li>Readability: ${data.readability} ${data.readability >= 50 ? '✓' : '✗'}</li>
          <li>Sentiment: ${data.sentiment}</li>
    `;
    
    if (data.similarity_score) {
      html += `<li>Similarity to previous submission: ${(data.similarity_score * 100).toFixed(0)}%</li>`;
    }
    
    html += `
        </ul>
        <p style="margin: 10px 0 0 0; font-size: 0.9em;">Please revise your reflection and try again.</p>
      </div>
    `;
    
    resultDiv.innerHTML = html;
  },

  // Show submission success with enhanced details
  showSubmissionSuccess: function(data) {
    const resultDiv = document.getElementById('result');
    let html = `
      <div style="background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px;">
        <p style="color: #155724; font-weight: bold; margin: 0 0 10px 0;">✅ Submission accepted!</p>
        <div style="background: white; padding: 10px; border-radius: 5px; margin: 10px 0;">
          <strong>Your reflection code:</strong> <code style="font-size: 1.2em; background: #f8f9fa; padding: 5px 10px; border-radius: 3px;">${data.code}</code>
        </div>
        <ul style="margin: 0; padding-left: 20px;">
          <li>Word count: ${data.word_count} ✓</li>
          <li>Readability score: ${data.readability}</li>
          <li>Sentiment score: ${data.sentiment}</li>
          <li>Weeks completed: ${data.weeks_completed} / 12</li>
          <li>Current badge: ${data.current_badge}</li>
    `;
    
    if (data.micro_credentials_earned > 0) {
      html += `<li>Micro-credentials earned: ${data.micro_credentials_earned}</li>`;
    }
    
    html += '</ul>';
    
    // Progress bar
    const progress = (data.weeks_completed / 12 * 100).toFixed(0);
    html += `
      <div style="margin: 15px 0;">
        <div style="background: #e9ecef; border-radius: 10px; height: 20px; overflow: hidden;">
          <div style="background: #28a745; width: ${progress}%; height: 100%; text-align: center; color: white; line-height: 20px; font-size: 0.8em;">
            ${progress}%
          </div>
        </div>
      </div>
    `;
    
    // Newly awarded credentials
    if (data.newly_awarded_credentials && data.newly_awarded_credentials.length > 0) {
      html += `
        <div style="background: #cff4fc; border: 1px solid #b6effb; padding: 10px; margin: 10px 0; border-radius: 5px;">
          <p style="color: #0c5460; font-weight: bold; margin: 0;">🎉 ${data.celebration_message}</p>
          <ul style="margin: 5px 0 0 0; padding-left: 20px;">
      `;
      for (const cred of data.newly_awarded_credentials) {
        html += `<li>${cred.emoji} <strong>${cred.name}</strong> - ${cred.description}</li>`;
      }
      html += '</ul></div>';
    }
    
    // Next badge info
    if (data.next_badge_info) {
      html += `<p style="margin: 10px 0 0 0; font-style: italic;">Next badge: ${data.next_badge_info} (${12 - data.weeks_completed} weeks to go)</p>`;
    }
    
    html += `
        <p style="margin: 10px 0 0 0; font-size: 0.9em; color: #666;">📌 Your badge status will be uploaded to Grade Centre weekly.</p>
      </div>
    `;
    
    resultDiv.innerHTML = html;
  },

  // Show temporary notification
  showNotification: function(message, type, duration) {
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      padding: 10px 20px;
      border-radius: 5px;
      color: white;
      font-weight: bold;
      z-index: 1000;
      animation: slideIn 0.3s ease-out;
    `;
    
    const colors = {
      success: '#28a745',
      error: '#dc3545',
      info: '#17a2b8'
    };
    
    notification.style.background = colors[type] || colors.info;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.style.animation = 'slideOut 0.3s ease-out';
      setTimeout(() => notification.remove(), 300);
    }, duration);
  },

  // Show error message
  showError: function(message) {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = `<p style="color: #dc3545; font-weight: bold;">⚠️ ${message}</p>`;
  }
};

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  @keyframes slideOut {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
  }
`;
document.head.appendChild(style);
