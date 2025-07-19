"""Badge system logic."""

from .config import CourseConfig


class BadgeSystem:
    """Manages badge assignments based on progress."""

    def __init__(self, course_config: CourseConfig):
        self.config = course_config
        self.badge_levels = course_config.get_badge_tuples()

    def assign_badge(self, weeks_completed: int) -> str:
        """Assign a badge based on number of weeks completed."""
        for threshold, badge in reversed(self.badge_levels):
            if weeks_completed >= threshold:
                return badge
        return "❌ No Badge Yet"

    def get_next_badge_info(self, weeks_completed: int) -> dict | None:
        """Get information about the next badge level."""
        for threshold, badge in self.badge_levels:
            if weeks_completed < threshold:
                return {
                    "weeks_needed": threshold - weeks_completed,
                    "next_badge": badge,
                    "threshold": threshold,
                }
        return None

    def get_progress_summary(self, weeks_completed: int) -> dict:
        """Get a comprehensive progress summary."""
        current_badge = self.assign_badge(weeks_completed)
        next_info = self.get_next_badge_info(weeks_completed)

        summary = {
            "weeks_completed": weeks_completed,
            "current_badge": current_badge,
            "progress_percentage": min(100, (weeks_completed / self.config.max_weeks) * 100),
        }

        if next_info:
            summary.update(next_info)

        return summary
