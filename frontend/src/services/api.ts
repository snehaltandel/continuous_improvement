import type { Dashboard, Score, Submission, Week } from "../types";


const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";
const DEMO_USER = "learner1";

async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        "X-User": DEMO_USER,
        ...(options.headers ?? {}),
      },
    });
  } catch (error) {
    throw new Error(
      "Cannot reach the backend API. Start the Django server on port 8000 or set VITE_API_BASE to the correct API URL.",
    );
  }

  if (!response.ok) {
    const errorPayload = await response.json().catch(() => ({ detail: "Request failed." }));
    throw new Error(errorPayload.detail ?? "Request failed.");
  }

  return response.json();
}

export function getDashboard(): Promise<Dashboard> {
  return apiRequest<Dashboard>("/dashboard");
}

export function getWeek(weekId: number): Promise<Week> {
  return apiRequest<Week>(`/weeks/${weekId}`);
}

export function getWeekSubmissions(weekId: number): Promise<{ submissions: Submission[]; scores: Score[] }> {
  return apiRequest<{ submissions: Submission[]; scores: Score[] }>(`/weeks/${weekId}/submissions`);
}

export function assistStep(
  weekId: number,
  stepId: number,
  body: { raw_user_input: string; opportunity_notes?: string },
): Promise<{ refined_text: string; explanation: string; suggestions: string }> {
  return apiRequest(`/ai/weeks/${weekId}/steps/${stepId}/assist`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function submitStep(
  weekId: number,
  stepId: number,
  body: Record<string, unknown>,
): Promise<{ submission: Submission; score: Score; week_total: number }> {
  return apiRequest(`/weeks/${weekId}/steps/${stepId}/submit`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}
