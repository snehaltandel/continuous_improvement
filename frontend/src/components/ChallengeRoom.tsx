import { useEffect, useMemo, useState } from "react";

import { assistStep, getWeekSubmissions, submitStep } from "../services/api";
import type { Score, Submission, Week } from "../types";


interface ChallengeRoomProps {
  week: Week;
  onBack: () => void;
  onRefreshDashboard: () => Promise<void>;
}


export function ChallengeRoom({ week, onBack, onRefreshDashboard }: ChallengeRoomProps) {
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [scores, setScores] = useState<Score[]>([]);
  const [currentStepNumber, setCurrentStepNumber] = useState(1);
  const [draftText, setDraftText] = useState("");
  const [notes, setNotes] = useState("");
  const [aiText, setAiText] = useState("");
  const [aiExplanation, setAiExplanation] = useState("");
  const [finalText, setFinalText] = useState("");
  const [reviewConfirmed, setReviewConfirmed] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [isWorking, setIsWorking] = useState(false);

  useEffect(() => {
    void (async () => {
      const result = await getWeekSubmissions(week.id);
      setSubmissions(result.submissions);
      setScores(result.scores);
      const completed = new Set(result.submissions.map((item) => item.step_number));
      const nextStep = week.steps.find((step) => !completed.has(step.step_number));
      setCurrentStepNumber(nextStep?.step_number ?? week.steps[week.steps.length - 1].step_number);

      const stepOne = result.submissions.find((item) => item.step_number === 1);
      const stepTwo = result.submissions.find((item) => item.step_number === 2);
      const stepThree = result.submissions.find((item) => item.step_number === 3);

      setDraftText(stepOne?.raw_user_input ?? "");
      setNotes(stepOne?.opportunity_notes ?? "");
      setAiText(stepTwo?.ai_generated_output ?? "");
      setAiExplanation(stepTwo?.ai_explanation ?? "");
      setFinalText(stepThree?.final_user_submission ?? stepTwo?.ai_generated_output ?? "");
      setReviewConfirmed(stepThree?.user_review_confirmed ?? false);
    })();
  }, [week.id, week.steps]);

  const currentStep = useMemo(
    () => week.steps.find((step) => step.step_number === currentStepNumber) ?? week.steps[0],
    [currentStepNumber, week.steps],
  );

  const scoreByStep = useMemo(() => {
    const scoreMap = new Map<number, Score>();
    scores.forEach((score) => {
      const current = scoreMap.get(score.step_number);
      if (!current || new Date(score.scored_at) > new Date(current.scored_at)) {
        scoreMap.set(score.step_number, score);
      }
    });
    return scoreMap;
  }, [scores]);

  async function refreshWeekState() {
    const result = await getWeekSubmissions(week.id);
    setSubmissions(result.submissions);
    setScores(result.scores);
    await onRefreshDashboard();
  }

  async function handleStepOneSubmit() {
    setIsWorking(true);
    setStatusMessage(null);
    try {
      await submitStep(week.id, currentStep.id, {
        submission_type: "draft",
        raw_user_input: draftText,
        opportunity_notes: notes,
      });
      setCurrentStepNumber(2);
      setStatusMessage("Step 1 submitted.");
      await refreshWeekState();
    } catch (error) {
      setStatusMessage(error instanceof Error ? error.message : "Step 1 submission failed.");
    } finally {
      setIsWorking(false);
    }
  }

  async function handleAiAssist() {
    setIsWorking(true);
    setStatusMessage(null);
    try {
      const result = await assistStep(week.id, currentStep.id, {
        raw_user_input: draftText,
        opportunity_notes: notes,
      });
      setAiText(result.refined_text);
      setAiExplanation(`${result.explanation} ${result.suggestions}`);
      setFinalText(result.refined_text);
      setStatusMessage("AI refinement generated.");
    } catch (error) {
      setStatusMessage(error instanceof Error ? error.message : "AI assist failed.");
    } finally {
      setIsWorking(false);
    }
  }

  async function handleStepTwoSubmit() {
    setIsWorking(true);
    setStatusMessage(null);
    try {
      await submitStep(week.id, currentStep.id, {
        submission_type: "ai-assisted",
        raw_user_input: draftText,
        opportunity_notes: notes,
        ai_generated_output: aiText,
        ai_explanation: aiExplanation,
      });
      setCurrentStepNumber(3);
      setStatusMessage("Step 2 submitted.");
      await refreshWeekState();
    } catch (error) {
      setStatusMessage(error instanceof Error ? error.message : "Step 2 submission failed.");
    } finally {
      setIsWorking(false);
    }
  }

  async function handleStepThreeSubmit() {
    setIsWorking(true);
    setStatusMessage(null);
    try {
      await submitStep(week.id, currentStep.id, {
        submission_type: "final",
        raw_user_input: draftText,
        opportunity_notes: notes,
        ai_generated_output: aiText,
        ai_explanation: aiExplanation,
        final_user_submission: finalText,
        user_review_confirmed: reviewConfirmed,
        was_user_edited: finalText.trim() !== aiText.trim(),
      });
      setStatusMessage("Final submission saved.");
      await refreshWeekState();
    } catch (error) {
      setStatusMessage(error instanceof Error ? error.message : "Final submission failed.");
    } finally {
      setIsWorking(false);
    }
  }

  return (
    <section className="challenge-room">
      <button className="ghost-button" onClick={onBack}>
        Back to dashboard
      </button>

      <div className="challenge-room__header">
        <div>
          <div className="eyebrow">Week {week.week_number}</div>
          <h1>
            {week.theme}: {week.scenario_title}
          </h1>
          <p>{week.scenario_narrative}</p>
        </div>
        <div className="orbital-card">
          <span>Current step</span>
          <strong>
            {currentStep.step_number}. {currentStep.step_name}
          </strong>
        </div>
      </div>

      <div className="challenge-layout">
        <aside className="panel panel--dense">
          <h2>Clues</h2>
          <ul className="clean-list">
            {week.clue_panel.map((clue) => (
              <li key={clue}>{clue}</li>
            ))}
          </ul>

          <h2>Step Tracker</h2>
          <div className="step-tracker">
            {week.steps.map((step) => (
              <button
                className={`step-chip ${step.step_number === currentStepNumber ? "step-chip--active" : ""}`}
                key={step.id}
                onClick={() => setCurrentStepNumber(step.step_number)}
                type="button"
              >
                Step {step.step_number}
              </button>
            ))}
          </div>

          <h2>Score Snapshot</h2>
          {week.steps.map((step) => {
            const score = scoreByStep.get(step.step_number);
            return (
              <div className="score-row" key={step.id}>
                <span>{step.step_name}</span>
                <strong>{score ? `${score.awarded_points}/${score.max_points}` : `0/${step.max_points}`}</strong>
              </div>
            );
          })}
        </aside>

        <main className="panel">
          <div className="panel__header">
            <div>
              <div className="eyebrow">Instructions</div>
              <h2>{currentStep.step_name}</h2>
            </div>
            <span className="panel__meta">{currentStep.max_points} points</span>
          </div>
          <p>{currentStep.instructions}</p>

          <div className="prompt-grid">
            {currentStep.guidance_prompts.map((prompt) => (
              <div className="prompt-card" key={prompt}>
                {prompt}
              </div>
            ))}
          </div>

          {currentStep.step_number === 1 && (
            <div className="editor-stack">
              <label>
                Problem statement draft
                <textarea value={draftText} onChange={(event) => setDraftText(event.target.value)} rows={6} />
              </label>
              <label>
                Improvement opportunity notes
                <textarea value={notes} onChange={(event) => setNotes(event.target.value)} rows={4} />
              </label>
              <button disabled={isWorking || !draftText.trim()} onClick={handleStepOneSubmit}>
                Submit Step 1
              </button>
            </div>
          )}

          {currentStep.step_number === 2 && (
            <div className="editor-stack">
              <label>
                User draft
                <textarea value={draftText} onChange={(event) => setDraftText(event.target.value)} rows={5} />
              </label>
              <button disabled={isWorking || !draftText.trim()} onClick={handleAiAssist}>
                Generate AI refinement
              </button>
              <label>
                AI-assisted version
                <textarea value={aiText} onChange={(event) => setAiText(event.target.value)} rows={6} />
              </label>
              <label>
                AI explanation
                <textarea value={aiExplanation} onChange={(event) => setAiExplanation(event.target.value)} rows={4} />
              </label>
              <button disabled={isWorking || !aiText.trim()} onClick={handleStepTwoSubmit}>
                Submit Step 2
              </button>
            </div>
          )}

          {currentStep.step_number === 3 && (
            <div className="editor-stack">
              <label>
                AI draft for review
                <textarea value={aiText} readOnly rows={5} />
              </label>
              <label>
                Final human-reviewed submission
                <textarea value={finalText} onChange={(event) => setFinalText(event.target.value)} rows={7} />
              </label>
              <label className="checkbox-row">
                <input
                  checked={reviewConfirmed}
                  onChange={(event) => setReviewConfirmed(event.target.checked)}
                  type="checkbox"
                />
                I reviewed the AI output before final submission.
              </label>
              <button disabled={isWorking || !finalText.trim() || !reviewConfirmed} onClick={handleStepThreeSubmit}>
                Submit Final Step
              </button>
            </div>
          )}

          {statusMessage && <div className="status-banner">{statusMessage}</div>}
        </main>
      </div>
    </section>
  );
}
