"use client";

import Link from "next/link";
import { useEffect,useState } from "react";
import { addQuestion,connectWallet,createQuiz,generateSalt,getNextQuizId,getQuiz,publishQuiz,type Quiz } from "../../lib/quizambig";

type DraftQuestion={text:string;answer:string;mode:"TEXT"|"NUMERIC";criteria:string;customTime:string;useCustom:boolean};

export default function MasterPage(){
  const [wallet,setWallet]=useState("");
  const [quiz,setQuiz]=useState<Quiz|null>(null);
  const [title,setTitle]=useState(""); const [description,setDescription]=useState("");
  const [count,setCount]=useState("1"); const [duration,setDuration]=useState("300");
  const [questions,setQuestions]=useState<DraftQuestion[]>([]);
  const [q,setQ]=useState<DraftQuestion>({text:"",answer:"",mode:"TEXT",criteria:"",customTime:"",useCustom:false});
  const [busy,setBusy]=useState(false); const [message,setMessage]=useState(""); const [error,setError]=useState("");

  async function connect(){try{setWallet(await connectWallet());}catch(e){setError(e instanceof Error?e.message:String(e));}}
  async function create(){
    setBusy(true);setError("");setMessage("");
    try{
      const expected=Number(count);if(!Number.isInteger(expected)||expected<1)throw new Error("Question count must be at least 1.");
      const id=await getNextQuizId();
      await createQuiz(title,description,expected,Number(duration));
      setQuiz(await getQuiz(id));setMessage(`Quiz #${id} created on-chain. Add its questions below.`);
    }catch(e){setError(e instanceof Error?e.message:String(e));}finally{setBusy(false);}
  }
  async function add(){
    if(!quiz)return;setBusy(true);setError("");setMessage("");
    try{
      if(!q.text.trim()||!q.answer.trim()||!q.criteria.trim())throw new Error("Question, master answer, and evaluation criteria are required.");
      const salt=generateSalt();
      await addQuestion(quiz.id,q.text.trim(),q.answer,q.mode,q.criteria.trim(),Number(q.customTime||0),q.useCustom);
      setQuestions([...questions,q]);setQ({text:"",answer:"",mode:"TEXT",criteria:"",customTime:"",useCustom:false});
      setMessage("Question committed on-chain. Keep the generated salt with the master answer; it is required for later reveal.");
    }catch(e){setError(e instanceof Error?e.message:String(e));}finally{setBusy(false);}
  }
  async function publish(){
    if(!quiz)return;setBusy(true);setError("");setMessage("");
    try{await publishQuiz(quiz.id);setQuiz({...quiz,status:"PUBLISHED"});setMessage("Quiz published. Its configuration and question timing are now frozen on-chain.");}
    catch(e){setError(e instanceof Error?e.message:String(e));}finally{setBusy(false);}
  }
  return <main className="shell">
    <nav className="nav"><Link className="brand" href="/">Quizambig</Link><div className="navRight">{wallet&&<span className="wallet">{wallet.slice(0,6)}…{wallet.slice(-4)}</span>}<button className="primary" onClick={connect}>Connect wallet</button></div></nav>
    <section className="hero"><div className="eyebrow">Quiz Master</div><h1>Create a semantic quiz.</h1><p>Quizambig stores quiz configuration and protected master-answer commitments on-chain. GenLayer evaluates player meaning after the question closes.</p></section>
    {error&&<div className="error">{error}</div>}{message&&<div className="success">{message}</div>}
    {!quiz?<section className="card"><h2>1. Create quiz</h2>
      <div className="field"><label>Title (optional)</label><input value={title} onChange={e=>setTitle(e.target.value)} placeholder="e.g. General Knowledge"/></div>
      <div className="field"><label>Description (optional)</label><textarea value={description} onChange={e=>setDescription(e.target.value)}/></div>
      <div className="field"><label>Question count</label><input type="number" min="1" value={count} onChange={e=>setCount(e.target.value)}/></div>
      <div className="field"><label>Overall duration (seconds)</label><input type="number" min="1" value={duration} onChange={e=>setDuration(e.target.value)}/></div>
      <button className="primary" disabled={busy} onClick={create}>{busy?"Creating…":"Create quiz on-chain"}</button>
    </section>:<>
      <section className="card"><h2>Quiz #{quiz.id}</h2><p className="muted">{quiz.title||"Untitled"} · {quiz.question_count} questions · {quiz.overall_duration_seconds}s</p><span className="badge">{quiz.status}</span></section>
      {quiz.status==="DRAFT"&&<section className="section card"><h2>2. Add question</h2>
        <div className="field"><label>Question</label><textarea value={q.text} onChange={e=>setQ({...q,text:e.target.value})}/></div>
        <div className="field"><label>Master answer</label><input value={q.answer} onChange={e=>setQ({...q,answer:e.target.value})} /></div>
        <div className="field"><label>Answer mode</label><select value={q.mode} onChange={e=>setQ({...q,mode:e.target.value as "TEXT"|"NUMERIC"})}><option value="TEXT">TEXT</option><option value="NUMERIC">NUMERIC</option></select></div>
        <div className="field"><label>Evaluation criteria</label><textarea value={q.criteria} onChange={e=>setQ({...q,criteria:e.target.value})} placeholder="What meaning must the answer express?"/></div>
        <div className="field"><label><input type="checkbox" checked={q.useCustom} onChange={e=>setQ({...q,useCustom:e.target.checked})}/> Use custom question time</label></div>
        {q.useCustom&&<div className="field"><label>Custom time (seconds)</label><input type="number" min="1" value={q.customTime} onChange={e=>setQ({...q,customTime:e.target.value})}/></div>}
        <button className="primary" disabled={busy||questions.length>=quiz.question_count} onClick={add}>Add question on-chain</button>
        <div className="section"><h3>Added this session: {questions.length}/{quiz.question_count}</h3>{questions.map((x,i)=><div className="card" key={i}><strong>Q{i+1}: {x.text}</strong><div className="meta"><span className="badge">{x.mode}</span><span className="badge">{x.useCustom?x.customTime:"automatic"} seconds</span></div></div>)}</div>
        {questions.length===quiz.question_count&&<button className="primary" disabled={busy} onClick={publish}>Publish quiz</button>}
      </section>}
      {quiz.status==="PUBLISHED"&&<section className="section card"><h2>Published</h2><p className="muted">The quiz is frozen. Players can now join it.</p><Link className="primary" href={"/quiz/"+quiz.id}>Open player view</Link></section>}
    </>}
  </main>;
}
