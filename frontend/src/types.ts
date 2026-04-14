export interface CriterionResult {
  criterion: string;
  passed: boolean;
}

export interface Score {
  id: number;
  submission: number;
  step: number;
  step_number: number;
  awarded_points: number;
  max_points: number;
  evaluator_feedback: string;
  criteria_json: CriterionResult[];
  scored_at: string;
}

export interface Step {
  id: number;
  step_number: number;
  step_name: string;
  instructions: string;
  max_points: number;
  ai_enabled: boolean;
  requires_human_review: boolean;
  guidance_prompts: string[];
  criteria: Array<{
    id: number;
    criterion_text: string;
    sort_order: number;
    required_for_full_score: boolean;
  }>;
}

export interface Week {
  id: number;
  week_number: number;
  title: string;
  theme: string;
  is_active: boolean;
  unlock_rule: string;
  scenario_title: string;
  scenario_narrative: string;
  clue_panel: string[];
  steps: Step[];
}

export interface LeaderboardEntry {
  rank: number;
  username: string;
  display_name: string;
  total_points: number;
  badges: string[];
}

export interface Badge {
  id: number;
  badge: {
    id: number;
    badge_name: string;
    badge_description: string;
    points_threshold: number | null;
    week_number_nullable: number | null;
  };
  awarded_at: string;
}

export interface Dashboard {
  campaign_title: string;
  active_week: Week;
  total_points: number;
  earned_badges: Badge[];
  weeks: Week[];
  leaderboard: LeaderboardEntry[];
  resume_week_id: number | null;
}

export interface Submission {
  id: number;
  submission_type: "draft" | "ai-assisted" | "final";
  step: number;
  step_number: number;
  step_name: string;
  raw_user_input: string;
  opportunity_notes: string;
  ai_generated_output: string;
  ai_explanation: string;
  final_user_submission: string;
  user_review_confirmed: boolean;
  was_user_edited: boolean;
  submitted_at: string;
  updated_at: string;
}
