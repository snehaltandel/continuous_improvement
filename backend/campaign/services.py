from typing import Any, Dict, List, Optional, Tuple

from django.contrib.auth.models import User
from django.db.models import Max, Sum

from .models import Badge, CampaignProfile, Score, StepCriterion, Submission, UserBadge, Week, WeekStep


def get_or_create_demo_user(request) -> User:
    if getattr(request, "user", None) and request.user.is_authenticated:
        user = request.user
    else:
        username = request.headers.get("X-User", "learner1").strip() or "learner1"
        user, _ = User.objects.get_or_create(username=username)
        CampaignProfile.objects.get_or_create(
            user=user,
            defaults={"display_name": username.replace("_", " ").title()},
        )
    return user


def evaluate_criteria(step: WeekStep, payload: Dict[str, Any]) -> Tuple[int, List[Dict[str, Any]], str]:
    criteria_results: List[Dict[str, Any]] = []

    raw_text = (payload.get("raw_user_input") or "").strip()
    ai_text = (payload.get("ai_generated_output") or "").strip()
    final_text = (payload.get("final_user_submission") or "").strip()
    notes = (payload.get("opportunity_notes") or "").strip()
    review_confirmed = bool(payload.get("user_review_confirmed"))
    source_text = final_text or ai_text or raw_text
    word_count = len(source_text.split())

    for criterion in step.criteria.all():
        text = criterion.criterion_text.lower()
        passed = False

        if "clear issue" in text:
            passed = word_count >= 8 and any(token in source_text.lower() for token in ["delay", "rework", "confusion", "inconsistent", "problem", "miss"])
        elif "observable process" in text or "outcome" in text:
            passed = any(token in source_text.lower() for token in ["process", "shipment", "inspection", "line", "label", "shift", "queue"])
        elif "improvement opportunity" in text:
            passed = bool(notes or any(token in source_text.lower() for token in ["improve", "opportunity", "reduce", "fix"]))
        elif "understandable language" in text:
            passed = word_count >= 8
        elif "retains original issue" in text or "preserves" in text:
            passed = raw_text and raw_text[:30].lower() in ai_text.lower() or any(token in ai_text.lower() for token in raw_text.lower().split()[:3])
        elif "improves clarity" in text or "better clarity" in text or "clearer structure" in text:
            passed = len(ai_text) >= len(raw_text) and len(ai_text.split(".")) >= len(raw_text.split("."))
        elif "identifies who or what is affected" in text or "audience aware" in text:
            passed = any(token in source_text.lower() for token in ["team", "operators", "customers", "orders", "shipments", "staff", "leadership"])
        elif "grounded in scenario" in text or "retains evidence" in text:
            passed = any(token in source_text.lower() for token in ["shift", "label", "inspection", "rework", "shipment", "queue"])
        elif "no unsupported assumptions" in text or "avoids unsupported assumptions" in text:
            passed = "because management" not in source_text.lower()
        elif "user reviewed ai output" in text or "review confirmed" in text:
            passed = review_confirmed
        elif "specific and coherent" in text or "coherent" in text:
            passed = word_count >= 12
        elif "suitable for ci use" in text:
            passed = any(token in source_text.lower() for token in ["process", "defect", "rework", "delay", "handoff", "root cause"])
        elif "business-appropriate" in text:
            passed = "!!!" not in source_text and word_count >= 8
        elif "reflects human judgment" in text:
            passed = review_confirmed and bool(final_text)
        elif "plausible cause" in text:
            passed = word_count >= 8
        elif "structured reasoning" in text:
            passed = ":" in source_text or "-" in source_text or "\n" in source_text
        elif "specific root cause" in text or "specific ask" in text:
            passed = word_count >= 10
        elif "clear proposal" in text or "impact stated" in text:
            passed = word_count >= 10
        else:
            passed = word_count >= 8

        criteria_results.append({"criterion": criterion.criterion_text, "passed": passed})

    passed_count = sum(1 for item in criteria_results if item["passed"])
    total_count = len(criteria_results) or 1
    awarded_points = round(step.max_points * (passed_count / total_count))

    if passed_count == total_count:
        feedback = "All configured criteria were met."
    else:
        unmet = [item["criterion"] for item in criteria_results if not item["passed"]]
        feedback = "Strengthen: " + "; ".join(unmet)

    return awarded_points, criteria_results, feedback


