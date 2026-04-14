import { useEffect, useState } from "react";

import { ChallengeRoom } from "./components/ChallengeRoom";
import { Leaderboard } from "./components/Leaderboard";
import { WeekCard } from "./components/WeekCard";
import { getDashboard, getWeek } from "./services/api";
import type { Dashboard, Week } from "./types";


export default function App() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [selectedWeek, setSelectedWeek] = useState<Week | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadDashboard() {
    try {
      const result = await getDashboard();
      setDashboard(result);
      setError(null);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Failed to load dashboard.");
    }
  }

  useEffect(() => {
    void loadDashboard();
  }, []);

  async function handleOpenWeek(weekId: number) {
    try {
      const week = await getWeek(weekId);
      setSelectedWeek(week);
      setError(null);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Failed to load week.");
    }
  }

  if (error) {
    return <main className="app-shell"><div className="status-banner">{error}</div></main>;
  }

  if (!dashboard) {
    return <main className="app-shell"><div className="status-banner">Loading campaign...</div></main>;
  }

  if (selectedWeek) {
    return (
      <main className="app-shell">
        <ChallengeRoom
          week={selectedWeek}
          onBack={() => setSelectedWeek(null)}
          onRefreshDashboard={loadDashboard}
        />
      </main>
    );
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <div>
          <div className="eyebrow">AI4CI Campaign</div>
          <h1>{dashboard.campaign_title}</h1>
          <p>
            Escape-room structure for continuous improvement learning with enforced human review before final
            submission.
          </p>
        </div>
        <div className="hero-stats">
          <div className="hero-stats__card">
            <span>Total score</span>
            <strong>{dashboard.total_points}</strong>
          </div>
          <div className="hero-stats__card">
            <span>Earned badges</span>
            <strong>{dashboard.earned_badges.length}</strong>
          </div>
        </div>
      </section>

      <section className="dashboard-grid">
        <div className="panel">
          <div className="panel__header">
            <h2>Campaign Rooms</h2>
            <span className="panel__meta">Progress by week</span>
          </div>
          <div className="week-grid">
            {dashboard.weeks.map((week) => (
              <WeekCard
                isResume={dashboard.resume_week_id === week.id}
                key={week.id}
                onOpen={handleOpenWeek}
                week={week}
              />
            ))}
          </div>
        </div>

        <div className="dashboard-side">
          <section className="panel">
            <div className="panel__header">
              <h2>Badges</h2>
              <span className="panel__meta">Milestones</span>
            </div>
            <div className="badge-list">
              {dashboard.earned_badges.length === 0 && <span>No badges yet.</span>}
              {dashboard.earned_badges.map((item) => (
                <div className="badge-pill" key={item.id}>
                  {item.badge.badge_name}
                </div>
              ))}
            </div>
          </section>
          <Leaderboard entries={dashboard.leaderboard} />
        </div>
      </section>
    </main>
  );
}
