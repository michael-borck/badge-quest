"""Micro-credentials system for theme-based achievements."""


from .config import CourseConfig
from .models import Database


class MicroCredentialSystem:
    """Manages micro-credential assignments based on themes and submissions."""

    def __init__(self, course_config: CourseConfig, db: Database):
        self.config = course_config
        self.db = db
        self.credentials = course_config.micro_credentials

    def check_and_award_credentials(
        self, student_id: str, course_id: str, theme_id: str | None
    ) -> list[dict]:
        """Check if student has earned any new micro-credentials.

        Returns:
            List of newly awarded credentials
        """
        if not theme_id or not self.credentials:
            return []

        newly_awarded = []

        # Check each credential
        for cred_id, cred_info in self.credentials.items():
            # Skip if student already has this credential
            existing_creds = self.db.get_student_micro_credentials(student_id, course_id)
            if any(cred["credential_id"] == cred_id for cred in existing_creds):
                continue

            # Check if current theme matches credential themes
            if theme_id in cred_info.get("themes", []):
                # Get all weeks where student submitted reflections for matching themes
                weeks_for_themes = []
                for theme in cred_info.get("themes", []):
                    theme_weeks = self.db.get_student_theme_weeks(student_id, course_id, theme)
                    weeks_for_themes.extend(theme_weeks)

                # Remove duplicates and count
                unique_weeks = list(set(weeks_for_themes))

                # Check if minimum submissions met
                min_submissions = cred_info.get("min_submissions", 1)
                if len(unique_weeks) >= min_submissions:
                    # Award the credential
                    awarded = self.db.add_micro_credential(
                        student_id, course_id, cred_id, unique_weeks
                    )
                    if awarded:
                        newly_awarded.append({
                            "credential_id": cred_id,
                            "name": cred_info.get("name", cred_id),
                            "emoji": cred_info.get("emoji", "🏅"),
                            "description": cred_info.get("description", ""),
                            "weeks_completed": unique_weeks,
                        })

        return newly_awarded

    def get_student_credentials_display(self, student_id: str, course_id: str) -> list[dict]:
        """Get formatted micro-credentials for display."""
        earned_creds = self.db.get_student_micro_credentials(student_id, course_id)

        display_creds = []
        for earned in earned_creds:
            cred_id = earned["credential_id"]
            if cred_id in self.credentials:
                cred_info = self.credentials[cred_id]
                display_creds.append({
                    "credential_id": cred_id,
                    "name": cred_info.get("name", cred_id),
                    "emoji": cred_info.get("emoji", "🏅"),
                    "description": cred_info.get("description", ""),
                    "earned_date": earned["earned_date"],
                    "weeks_completed": earned["weeks_completed"],
                })

        return display_creds

    def get_credentials_progress(self, student_id: str, course_id: str) -> list[dict]:
        """Get progress toward all available micro-credentials."""
        progress = []

        for cred_id, cred_info in self.credentials.items():
            # Check if already earned
            existing_creds = self.db.get_student_micro_credentials(student_id, course_id)
            earned = any(cred["credential_id"] == cred_id for cred in existing_creds)

            if earned:
                # Include earned credential info
                earned_cred = next(c for c in existing_creds if c["credential_id"] == cred_id)
                progress.append({
                    "credential_id": cred_id,
                    "name": cred_info.get("name", cred_id),
                    "emoji": cred_info.get("emoji", "🏅"),
                    "description": cred_info.get("description", ""),
                    "status": "earned",
                    "earned_date": earned_cred["earned_date"],
                    "progress": f"{len(earned_cred['weeks_completed'])}/{cred_info.get('min_submissions', 1)}",
                })
            else:
                # Calculate progress
                weeks_for_themes = []
                for theme in cred_info.get("themes", []):
                    theme_weeks = self.db.get_student_theme_weeks(student_id, course_id, theme)
                    weeks_for_themes.extend(theme_weeks)

                unique_weeks = list(set(weeks_for_themes))
                min_needed = cred_info.get("min_submissions", 1)

                progress.append({
                    "credential_id": cred_id,
                    "name": cred_info.get("name", cred_id),
                    "emoji": cred_info.get("emoji", "🏅"),
                    "description": cred_info.get("description", ""),
                    "status": "in_progress",
                    "progress": f"{len(unique_weeks)}/{min_needed}",
                    "themes_needed": cred_info.get("themes", []),
                    "weeks_remaining": max(0, min_needed - len(unique_weeks)),
                })

        return progress
