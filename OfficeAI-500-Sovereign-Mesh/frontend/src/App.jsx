import React,{useEffect,useState} from 'react';
import {getHealth,getMetrics,getAgents,getTasks,dispatchTask,run500Demo,searchMemory,approveTask,rejectTask,tamperMemory,verifyMemory,loadDemo} from './api';

export default function App(){
  const [view,setView]=useState('Dashboard'); const [metrics,setMetrics]=useState({}); const [agents,setAgents]=useState([]); const [tasks,setTasks]=useState([]); const [memory,setMemory]=useState([]); const [offline,setOffline]=useState(false); const [err,setErr]=useState('');
  const refresh=async()=>{try{await getHealth(); setOffline(false); setErr(''); setMetrics(await getMetrics()); setAgents(await getAgents()); setTasks(await getTasks(50)); setMemory(await searchMemory(''));}catch(e){setOffline(true); setErr(String(e)); setAgents([{id:1,role:'fallback',status:'idle'}]);}};
  useEffect(()=>{refresh();},[]);
  const runDemo=async()=>{await loadDemo(); await run500Demo(); await refresh();};
  const quickDispatch=async()=>{await dispatchTask({type:'GENERAL',payload:{subject:'manual'},amount:10,priority:1}); await refresh();};
  const reviewTasks=tasks.filter(t=>t.status==='needs_review');
  return <div className='p-4 space-y-3'>
    <h1 className='text-2xl font-bold'>OfficeAI-500 Sovereign Mesh</h1>
    {offline && <div className='bg-red-700 p-2 rounded'>OFFLINE DEMO MODE</div>}
    {err && <div className='bg-red-900 p-2 rounded'>{err}</div>}
    <div className='flex gap-2'>{['Dashboard','Agents','Tasks','Memory','Governance'].map(v=><button key={v} className='card' onClick={()=>setView(v)}>{v}</button>)}</div>
    <div className='flex gap-2'><button className='card' onClick={refresh}>Refresh</button><button className='card' onClick={quickDispatch}>Dispatch Task</button><button className='card' onClick={runDemo}>Run 500 Demo</button></div>
    {view==='Dashboard' && <div className='grid grid-cols-3 gap-2'>{Object.entries(metrics).map(([k,v])=><div className='card' key={k}><div className='text-xs text-slate-400'>{k}</div><div>{String(v)}</div></div>)}</div>}
    {view==='Agents' && <div className='space-y-1'>{agents.map(a=><div className='card' key={a.id}>{a.id} | {a.role} | {a.status}</div>)}</div>}
    {view==='Tasks' && <div className='space-y-1'>{tasks.map(t=><div className='card' key={t.id}>{t.id} | {t.agent_id} | {t.type} | {t.status} | {t.payload} | {t.amount} | {t.trace_id}</div>)}</div>}
    {view==='Memory' && <div className='space-y-1'>{memory.map(m=><div className='card' key={m.capsule_id}>{m.capsule_id} | {m.task_type} | {m.confidence} | {m.use_count} | {String(m.verified)} <button onClick={async()=>{await tamperMemory(m.capsule_id);await refresh();}}>Tamper</button> <button onClick={async()=>{await verifyMemory(m.capsule_id);await refresh();}}>Verify</button></div>)}</div>}
    {view==='Governance' && <div className='space-y-1'>{reviewTasks.map(t=><div className='card' key={t.id}>{t.id} {t.type} <button onClick={async()=>{await approveTask(t.id);await refresh();}}>Approve</button> <button onClick={async()=>{await rejectTask(t.id);await refresh();}}>Reject</button></div>)}</div>}
  </div>
}
