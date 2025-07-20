"""Command-line interface for BadgeQuest."""

import csv
import json
import sys
from pathlib import Path

import click
import requests

from . import __version__
from .app import create_app
from .models import Database


@click.group()
@click.version_option(version=__version__, prog_name="BadgeQuest")
def cli():
    """BadgeQuest - Collect, learn, repeat.

    A gamified reflection system for Learning Management Systems.
    """
    pass


@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=5000, help="Port to bind to")
@click.option("--debug", is_flag=True, help="Run in debug mode")
def run_server(host: str, port: int, debug: bool):
    """Run the BadgeQuest Flask server."""
    app = create_app()
    click.echo(f"🚀 Starting BadgeQuest server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)


@cli.command()
@click.option("--db-path", default=None, help="Database path (defaults to config)")
def init_db(db_path: str | None):
    """Initialize the database."""
    Database(db_path)
    click.echo("✅ Database initialized successfully")


@cli.command()
@click.argument("lms", type=click.Choice(["blackboard", "canvas", "moodle"]))
@click.option("--output", "-o", default="form.html", help="Output filename")
@click.option("--course-id", default="default", help="Course ID for configuration")
def extract_lms(lms: str, output: str, course_id: str):
    """Extract LMS integration templates."""
    template_dir = Path(__file__).parent.parent.parent / "templates" / "lms"

    if lms == "blackboard":
        form_path = template_dir / "blackboard_form.html"
        rubric_path = template_dir / "blackboard_rubric.md"

        if not form_path.exists():
            click.echo(f"❌ Template not found: {form_path}", err=True)
            sys.exit(1)

        # Read and customize the form
        with open(form_path) as f:
            content = f.read()

        # Replace course ID placeholder
        content = content.replace('value="default"', f'value="{course_id}"')

        # Write output
        with open(output, "w") as f:
            f.write(content)

        click.echo(f"✅ Extracted Blackboard form to: {output}")

        # Also extract rubric if it exists
        if rubric_path.exists():
            rubric_output = output.replace(".html", "_rubric.md")
            with open(rubric_path) as f:
                rubric_content = f.read()
            with open(rubric_output, "w") as f:
                f.write(rubric_content)
            click.echo(f"✅ Extracted rubric to: {rubric_output}")
    else:
        click.echo(f"❌ LMS '{lms}' not yet supported", err=True)
        sys.exit(1)


@cli.command()
@click.option("--students", "-s", required=True, help="File with student IDs (one per line)")
@click.option("--course", "-c", default="default", help="Course ID")
@click.option("--output", "-o", default="badge_upload.csv", help="Output CSV file")
@click.option("--server", default="http://localhost:5000", help="BadgeQuest server URL")
def generate_progress(students: str, course: str, output: str, server: str):
    """Generate progress CSV for grade center upload."""
    # Read student IDs
    student_ids = []
    with open(students) as f:
        student_ids = [line.strip() for line in f if line.strip()]

    if not student_ids:
        click.echo("❌ No student IDs found in file", err=True)
        sys.exit(1)

    click.echo(f"📊 Fetching progress for {len(student_ids)} students...")

    # Use bulk endpoint if available
    try:
        response = requests.post(
            f"{server}/api/progress/bulk",
            json={"student_ids": student_ids, "course_id": course},
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()
            results = data["results"]

            # Write CSV
            with open(output, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Student ID", "Completed Weeks", "Badge", "Micro-Credentials Earned", "Micro-Credentials List"])
                for result in results:
                    # Format micro-credentials list
                    micro_creds_list = ""
                    if result.get("micro_credentials"):
                        micro_creds_list = "; ".join([
                            f"{cred['emoji']} {cred['name']}"
                            for cred in result["micro_credentials"]
                        ])

                    writer.writerow([
                        result["student_id"],
                        result["weeks_completed"],
                        result["badge"],
                        result.get("micro_credentials_earned", 0),
                        micro_creds_list
                    ])

            click.echo(f"✅ Progress report saved to: {output}")
            return
    except Exception as e:
        click.echo(f"⚠️  Bulk endpoint failed, falling back to individual queries: {e}")

    # Fallback to individual queries
    rows = []
    with click.progressbar(student_ids, label="Fetching progress") as bar:
        for sid in bar:
            try:
                response = requests.get(
                    f"{server}/progress/{sid}",
                    params={"course": course, "format": "json"},
                    timeout=5,
                )
                if response.status_code == 200:
                    data = response.json()
                    # Format micro-credentials list
                    micro_creds_list = ""
                    micro_creds_earned = 0
                    if "micro_credentials" in data and data["micro_credentials"].get("earned"):
                        earned = data["micro_credentials"]["earned"]
                        micro_creds_earned = len(earned)
                        micro_creds_list = "; ".join([
                            f"{cred['emoji']} {cred['name']}"
                            for cred in earned
                        ])

                    rows.append((
                        sid,
                        data["weeks_completed"],
                        data["current_badge"],
                        micro_creds_earned,
                        micro_creds_list
                    ))
                else:
                    rows.append((sid, "0", "❌ Not Found", "0", ""))
            except Exception:
                rows.append((sid, "0", "❌ Error", "0", ""))

    # Write CSV
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Student ID", "Completed Weeks", "Badge", "Micro-Credentials Earned", "Micro-Credentials List"])
        writer.writerows(rows)

    click.echo(f"✅ Progress report saved to: {output}")


@cli.command()
@click.argument("config_file", type=click.Path(exists=True))
def load_config(config_file: str):
    """Load course configurations from a JSON file."""
    try:
        with open(config_file) as f:
            courses = json.load(f)

        click.echo(f"📋 Loaded {len(courses)} course configurations:")
        for course_id, config in courses.items():
            click.echo(f"  - {course_id}: {config.get('name', 'Unnamed')}")

        # Save to a local config file that the app can use
        config_path = Path("courses.json")
        with open(config_path, "w") as f:
            json.dump(courses, f, indent=2)

        click.echo(f"✅ Saved to: {config_path}")
        click.echo("💡 Set BADGEQUEST_COURSES_FILE environment variable to use this file")

    except Exception as e:
        click.echo(f"❌ Error loading config: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--schedule", "-s", type=click.Path(exists=True), required=True, help="Course schedule JSON file")
@click.option("--output", "-o", default="weekly_forms", help="Output directory for forms")
@click.option("--server-url", default="https://YOUR_SERVER_URL", help="BadgeQuest server URL")
def generate_weekly_forms(schedule: str, output: str, server_url: str):
    """Generate pre-configured weekly forms from course schedule."""
    import shutil
    from pathlib import Path

    # Load schedule
    try:
        with open(schedule) as f:
            course_data = json.load(f)
    except Exception as e:
        click.echo(f"❌ Error loading schedule: {e}", err=True)
        sys.exit(1)

    # Create output directory
    output_path = Path(output)
    output_path.mkdir(exist_ok=True)

    # Get template directory
    template_dir = Path(__file__).parent.parent.parent / "templates" / "lms" / "weekly"

    # Copy shared files
    shared_files = ["badgequest_lib.js", "course_schedule.json", "catch_up_form.html",
                   "progress_dashboard.html", "instructor_guide.md"]

    for file in shared_files:
        src = template_dir / file
        if src.exists():
            dst = output_path / file
            shutil.copy2(src, dst)

            # Update server URL in files
            if file.endswith((".js", ".html")):
                with open(dst) as f:
                    content = f.read()
                content = content.replace("https://YOUR_SERVER_URL", server_url)
                with open(dst, "w") as f:
                    f.write(content)

    # Generate week-specific forms
    week_template = template_dir / "week_01_introduction.html"
    if week_template.exists():
        with open(week_template) as f:
            template_content = f.read()
    else:
        click.echo("⚠️  Week template not found, using basic template", err=True)
        template_content = "<html><body>Week {{week}} Form</body></html>"

    # Generate forms for each week
    generated = 0
    for week_data in course_data.get("schedule", []):
        week_num = week_data["week"]
        week_id = week_data["week_id"]
        title = week_data["title"]
        theme_id = week_data.get("theme_id", "")
        theme_name = week_data.get("theme_name", "General Reflection")

        # Determine filename
        if theme_id:
            filename = f"week_{str(week_num).zfill(2)}_{theme_id}.html"
        else:
            filename = f"week_{str(week_num).zfill(2)}_general.html"

        # Customize content
        form_content = template_content
        form_content = form_content.replace("Week 1:", f"Week {week_num}:")
        form_content = form_content.replace("Introduction to AI", title)
        form_content = form_content.replace('value="Week01"', f'value="{week_id}"')
        form_content = form_content.replace('BadgeQuest.init(1,', f'BadgeQuest.init({week_num},')
        form_content = form_content.replace("'Week01',", f"'{week_id}',")
        form_content = form_content.replace("General Reflection", theme_name)
        form_content = form_content.replace('value=""', f'value="{theme_id}"')
        form_content = form_content.replace(server_url, server_url)

        # Write form
        with open(output_path / filename, "w") as f:
            f.write(form_content)
        generated += 1

    click.echo(f"✅ Generated {generated} weekly forms in: {output_path}")
    click.echo("📁 Files created:")
    for file in sorted(output_path.iterdir()):
        click.echo(f"   - {file.name}")
    click.echo("\n💡 Next steps:")
    click.echo("   1. Review and customize the forms")
    click.echo("   2. Update server URL in badgequest_lib.js")
    click.echo("   3. Upload to your LMS")
    click.echo("   4. See instructor_guide.md for deployment tips")


@cli.command()
def example_config():
    """Generate an example course configuration file."""
    example = {
        "AI101": {
            "name": "Introduction to AI",
            "prefix": "AI",
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
                {"weeks": 14, "emoji": "🏆", "title": "Mastery"},
            ],
        },
        "CS101": {
            "name": "Computer Science Fundamentals",
            "prefix": "CS",
            "min_words": 150,
            "min_readability": 45,
            "min_sentiment": -0.1,
            "max_weeks": 14,
            "badges": [
                {"weeks": 1, "emoji": "💻", "title": "Novice"},
                {"weeks": 3, "emoji": "⌨️", "title": "Coder"},
                {"weeks": 5, "emoji": "🔧", "title": "Developer"},
                {"weeks": 7, "emoji": "🏗️", "title": "Builder"},
                {"weeks": 10, "emoji": "🚀", "title": "Engineer"},
                {"weeks": 12, "emoji": "🎯", "title": "Architect"},
                {"weeks": 14, "emoji": "🌟", "title": "Master"},
            ],
        },
    }

    with open("courses_example.json", "w") as f:
        json.dump(example, f, indent=2)

    click.echo("✅ Created example configuration: courses_example.json")


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
