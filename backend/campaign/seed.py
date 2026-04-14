from django.contrib.auth.models import User

from .models import Badge, CampaignProfile, StepCriterion, Week, WeekStep


CAMPAIGN_SEED = [
    {
        "week_number": 1,
        "title": "Week 1",
        "theme": "See",
        "is_active": True,
        "scenario_title": "Bottleneck at the Packing Line",
        "scenario_narrative": (
            "A packaging team is missing shipment cutoffs three days a week. Rework, unclear handoffs, "
            "and inconsistent labeling are creating delays, but the team has not defined the problem clearly."
        ),
        "clue_panel": [
            "Orders queue at final inspection every afternoon.",
            "Operators report inconsistent work instructions between shifts.",
            "Re-labeled boxes are often found in the rework area.",
        ],
        "steps": [
            {
                "step_number": 1,
                "step_name": "Draft Problem Statement",
                "instructions": "Describe what is not working, what evidence you see, and who or what is affected.",
                "max_points": 20,
                "ai_enabled": False,
                "requires_human_review": False,
                "guidance_prompts": [
                    "What is not working as expected?",
                    "Where do you see delay, waste, rework, confusion, or inconsistency?",
                    "Who or what is affected?",
                    "What evidence suggests there is an improvement opportunity?",
                ],
                "criteria": [
                    "clear issue identified",
                    "observable process or outcome",
                    "improvement opportunity identified",
                    "understandable language",
                ],
            },
            {
                "step_number": 2,
                "step_name": "AI Refined Problem Statement",
                "instructions": "Review the AI refinement and confirm the AI-assisted version before moving on.",
                "max_points": 30,
                "ai_enabled": True,
                "requires_human_review": False,
                "guidance_prompts": [
                    "Check whether the original issue is preserved.",
                    "Make sure the statement stays grounded in the scenario.",
                ],
                "criteria": [
                    "retains original issue",
                    "improves clarity",
                    "identifies who or what is affected",
                    "grounded in scenario",
                    "no unsupported assumptions",
                ],
            },
            {
                "step_number": 3,
                "step_name": "Human Reviewed Final Problem Statement",
                "instructions": "Edit or approve the AI-assisted version, confirm your review, and submit the final statement.",
                "max_points": 50,
                "ai_enabled": True,
                "requires_human_review": True,
                "guidance_prompts": [
                    "Does the final statement reflect your judgment?",
                    "Is the wording business-appropriate and specific?",
                ],
                "criteria": [
                    "user reviewed AI output",
                    "specific and coherent",
                    "suitable for CI use",
                    "business-appropriate wording",
                    "reflects human judgment",
                ],
            },
        ],
    },
    {
        "week_number": 2,
        "title": "Week 2",
        "theme": "Solve",
        "is_active": False,
        "scenario_title": "Root Cause Lab",
        "scenario_narrative": "Use the same scenario to conduct a structured root cause analysis.",
        "clue_panel": ["Shifts escalate the same issue differently.", "The same defects recur after rework."],
        "steps": [
            {
                "step_number": 1,
                "step_name": "Draft RCA",
                "instructions": "Draft an initial root cause analysis.",
                "max_points": 25,
                "ai_enabled": False,
                "requires_human_review": False,
                "guidance_prompts": ["List likely causes before choosing root causes."],
                "criteria": ["plausible cause list", "cause tied to evidence", "structured reasoning"],
            },
            {
                "step_number": 2,
                "step_name": "AI Enhanced RCA",
                "instructions": "Use AI to sharpen the reasoning without inventing causes.",
                "max_points": 25,
                "ai_enabled": True,
                "requires_human_review": False,
                "guidance_prompts": ["Preserve evidence and avoid assumptions."],
                "criteria": ["retains evidence", "better structure", "avoids unsupported assumptions"],
            },
            {
                "step_number": 3,
                "step_name": "Final RCA",
                "instructions": "Review and submit the final RCA.",
                "max_points": 50,
                "ai_enabled": True,
                "requires_human_review": True,
                "guidance_prompts": ["Confirm review before final submission."],
                "criteria": ["review confirmed", "specific root cause", "business-ready wording"],
            },
        ],
    },
    {
        "week_number": 3,
        "title": "Week 3",
        "theme": "Share",
        "is_active": False,
        "scenario_title": "Share-out Studio",
        "scenario_narrative": "Convert the analysis into a concise, persuasive improvement proposal.",
        "clue_panel": ["Leadership wants one-slide clarity.", "Frontline staff care about practical impact."],
        "steps": [
            {
                "step_number": 1,
                "step_name": "Draft Proposal",
                "instructions": "Draft the improvement proposal.",
                "max_points": 25,
                "ai_enabled": False,
                "requires_human_review": False,
                "guidance_prompts": ["Focus on outcome, audience, and practical impact."],
                "criteria": ["clear proposal", "audience aware", "impact stated"],
            },
            {
                "step_number": 2,
                "step_name": "AI Enhanced Proposal",
                "instructions": "Let AI improve clarity and persuasion.",
                "max_points": 25,
                "ai_enabled": True,
                "requires_human_review": False,
                "guidance_prompts": ["Improve structure without changing the proposal."],
                "criteria": ["clearer structure", "persuasive wording", "retains core message"],
            },
            {
                "step_number": 3,
                "step_name": "Final Share-out",
                "instructions": "Review and submit the final communication.",
                "max_points": 50,
                "ai_enabled": True,
                "requires_human_review": True,
                "guidance_prompts": ["Make sure it sounds like you, not just the AI."],
                "criteria": ["review confirmed", "specific ask", "business-appropriate communication"],
            },
        ],
    },
    {
        "week_number": 4,
        "title": "Week 4",
        "theme": "Final Escape",
        "is_active": False,
        "scenario_title": "Integrated Challenge",
        "scenario_narrative": "Combine observation, root cause analysis, and proposal design under time pressure.",
        "clue_panel": ["Hints are limited.", "The final answer must reflect human judgment."],
        "steps": [
            {
                "step_number": 1,
                "step_name": "Integrated Draft",
                "instructions": "Prepare the end-to-end draft.",
                "max_points": 30,
                "ai_enabled": False,
                "requires_human_review": False,
                "guidance_prompts": ["Connect problem, cause, and solution logically."],
                "criteria": ["problem captured", "cause captured", "solution direction captured"],
            },
            {
                "step_number": 2,
                "step_name": "AI Escape Assist",
                "instructions": "Use AI carefully to improve the integrated draft.",
                "max_points": 20,
                "ai_enabled": True,
                "requires_human_review": False,
                "guidance_prompts": ["Do not let AI invent unsupported content."],
                "criteria": ["preserves original logic", "better clarity", "no unsupported assumptions"],
            },
            {
                "step_number": 3,
                "step_name": "Final Escape Submission",
                "instructions": "Review, confirm, and submit the final end-to-end response.",
                "max_points": 50,
                "ai_enabled": True,
                "requires_human_review": True,
                "guidance_prompts": ["Final submission must be explicitly reviewed."],
                "criteria": ["review confirmed", "coherent end-to-end story", "business-ready final output"],
            },
        ],
    },
]


