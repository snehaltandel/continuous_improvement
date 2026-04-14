from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Score, Submission, UserBadge, Week, WeekStep
from .seed import seed_campaign
from .serializers import DashboardSerializer, ScoreSerializer, SubmissionSerializer, WeekSerializer, WeekStepSerializer
from .services import (
    can_submit_step,
    ensure_review_requirement,
    evaluate_criteria,
    generate_ai_assist,
    get_or_create_demo_user,
    get_resume_week_id,
    get_user_total_points,
    save_submission_and_score,
    serialize_leaderboard,
)


def ensure_seeded() -> None:
    seed_campaign()


class DashboardView(APIView):
    def get(self, request):
        ensure_seeded()
        user = get_or_create_demo_user(request)
        weeks = Week.objects.prefetch_related("steps__criteria").all()
        active_week = weeks.filter(is_active=True).first() or weeks.first()
        earned_badges = UserBadge.objects.filter(user=user).select_related("badge")
        payload = {
            "campaign_title": "AI4CI Gamified Escape Room Campaign",
            "active_week": active_week,
            "total_points": get_user_total_points(user),
            "earned_badges": earned_badges,
            "weeks": weeks,
            "leaderboard": serialize_leaderboard()[:10],
            "resume_week_id": get_resume_week_id(user),
        }
        return Response(DashboardSerializer(payload).data)


class WeeksView(APIView):
    def get(self, request):
        ensure_seeded()
        queryset = Week.objects.prefetch_related("steps__criteria").all()
        return Response(WeekSerializer(queryset, many=True).data)


class WeekDetailView(APIView):
    def get(self, request, week_id: int):
        ensure_seeded()
        week = Week.objects.prefetch_related("steps__criteria").get(id=week_id)
        return Response(WeekSerializer(week).data)


class WeekStepsView(APIView):
    def get(self, request, week_id: int):
        ensure_seeded()
        steps = WeekStep.objects.filter(week_id=week_id).prefetch_related("criteria")
        return Response(WeekStepSerializer(steps, many=True).data)


class SubmissionsView(APIView):
    def get(self, request, week_id: int):
        ensure_seeded()
        user = get_or_create_demo_user(request)
        submissions = Submission.objects.filter(user=user, week_id=week_id).select_related("step")
        scores = Score.objects.filter(user=user, week_id=week_id).select_related("step", "submission")
        return Response(
            {
                "submissions": SubmissionSerializer(submissions, many=True).data,
                "scores": ScoreSerializer(scores, many=True).data,
            }
        )


class StepSubmissionView(APIView):
    def post(self, request, week_id: int, step_id: int):
        ensure_seeded()
        user = get_or_create_demo_user(request)
        step = WeekStep.objects.select_related("week").prefetch_related("criteria").get(id=step_id, week_id=week_id)

        can_submit, reason = can_submit_step(user, step)
        if not can_submit:
            return Response({"detail": reason}, status=status.HTTP_400_BAD_REQUEST)

        payload = request.data.copy()
        submission_type = payload.get("submission_type", "draft")
        if submission_type not in {"draft", "ai-assisted", "final"}:
            return Response({"detail": "Invalid submission type."}, status=status.HTTP_400_BAD_REQUEST)

        meets_review_rule, review_message = ensure_review_requirement(step, payload)
        if not meets_review_rule:
            return Response({"detail": review_message}, status=status.HTTP_400_BAD_REQUEST)

        submission, score = save_submission_and_score(user, step, payload, submission_type)
        return Response(
            {
                "submission": SubmissionSerializer(submission).data,
                "score": ScoreSerializer(score).data,
                "week_total": get_user_total_points(user),
            },
            status=status.HTTP_201_CREATED,
        )


class AssistView(APIView):
    def post(self, request, week_id: int, step_id: int):
        ensure_seeded()
        user = get_or_create_demo_user(request)
        step = WeekStep.objects.select_related("week").get(id=step_id, week_id=week_id)
        can_submit, reason = can_submit_step(user, step)
        if not can_submit:
            return Response({"detail": reason}, status=status.HTTP_400_BAD_REQUEST)

        raw_text = request.data.get("raw_user_input", "")
        notes = request.data.get("opportunity_notes", "")
        result = generate_ai_assist(step, raw_text, notes)
        return Response(result)


class EvaluateView(APIView):
    def post(self, request, week_id: int, step_id: int):
        ensure_seeded()
        step = WeekStep.objects.prefetch_related("criteria").get(id=step_id, week_id=week_id)
        payload = request.data.copy()
        awarded_points, criteria_results, feedback = evaluate_criteria(step, payload)
        return Response(
            {
                "step_id": step.id,
                "step_number": step.step_number,
                "awarded_points": awarded_points,
                "max_points": step.max_points,
                "criteria_json": criteria_results,
                "evaluator_feedback": feedback,
            }
        )


class LeaderboardView(APIView):
    def get(self, request):
        ensure_seeded()
        return Response(serialize_leaderboard())
