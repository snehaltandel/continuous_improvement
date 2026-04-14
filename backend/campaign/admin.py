from django.contrib import admin

from .models import Badge, CampaignProfile, Score, StepCriterion, Submission, UserBadge, Week, WeekStep


@admin.register(Week)
class WeekAdmin(admin.ModelAdmin):
    list_display = ("week_number", "title", "theme", "is_active")


@admin.register(WeekStep)
class WeekStepAdmin(admin.ModelAdmin):
    list_display = ("step_name", "week", "step_number", "max_points", "ai_enabled", "requires_human_review")
    inlines = [
        type(
            "StepCriterionInline",
            (admin.TabularInline,),
            {"model": StepCriterion, "extra": 0},
        )
    ]


admin.site.register(CampaignProfile)
admin.site.register(Submission)
admin.site.register(Score)
admin.site.register(Badge)
admin.site.register(UserBadge)
