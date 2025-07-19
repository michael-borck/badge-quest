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
                writer.writerow(["Student ID", "Completed Weeks", "Badge"])
                for result in results:
                    writer.writerow(
                        [result["student_id"], result["weeks_completed"], result["badge"]]
                    )

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
                    rows.append((sid, data["weeks_completed"], data["current_badge"]))
                else:
                    rows.append((sid, "0", "❌ Not Found"))
            except Exception:
                rows.append((sid, "0", "❌ Error"))

    # Write CSV
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Student ID", "Completed Weeks", "Badge"])
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
