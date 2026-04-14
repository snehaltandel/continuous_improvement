import type { LeaderboardEntry } from "../types";


export function Leaderboard({ entries }: { entries: LeaderboardEntry[] }) {
  return (
    <section className="panel">
      <div className="panel__header">
        <h2>Leaderboard</h2>
        <span className="panel__meta">Top performers</span>
      </div>
      <div className="leaderboard">
        {entries.map((entry) => (
          <div className="leaderboard__row" key={entry.username}>
            <div>
              <strong>#{entry.rank}</strong> {entry.display_name}
            </div>
            <div>{entry.total_points} pts</div>
          </div>
        ))}
      </div>
    </section>
  );
}
