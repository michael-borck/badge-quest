"""Flask application for BadgeQuest."""

from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS

from .badges import BadgeSystem
from .config import Config
from .models import Database, ReflectionProcessor
from .similarity import SimilarityChecker
from .validators import ReflectionValidator


def create_app(config_class=Config) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize CORS
    CORS(app, origins=config_class.CORS_ORIGINS)

    # Initialize database
    db = Database(config_class().DATABASE_PATH)
    processor = ReflectionProcessor(config_class.SECRET_KEY)

    @app.route("/stamp", methods=["POST"])
    def stamp():
        """Submit a reflection for validation and storage."""
        data = request.get_json()
        text = data.get("text", "").strip()
        week_id = data.get("week_id", "").strip()
        student_id = data.get("student_id", "").strip()
        course_id = data.get("course_id", "default").strip()

        if not text or not week_id or not student_id:
            return jsonify({"error": "Missing text, week_id, or student_id"}), 400

        # Get course configuration
        course_config = config_class.get_course_config(course_id)
        validator = ReflectionValidator(course_config)
        badge_system = BadgeSystem(course_config)

        # Validate the reflection
        is_valid, error_message, metrics = validator.validate(text)

        if not is_valid:
            return jsonify(
                {
                    "valid": False,
                    "reason": error_message,
                    "word_count": metrics["word_count"],
                    "readability": metrics["readability"],
                    "sentiment": metrics["sentiment"],
                }
            )

        # Check for exact duplicates first
        fingerprint = processor.get_fingerprint(text)
        if db.check_duplicate(fingerprint):
            return jsonify(
                {
                    "valid": False,
                    "reason": "Exact duplicate submission detected",
                    "word_count": metrics["word_count"],
                    "readability": metrics["readability"],
                    "sentiment": metrics["sentiment"],
                }
            )

        # Check for similarity with previous submissions
        similarity_checker = SimilarityChecker(course_config.similarity_threshold)
        previous_reflections = db.get_student_reflections_encrypted(student_id, course_id)

        if previous_reflections:
            # Decode previous reflections for comparison
            previous_texts = []
            for week_id_prev, encrypted_text in previous_reflections:
                if encrypted_text:  # Skip if no text stored
                    try:
                        decoded_text = similarity_checker.decode_text(encrypted_text)
                        previous_texts.append((week_id_prev, decoded_text))
                    except Exception:
                        # Skip if decoding fails
                        pass

            # Check similarity
            if previous_texts:
                for week_id_prev, prev_text in previous_texts:
                    similarity = similarity_checker.calculate_similarity(text, prev_text)
                    if similarity > course_config.similarity_threshold:
                        return jsonify(
                            {
                                "valid": False,
                                "reason": f"Too similar to your {week_id_prev} submission ({similarity:.0%} similarity)",
                                "word_count": metrics["word_count"],
                                "readability": metrics["readability"],
                                "sentiment": metrics["sentiment"],
                                "similarity_score": similarity,
                                "threshold": course_config.similarity_threshold,
                            }
                        )

        # Generate code and store reflection
        code = processor.generate_code(text, week_id, student_id)

        # Encode text for storage
        text_encrypted = similarity_checker.encode_text(text)

        db.add_reflection(
            student_id=student_id,
            course_id=course_id,
            fingerprint=fingerprint,
            week_id=week_id,
            code=code,
            word_count=int(metrics["word_count"]),
            readability=metrics["readability"],
            sentiment=metrics["sentiment"],
            text_encrypted=text_encrypted,
        )

        # Get progress information
        weeks = db.get_student_weeks(student_id, course_id)
        progress = badge_system.get_progress_summary(len(weeks))

        return jsonify(
            {
                "valid": True,
                "code": code,
                "word_count": metrics["word_count"],
                "readability": metrics["readability"],
                "sentiment": metrics["sentiment"],
                "weeks_completed": progress["weeks_completed"],
                "current_badge": progress["current_badge"],
                "progress_percentage": progress["progress_percentage"],
                "next_badge_info": progress.get("next_badge"),
                "note": "📌 This badge status will be uploaded to Grade Centre weekly.",
            }
        )

    @app.route("/verify/<code>")
    def verify(code: str):
        """Verify a reflection code."""
        details = db.verify_code(code)
        if details:
            return (
                f"✅ Code {code} is valid for {details['week_id']} "
                f"by {details['student_id']} in {details['course_id']} "
                f"(submitted {details['timestamp']})"
            )
        else:
            return f"❌ Code {code} not found or invalid."

    @app.route("/progress/<student_id>")
    def progress(student_id: str):
        """View student progress."""
        course_id = request.args.get("course", "default")
        format_type = request.args.get("format", "html")

        course_config = config_class.get_course_config(course_id)
        badge_system = BadgeSystem(course_config)

        weeks = db.get_student_weeks(student_id, course_id)
        progress_info = badge_system.get_progress_summary(len(weeks))

        if format_type == "json":
            return jsonify(
                {"student_id": student_id, "course_id": course_id, "weeks": weeks, **progress_info}
            )

        # HTML response
        html = f"""
        <html><body style="font-family: Arial; max-width: 600px; margin: auto;">
        <h2>🎓 {course_config.name} Reflection Journey</h2>
        <p><strong>Student ID:</strong> {student_id}</p>
        <p><strong>Weeks Completed:</strong> {progress_info["weeks_completed"]}</p>
        <p><strong>Current Badge:</strong> {progress_info["current_badge"]}</p>
        <p><strong>Progress:</strong> {progress_info["progress_percentage"]:.0f}%</p>
        """

        if "next_badge" in progress_info:
            html += f"""
            <p><strong>Next Badge:</strong> {progress_info["next_badge"]}
            (in {progress_info["weeks_needed"]} more weeks)</p>
            """

        if weeks:
            html += "<h3>Completed Weeks:</h3><ul>"
            html += "".join(f"<li>{w}</li>" for w in sorted(weeks))
            html += "</ul>"

        html += "</body></html>"
        return render_template_string(html)

    @app.route("/api/progress/bulk", methods=["POST"])
    def bulk_progress():
        """Get progress for multiple students."""
        data = request.get_json()
        student_ids = data.get("student_ids", [])
        course_id = data.get("course_id", "default")

        if not student_ids:
            return jsonify({"error": "No student IDs provided"}), 400

        course_config = config_class.get_course_config(course_id)
        badge_system = BadgeSystem(course_config)

        results = []
        for student_id in student_ids:
            weeks = db.get_student_weeks(student_id, course_id)
            progress_info = badge_system.get_progress_summary(len(weeks))
            results.append(
                {
                    "student_id": student_id,
                    "weeks_completed": len(weeks),
                    "badge": progress_info["current_badge"],
                }
            )

        return jsonify({"course_id": course_id, "results": results})

    @app.route("/health")
    def health():
        """Health check endpoint."""
        return jsonify(
            {"status": "healthy", "app": config_class.APP_NAME, "version": config_class.APP_VERSION}
        )

    return app