BADGE_SEED = [
    ("Week 1 Complete", "Completed the Week 1 challenge.", None, 1),
    ("Week 2 Complete", "Completed the Week 2 challenge.", None, 2),
    ("Week 3 Complete", "Completed the Week 3 challenge.", None, 3),
    ("Final Escape", "Completed the final challenge.", None, 4),
    ("100 Point Club", "Reached 100 total points.", 100, None),
    ("250 Point Club", "Reached 250 total points.", 250, None),
]


def seed_campaign() -> None:
    if Week.objects.exists():
        return

    for week_payload in CAMPAIGN_SEED:
        steps_payload = week_payload["steps"]
        week = Week.objects.create(
            week_number=week_payload["week_number"],
            title=week_payload["title"],
            theme=week_payload["theme"],
            is_active=week_payload["is_active"],
            unlock_rule=week_payload.get("unlock_rule", ""),
            scenario_title=week_payload["scenario_title"],
            scenario_narrative=week_payload["scenario_narrative"],
            clue_panel=week_payload["clue_panel"],
        )
        for step_payload in steps_payload:
            criteria_payload = step_payload["criteria"]
            step = WeekStep.objects.create(
                week=week,
                step_number=step_payload["step_number"],
                step_name=step_payload["step_name"],
                instructions=step_payload["instructions"],
                max_points=step_payload["max_points"],
                ai_enabled=step_payload["ai_enabled"],
                requires_human_review=step_payload["requires_human_review"],
                guidance_prompts=step_payload["guidance_prompts"],
            )
            for index, criterion_text in enumerate(criteria_payload, start=1):
                StepCriterion.objects.create(
                    week_step=step,
                    criterion_text=criterion_text,
                    sort_order=index,
                    required_for_full_score=True,
                )

    for badge_name, description, threshold, week_number in BADGE_SEED:
        Badge.objects.get_or_create(
            badge_name=badge_name,
            defaults={
                "badge_description": description,
                "points_threshold": threshold,
                "week_number_nullable": week_number,
            },
        )

    for username in ["learner1", "lean_lead", "ops_star"]:
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password("demo1234")
            user.save()
        CampaignProfile.objects.get_or_create(
            user=user,
            defaults={"display_name": username.replace("_", " ").title()},
        )
