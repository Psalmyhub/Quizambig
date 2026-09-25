"use client";

import Link from "next/link";
import { useState } from "react";
import {
  addQuestion,
  closeQuestion,
  connectWallet,
  createQuiz,
  evaluateSubmission,
  generateSalt,
  getNextQuestionId,
  getNextQuizId,
  getQuestion,
  getQuiz,
  publishQuiz,
  revealMasterAnswer,
  startQuestion,
  type Question,
  type Quiz,
} from "../../lib/quizambig";

type DraftQuestion = {
  text: string;
  answer: string;
  salt: string;
  mode: "TEXT" | "NUMERIC";
  criteria: string;
  customTime: string;
  useCustom: boolean;
};

export default function MasterPage() {
  const [wallet, setWallet] = useState("");
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [count, setCount] = useState("1");
  const [duration, setDuration] = useState("300");
  const [questions, setQuestions] = useState<DraftQuestion[]>([]);
  const [q, setQ] = useState<DraftQuestion>({
    text: "",
    answer: "",
    salt: "",
    mode: "TEXT",
    criteria: "",
    customTime: "",
    useCustom: false,
  });
  const [activeQuestion, setActiveQuestion] = useState<Question | null>(null);
  const [masterAnswer, setMasterAnswer] = useState("");
  const [masterSalt, setMasterSalt] = useState("");
  const [player, setPlayer] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function connect() {
    try {
      setWallet(await connectWallet());
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  async function create() {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const expected = Number(count);
      if (!Number.isInteger(expected) || expected < 1) {
        throw new Error("Question count must be at least 1.");
      }
      const id = await getNextQuizId();
      await createQuiz(title, description, expected, Number(duration));
      setQuiz(await getQuiz(id));
      setMessage(`Quiz #${id} created on-chain. Add its questions below.`);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function add() {
    if (!quiz) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      if (!q.text.trim() || !q.answer.trim() || !q.criteria.trim()) {
        throw new Error("Question, master answer, and evaluation criteria are required.");
      }
      const salt = generateSalt();
      await addQuestion(
        quiz.id,
        q.text.trim(),
        q.answer,
        salt,
        q.mode,
        q.criteria.trim(),
        Number(q.customTime || 0),
        q.useCustom,
      );
      setQuestions([...questions, { ...q, salt }]);
      setQ({
        text: "",
        answer: "",
        salt: "",
        mode: "TEXT",
        criteria: "",
        customTime: "",
        useCustom: false,
      });
      setMessage("Question committed on-chain. Keep the generated salt with the master answer; it is required for later reveal.");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function loadActiveQuestion() {
    if (!quiz) return;
    setBusy(true);
    setError("");
    try {
      const next = await getNextQuestionId();
      for (let id = 1; id < next; id++) {
        try {
          const candidate = await getQuestion(id);
          if (Number(candidate.quiz_id) === quiz.id) {
            setActiveQuestion(candidate);
            return;
          }
        } catch {}
      }
      throw new Error("No question found for this quiz.");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function masterAction(action: "start" | "close" | "reveal" | "evaluate") {
    if (!activeQuestion) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      if (action === "start") await startQuestion(activeQuestion.id);
      if (action === "close") await closeQuestion(activeQuestion.id);
      if (action === "reveal") {
        if (!masterAnswer.trim() || !masterSalt.trim()) {
          throw new Error("Master answer and original salt are required for verified reveal.");
        }
        await revealMasterAnswer(activeQuestion.id, masterAnswer, masterSalt);
      }
      if (action === "evaluate") {
        if (!player.trim()) throw new Error("Enter the player's wallet address.");
        await evaluateSubmission(activeQuestion.id, player.trim() as `0x${string}`);
      }
      await loadActiveQuestion();
      setMessage("Transaction confirmed by GenLayer.");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function publish() {
    if (!quiz) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await publishQuiz(quiz.id);
      setQuiz({ ...quiz, status: "PUBLISHED" });
      setMessage("Quiz published. Its configuration and question timing are now frozen on-chain.");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="shell">
      <nav className="nav">
        <Link className="brand" href="/">Quizambig</Link>
        <div className="navRight">
          {wallet && <span className="wallet">{wallet.slice(0, 6)}…{wallet.slice(-4)}</span>}
          <button className="primary" onClick={connect}>Connect wallet</button>
        </div>
      </nav>

      <section className="hero">
        <div className="eyebrow">Quiz Master</div>
        <h1>Create a semantic quiz.</h1>
        <p>Quizambig stores quiz configuration and protected master-answer commitments on-chain. GenLayer evaluates player meaning after the question closes.</p>
      </section>

      {error && <div className="error">{error}</div>}
      {message && <div className="success">{message}</div>}

      {!quiz ? (
        <section className="card">
          <h2>1. Create quiz</h2>
          <div className="field"><label>Title (optional)</label><input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. General Knowledge" /></div>
          <div className="field"><label>Description (optional)</label><textarea value={description} onChange={(e) => setDescription(e.target.value)} /></div>
          <div className="field"><label>Question count</label><input type="number" min="1" value={count} onChange={(e) => setCount(e.target.value)} /></div>
          <div className="field"><label>Overall duration (seconds)</label><input type="number" min="1" value={duration} onChange={(e) => setDuration(e.target.value)} /></div>
          <button className="primary" disabled={busy} onClick={create}>{busy ? "Creating…" : "Create quiz on-chain"}</button>
        </section>
      ) : (
        <>
          <section className="card">
            <h2>Quiz #{quiz.id}</h2>
            <p className="muted">{quiz.title || "Untitled"} · {quiz.question_count} questions · {quiz.overall_duration_seconds}s</p>
            <span className="badge">{quiz.status}</span>
          </section>

          {quiz.status === "DRAFT" && (
            <section className="section card">
              <h2>2. Add question</h2>
              <div className="field"><label>Question</label><textarea value={q.text} onChange={(e) => setQ({ ...q, text: e.target.value })} /></div>
              <div className="field"><label>Master answer</label><input value={q.answer} onChange={(e) => setQ({ ...q, answer: e.target.value })} /></div>
              <div className="field"><label>Answer mode</label><select value={q.mode} onChange={(e) => setQ({ ...q, mode: e.target.value as "TEXT" | "NUMERIC" })}><option value="TEXT">TEXT</option><option value="NUMERIC">NUMERIC</option></select></div>
              <div className="field"><label>Evaluation criteria</label><textarea value={q.criteria} onChange={(e) => setQ({ ...q, criteria: e.target.value })} placeholder="What meaning must the answer express?" /></div>
              <div className="field"><label><input type="checkbox" checked={q.useCustom} onChange={(e) => setQ({ ...q, useCustom: e.target.checked })} /> Use custom question time</label></div>
              {q.useCustom && <div className="field"><label>Custom time (seconds)</label><input type="number" min="1" value={q.customTime} onChange={(e) => setQ({ ...q, customTime: e.target.value })} /></div>}
              <button className="primary" disabled={busy || questions.length >= quiz.question_count} onClick={add}>Add question on-chain</button>

              <div className="section">
                <h3>Added this session: {questions.length}/{quiz.question_count}</h3>
                {questions.map((x, i) => (
                  <div className="card" key={i}>
                    <strong>Q{i + 1}: {x.text}</strong>
                    <div className="meta"><span className="badge">{x.mode}</span><span className="badge">{x.useCustom ? x.customTime : "automatic"} seconds</span></div>
                  </div>
                ))}
              </div>

              {questions.length === quiz.question_count && <button className="primary" disabled={busy} onClick={publish}>Publish quiz</button>}
            </section>
          )}

          {quiz.status === "PUBLISHED" && (
            <section className="section card">
              <h2>Control panel</h2>
              <p className="muted">Load a question to manage its on-chain lifecycle. Master answer verification happens on-chain; the frontend never decides correctness.</p>
              <button className="secondary" disabled={busy} onClick={loadActiveQuestion}>Load question</button>

              {activeQuestion && (
                <div className="section">
                  <div className="meta">
                    <span className="badge">Question #{activeQuestion.id}</span>
                    <span className="badge">{activeQuestion.status}</span>
                    <span className="badge">{activeQuestion.final_time}s</span>
                    {activeQuestion.answer_revealed && <span className="badge">Answer revealed</span>}
                  </div>
                  <div className="question">{activeQuestion.question_text}</div>
                  {activeQuestion.status === "PUBLISHED" && <button className="primary" disabled={busy} onClick={() => void masterAction("start")}>Start question</button>}
                  {activeQuestion.status === "ACTIVE" && <button className="primary" disabled={busy} onClick={() => void masterAction("close")}>Close question</button>}
                  {activeQuestion.status === "CLOSED" && !activeQuestion.answer_revealed && (
                    <>
                      <div className="field"><label>Master answer</label><input value={masterAnswer} onChange={(e) => setMasterAnswer(e.target.value)} /></div>
                      <div className="field"><label>Original salt</label><input value={masterSalt} onChange={(e) => setMasterSalt(e.target.value)} /></div>
                      <button className="primary" disabled={busy} onClick={() => void masterAction("reveal")}>Verify & reveal answer</button>
                    </>
                  )}
                  {activeQuestion.answer_revealed && (
                    <>
                      <div className="field"><label>Player wallet to evaluate</label><input value={player} onChange={(e) => setPlayer(e.target.value)} placeholder="0x…" /></div>
                      <button className="primary" disabled={busy || !player.trim()} onClick={() => void masterAction("evaluate")}>Run GenLayer evaluation</button>
                    </>
                  )}
                </div>
              )}

              <div className="actions"><Link className="secondary" href={"/quiz/" + quiz.id}>Open player view</Link></div>
            </section>
          )}
        </>
      )}
    </main>
  );
}
