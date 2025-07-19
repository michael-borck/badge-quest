# BadgeQuest Deployment Guide

This guide covers deploying BadgeQuest to a VPS for production use.

## Prerequisites

- A VPS with Ubuntu 20.04+ or similar
- Python 3.10 or higher
- A domain name (optional but recommended for HTTPS)
- Basic knowledge of Linux administration

## Quick Start

### 1. Install BadgeQuest

```bash
# Install Python and pip
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Create a directory for the application
sudo mkdir -p /opt/badgequest
sudo chown $USER:$USER /opt/badgequest
cd /opt/badgequest

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install BadgeQuest
pip install badgequest
```

### 2. Configure Environment

Create a `.env` file:

```bash
cat > .env << EOF
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
DATABASE_URL=sqlite:////opt/badgequest/reflections.db
CORS_ORIGINS=https://your-lms.edu,https://blackboard.your-university.edu
EOF
```

### 3. Initialize Database

```bash
badgequest init-db
```

### 4. Test the Server

```bash
badgequest run-server --host 0.0.0.0 --port 5000
```

Visit `http://your-server-ip:5000/health` to verify it's working.

## Production Deployment with Gunicorn

### 1. Install Gunicorn

```bash
pip install gunicorn
```

### 2. Create Gunicorn Service

```bash
sudo nano /etc/systemd/system/badgequest.service
```

Add the following content:

```ini
[Unit]
Description=BadgeQuest Reflection System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/badgequest
Environment="PATH=/opt/badgequest/venv/bin"
ExecStart=/opt/badgequest/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:badgequest.sock \
    -m 007 \
    "badgequest:create_app()"

[Install]
WantedBy=multi-user.target
```

### 3. Start the Service

```bash
sudo systemctl start badgequest
sudo systemctl enable badgequest
sudo systemctl status badgequest
```

## Nginx Configuration

### 1. Install Nginx

```bash
sudo apt install nginx
```

### 2. Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/badgequest
```

Add:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/opt/badgequest/badgequest.sock;
    }

    location /health {
        include proxy_params;
        proxy_pass http://unix:/opt/badgequest/badgequest.sock;
    }
}
```

### 3. Enable the Site

```bash
sudo ln -s /etc/nginx/sites-available/badgequest /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## HTTPS with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Course Configuration

### 1. Create Course Configuration File

```bash
cd /opt/badgequest
badgequest example-config
# Edit courses_example.json as needed
mv courses_example.json courses.json
```

### 2. Load Configuration

```bash
badgequest load-config courses.json
```

## LMS Integration

### 1. Extract Form Template

```bash
badgequest extract-lms blackboard --course-id AI101 --output blackboard_form.html
```

### 2. Update Form URL

Edit `blackboard_form.html` and replace `YOUR_SERVER_URL` with your actual server URL:

```javascript
fetch("https://your-domain.com/stamp", {
```

### 3. Add to Blackboard

1. Log into Blackboard as an instructor
2. Navigate to your course
3. Create a new Item or Module Page
4. Switch to HTML mode
5. Paste the contents of `blackboard_form.html`
6. Save and make available to students

## Weekly Progress Updates

### 1. Create Student List

```bash
# Create a file with student IDs (one per line)
nano students.txt
```

### 2. Generate Progress Report

```bash
badgequest generate-progress \
    --students students.txt \
    --course AI101 \
    --server https://your-domain.com \
    --output badge_upload.csv
```

### 3. Upload to Blackboard

1. Go to Grade Center > Work Offline > Upload
2. Select `badge_upload.csv`
3. Map columns appropriately
4. Submit

## Monitoring

### Check Logs

```bash
# Service logs
sudo journalctl -u badgequest -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Database Backup

```bash
# Create backup
cp /opt/badgequest/reflections.db /opt/badgequest/reflections_$(date +%Y%m%d).db

# Setup automated backups with cron
crontab -e
# Add: 0 2 * * * cp /opt/badgequest/reflections.db /opt/badgequest/backups/reflections_$(date +\%Y\%m\%d).db
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure www-data user has access to database file
   ```bash
   sudo chown www-data:www-data /opt/badgequest/reflections.db
   ```

2. **CORS Errors**: Update CORS_ORIGINS in .env file with your LMS domain

3. **502 Bad Gateway**: Check if the service is running
   ```bash
   sudo systemctl status badgequest
   ```

4. **Database Locked**: Ensure only one process accesses the SQLite database

## Security Considerations

1. Always use HTTPS in production
2. Set a strong SECRET_KEY
3. Limit CORS origins to your LMS domains only
4. Regular backups of the database
5. Keep system and dependencies updated
6. Consider using PostgreSQL for larger deployments

## Support

For issues and questions, visit: https://github.com/yourusername/badgequest/issues