def generate_ai_assist(step: WeekStep, raw_text: str, notes: str = "") -> Dict[str, str]:
    base = raw_text.strip()
    notes_text = notes.strip()
    refined = base

    if step.week.week_number == 1:
        refined = (
            "The packing process is missing shipment cutoffs because inconsistent work instructions, "
            "inspection queues, and rework on relabeled boxes create avoidable delays for operators and outbound orders. "
            f"Observed evidence: {base}"
        )
        if notes_text:
            refined += f" Improvement opportunity: {notes_text}"
        explanation = "The AI tightened the statement around the observed process issue, affected parties, and visible evidence."
        suggestions = "Confirm the wording matches the scenario and remove anything that does not reflect your own judgment."
    else:
        refined = f"AI-assisted revision: {base}"
        if notes_text:
            refined += f" Context: {notes_text}"
        explanation = "The AI reorganized the draft for clarity while preserving the original intent."
        suggestions = "Review and revise the AI draft before final submission."

    return {
        "refined_text": refined,
        "explanation": explanation,
        "suggestions": suggestions,
    }


def latest_submission(user: User, step: WeekStep, submission_type: Optional[str] = None) -> Optional[Submission]:
    queryset = Submission.objects.filter(user=user, step=step)
    if submission_type:
        queryset = queryset.filter(submission_type=submission_type)
    return queryset.order_by("-submitted_at").first()


def can_submit_step(user: User, step: WeekStep) -> Tuple[bool, str]:
    if step.step_number == 1:
        return True, ""

    prior_step = WeekStep.objects.filter(week=step.week, step_number=step.step_number - 1).first()
    if not prior_step:
        return True, ""

    prior_submission = latest_submission(user, prior_step)
    if not prior_submission:
        return False, "Complete the previous step before continuing."

    return True, ""


def save_submission_and_score(user: User, step: WeekStep, payload: Dict[str, Any], submission_type: str) -> Tuple[Submission, Score]:
    submission = Submission.objects.create(
        user=user,
        week=step.week,
        step=step,
        submission_type=submission_type,
        raw_user_input=payload.get("raw_user_input", ""),
        opportunity_notes=payload.get("opportunity_notes", ""),
        ai_generated_output=payload.get("ai_generated_output", ""),
        ai_explanation=payload.get("ai_explanation", ""),
        final_user_submission=payload.get("final_user_submission", ""),
        user_review_confirmed=bool(payload.get("user_review_confirmed")),
        was_user_edited=bool(payload.get("was_user_edited")),
    )

    awarded_points, criteria_results, feedback = evaluate_criteria(step, payload)
    score = Score.objects.create(
        submission=submission,
        user=user,
        week=step.week,
        step=step,
        awarded_points=awarded_points,
        max_points=step.max_points,
        evaluator_feedback=feedback,
        criteria_json=criteria_results,
    )
    award_badges(user)
    return submission, score


def award_badges(user: User) -> None:
    total_points = get_user_total_points(user)
    completed_weeks = (
        Submission.objects.filter(user=user, submission_type="final")
        .values_list("week__week_number", flat=True)
        .distinct()
    )

    for badge in Badge.objects.all():
        if badge.points_threshold is not None and total_points >= badge.points_threshold:
            UserBadge.objects.get_or_create(user=user, badge=badge)
        if badge.week_number_nullable is not None and badge.week_number_nullable in completed_weeks:
            UserBadge.objects.get_or_create(user=user, badge=badge)


def get_user_total_points(user: User) -> int:
    latest_scores = (
        Score.objects.filter(user=user)
        .values("step")
        .annotate(latest_scored_at=Max("scored_at"))
    )
    latest_score_ids = []
    for item in latest_scores:
        score = (
            Score.objects.filter(user=user, step_id=item["step"], scored_at=item["latest_scored_at"])
            .order_by("-id")
            .first()
        )
        if score:
            latest_score_ids.append(score.id)
    return Score.objects.filter(id__in=latest_score_ids).aggregate(total=Sum("awarded_points"))["total"] or 0


def serialize_leaderboard() -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for user in User.objects.all().order_by("username"):
        display_name = getattr(getattr(user, "campaign_profile", None), "display_name", user.username)
        badges = list(user.user_badges.select_related("badge").values_list("badge__badge_name", flat=True))
        entries.append(
            {
                "username": user.username,
                "display_name": display_name,
                "total_points": get_user_total_points(user),
                "badges": badges,
            }
        )

    entries.sort(key=lambda item: (-item["total_points"], item["display_name"]))
    for index, entry in enumerate(entries, start=1):
        entry["rank"] = index
    return entries


def get_resume_week_id(user: User) -> Optional[int]:
    weeks = Week.objects.order_by("week_number")
    for week in weeks:
        total_steps = week.steps.count()
        completed_steps = (
            Submission.objects.filter(user=user, week=week)
            .values("step")
            .distinct()
            .count()
        )
        if completed_steps < total_steps:
            return week.id
    return weeks.first().id if weeks.exists() else None


def ensure_review_requirement(step: WeekStep, payload: Dict[str, Any]) -> Tuple[bool, str]:
    if step.requires_human_review and not payload.get("user_review_confirmed"):
        return False, "Human review confirmation is required for this step."
    if step.requires_human_review and not payload.get("final_user_submission"):
        return False, "A final reviewed submission is required for this step."
    return True, ""
