from django.urls import path

from .views import (
    AssistView,
    DashboardView,
    EvaluateView,
    LeaderboardView,
    StepSubmissionView,
    SubmissionsView,
    WeekDetailView,
    WeeksView,
    WeekStepsView,
)


urlpatterns = [
    path("dashboard", DashboardView.as_view()),
    path("weeks", WeeksView.as_view()),
    path("weeks/<int:week_id>", WeekDetailView.as_view()),
    path("weeks/<int:week_id>/steps", WeekStepsView.as_view()),
    path("weeks/<int:week_id>/steps/<int:step_id>/submit", StepSubmissionView.as_view()),
    path("weeks/<int:week_id>/submissions", SubmissionsView.as_view()),
    path("ai/weeks/<int:week_id>/steps/<int:step_id>/assist", AssistView.as_view()),
    path("ai/weeks/<int:week_id>/steps/<int:step_id>/evaluate", EvaluateView.as_view()),
    path("leaderboard", LeaderboardView.as_view()),
]
