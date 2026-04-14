from django.contrib.auth.models import User
from django.db import models


class CampaignProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="campaign_profile")
    display_name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.display_name


class Week(models.Model):
    week_number = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=120)
    theme = models.CharField(max_length=120)
    is_active = models.BooleanField(default=False)
    unlock_rule = models.CharField(max_length=255, blank=True)
    scenario_title = models.CharField(max_length=255, blank=True)
    scenario_narrative = models.TextField(blank=True)
    clue_panel = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["week_number"]

    def __str__(self) -> str:
        return f"Week {self.week_number}: {self.theme}"


class WeekStep(models.Model):
    week = models.ForeignKey(Week, on_delete=models.CASCADE, related_name="steps")
    step_number = models.PositiveIntegerField()
    step_name = models.CharField(max_length=160)
    instructions = models.TextField()
    max_points = models.PositiveIntegerField()
    ai_enabled = models.BooleanField(default=False)
    requires_human_review = models.BooleanField(default=False)
    guidance_prompts = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["week__week_number", "step_number"]
        unique_together = ("week", "step_number")

    def __str__(self) -> str:
        return f"{self.week} / Step {self.step_number}"


class StepCriterion(models.Model):
    week_step = models.ForeignKey(WeekStep, on_delete=models.CASCADE, related_name="criteria")
    criterion_text = models.TextField()
    sort_order = models.PositiveIntegerField(default=1)
    required_for_full_score = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return self.criterion_text[:60]


class Submission(models.Model):
    SUBMISSION_TYPES = [
        ("draft", "Draft"),
        ("ai-assisted", "AI Assisted"),
        ("final", "Final"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submissions")
    week = models.ForeignKey(Week, on_delete=models.CASCADE, related_name="submissions")
    step = models.ForeignKey(WeekStep, on_delete=models.CASCADE, related_name="submissions")
    submission_type = models.CharField(max_length=24, choices=SUBMISSION_TYPES)
    raw_user_input = models.TextField(blank=True)
    opportunity_notes = models.TextField(blank=True)
    ai_generated_output = models.TextField(blank=True)
    ai_explanation = models.TextField(blank=True)
    final_user_submission = models.TextField(blank=True)
    user_review_confirmed = models.BooleanField(default=False)
    was_user_edited = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self) -> str:
        return f"{self.user.username} / {self.week} / {self.step.step_number} / {self.submission_type}"


class Score(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="scores")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="scores")
    week = models.ForeignKey(Week, on_delete=models.CASCADE, related_name="scores")
    step = models.ForeignKey(WeekStep, on_delete=models.CASCADE, related_name="scores")
    awarded_points = models.PositiveIntegerField()
    max_points = models.PositiveIntegerField()
    evaluator_feedback = models.TextField(blank=True)
    criteria_json = models.JSONField(default=list, blank=True)
    scored_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-scored_at"]


class Badge(models.Model):
    badge_name = models.CharField(max_length=120, unique=True)
    badge_description = models.TextField()
    points_threshold = models.PositiveIntegerField(null=True, blank=True)
    week_number_nullable = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return self.badge_name


class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_badges")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="user_badges")
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "badge")
