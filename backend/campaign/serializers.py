from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Badge, CampaignProfile, Score, StepCriterion, Submission, UserBadge, Week, WeekStep


class StepCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StepCriterion
        fields = ["id", "criterion_text", "sort_order", "required_for_full_score"]


class WeekStepSerializer(serializers.ModelSerializer):
    criteria = StepCriterionSerializer(many=True, read_only=True)

    class Meta:
        model = WeekStep
        fields = [
            "id",
            "step_number",
            "step_name",
            "instructions",
            "max_points",
            "ai_enabled",
            "requires_human_review",
            "guidance_prompts",
            "criteria",
        ]


class WeekSerializer(serializers.ModelSerializer):
    steps = WeekStepSerializer(many=True, read_only=True)

    class Meta:
        model = Week
        fields = [
            "id",
            "week_number",
            "title",
            "theme",
            "is_active",
            "unlock_rule",
            "scenario_title",
            "scenario_narrative",
            "clue_panel",
            "steps",
        ]


class SubmissionSerializer(serializers.ModelSerializer):
    step_number = serializers.IntegerField(source="step.step_number", read_only=True)
    step_name = serializers.CharField(source="step.step_name", read_only=True)

    class Meta:
        model = Submission
        fields = [
            "id",
            "submission_type",
            "step",
            "step_number",
            "step_name",
            "raw_user_input",
            "opportunity_notes",
            "ai_generated_output",
            "ai_explanation",
            "final_user_submission",
            "user_review_confirmed",
            "was_user_edited",
            "submitted_at",
            "updated_at",
        ]


class ScoreSerializer(serializers.ModelSerializer):
    step_number = serializers.IntegerField(source="step.step_number", read_only=True)

    class Meta:
        model = Score
        fields = [
            "id",
            "submission",
            "step",
            "step_number",
            "awarded_points",
            "max_points",
            "evaluator_feedback",
            "criteria_json",
            "scored_at",
        ]


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ["id", "badge_name", "badge_description", "points_threshold", "week_number_nullable"]


class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)

    class Meta:
        model = UserBadge
        fields = ["id", "badge", "awarded_at"]


class LeaderboardEntrySerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    username = serializers.CharField()
    display_name = serializers.CharField()
    total_points = serializers.IntegerField()
    badges = serializers.ListField(child=serializers.CharField())


class DashboardSerializer(serializers.Serializer):
    campaign_title = serializers.CharField()
    active_week = WeekSerializer()
    total_points = serializers.IntegerField()
    earned_badges = UserBadgeSerializer(many=True)
    weeks = WeekSerializer(many=True)
    leaderboard = LeaderboardEntrySerializer(many=True)
    resume_week_id = serializers.IntegerField(allow_null=True)


class DemoUserSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "display_name"]

    def get_display_name(self, obj: User) -> str:
        profile = getattr(obj, "campaign_profile", None)
        return profile.display_name if profile else obj.username
