import type { Week } from "../types";


interface WeekCardProps {
  week: Week;
  isResume: boolean;
  onOpen: (weekId: number) => void;
}


export function WeekCard({ week, isResume, onOpen }: WeekCardProps) {
  return (
    <article className={`week-card ${week.is_active ? "week-card--active" : ""}`}>
      <div className="week-card__eyebrow">Week {week.week_number}</div>
      <h3>{week.theme}</h3>
      <p>{week.scenario_title}</p>
      <div className="week-card__footer">
        <span>{week.steps.length} steps</span>
        <button onClick={() => onOpen(week.id)}>{isResume ? "Resume" : "Open Room"}</button>
      </div>
    </article>
  );
}
