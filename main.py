from __future__ import annotations
import os, re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Literal
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

load_dotenv()
app = FastAPI(title="SANA AI | ERIX | Storm Break", version="4.0.0",
              description="Compact single-service build of SANA AI, ERIX task routing, RAG and Storm Break simulator.")
origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "*").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False,
                   allow_methods=["GET", "POST"], allow_headers=["*"])

@dataclass(frozen=True)
class AgentTask:
    id: str
    name: str
    domain: str
    description: str
    agent: str

DOMAINS = {
    "research": ("DataScout", ["web research plan", "fact extraction", "source comparison", "market scan", "literature review", "trend analysis", "entity extraction", "data summarization", "knowledge mapping", "research brief", "competitor analysis", "document classification", "question answering", "timeline building", "insight discovery", "dataset profiling", "citation checklist", "information gap analysis", "report outline", "evidence review"]),
    "analysis": ("RiskAnalyzer", ["risk assessment", "root cause analysis", "impact analysis", "scenario planning", "decision matrix", " SWOT analysis", "cost benefit analysis", "quality review", "anomaly review", "compliance checklist", "security review", "bias review", "forecast assumptions", "sensitivity analysis", "priority scoring", "failure mode analysis", "mitigation plan", "performance review", "readiness assessment", "executive summary"]),
    "operations": ("ResourceDispatcher", ["project plan", "task breakdown", "resource allocation", "schedule plan", "incident checklist", "workflow design", "process optimization", "SOP drafting", "handoff plan", "capacity plan", "deployment checklist", "release plan", "support triage", "service recovery", "inventory plan", "logistics plan", "team coordination", "status report", "escalation plan", "retrospective"]),
    "content": ("SanaCreativeAgent", ["email draft", "blog outline", "social post", "press release", "translation brief", "meeting minutes", "presentation outline", " FAQ generation", "copy editing", "tone rewrite", "lesson plan", "quiz generation", "script draft", "product description", "documentation", "proposal draft", "newsletter", "speech draft", "job description", "customer reply"]),
    "engineering": ("BuildEngineer", ["API design", "code review", "test plan", "bug triage", "database schema", "architecture review", "debug checklist", "refactoring plan", "CI configuration", "deployment review", "performance tuning", "accessibility audit", "dependency audit", "migration plan", "security hardening", "log analysis", "integration plan", "unit test design", "frontend review", "backend review"]),
    "emergency": ("StormResponseAgent", ["hazard assessment", "evacuation planning", "shelter capacity plan", "emergency communication", "resource staging", "incident command brief", "weather impact scenario", "critical infrastructure review", "medical support coordination", "recovery checklist", "public alert draft", "continuity plan", "route risk review", "utility outage response", "damage assessment", "supply distribution", "vulnerability mapping", "response prioritization", "after action report", "drill design"]),
    "knowledge": ("RAGKnowledgeAgent", ["document ingestion", "knowledge retrieval", "semantic query plan", "chunk quality review", "knowledge gap report", "document comparison", "policy lookup", "technical Q&A", "FAQ extraction", "knowledge base audit", "context assembly", "source relevance scoring", "duplicate detection", "metadata extraction", "document summarization", "answer verification", "knowledge refresh", "taxonomy design", "glossary extraction", "citation validation"]),
    "personal": ("SanaAssistantAgent", ["daily planning", "goal breakdown", "learning roadmap", "study schedule", "habit plan", "brainstorming", "decision support", "travel checklist", "budget outline", "interview practice", "career roadmap", "skill gap review", "time management", "idea evaluation", "personal productivity", "reminder wording", "checklist creation", "reflection prompts", "practice exercise", "weekly review"]),
    "data": ("DataScout", ["CSV profiling", "data cleaning plan", "metric definition", "dashboard specification", "KPI analysis", "data validation", "schema mapping", "ETL design", "data dictionary", "cohort analysis", "segmentation plan", "survey analysis", "experiment design", "sampling review", "data quality report", "chart recommendation", "SQL query plan", "pipeline monitoring", "data governance", "metric interpretation"]),
    "product": ("ProductStrategyAgent", ["user story", "acceptance criteria", "product roadmap", "feature prioritization", "persona draft", "journey mapping", "requirements brief", "MVP scope", "usability test plan", "release notes", "feedback synthesis", "product metrics", "backlog grooming", "competitive positioning", "pricing research plan", "onboarding flow", "feature risk review", "product spec", "stakeholder update", "launch checklist"]),
    "education": ("LearningAgent", ["concept explanation", "curriculum map", "flashcard set", "assessment rubric", "study guide", "tutorial outline", "practice problems", "learning objective", "reading plan", "knowledge check", "class activity", "lab exercise", "revision timetable", "misconception check", "course evaluation", "microlearning plan", "teacher guide", "student feedback", "exam blueprint", "learning summary"]),
}

class ErixUltimateOrchestrator:
    def __init__(self):
        self.tasks: list[AgentTask] = []
        for domain, (agent, templates) in DOMAINS.items():
            for i, template in enumerate(templates, 1):
                self.tasks.append(AgentTask(f"{domain}-{i:03d}", template.title(), domain,
                                            f"Assist with {template}.", agent))
        self.by_id = {t.id: t for t in self.tasks}

    def catalog(self, domain: str | None = None) -> list[dict[str, str]]:
        return [t.__dict__ for t in self.tasks if not domain or t.domain == domain]

    def route(self, message: str) -> AgentTask:
        q = message.lower()
        keywords = {
            "emergency": "emergency", "storm": "emergency", "flood": "emergency", "cyclone": "emergency", "disaster": "emergency",
            "code": "engineering", "python": "engineering", "api": "engineering", "bug": "engineering", "deploy": "engineering",
            "document": "knowledge", "rag": "knowledge", "pdf": "knowledge", "knowledge": "knowledge",
            "data": "data", "csv": "data", "dashboard": "data", "analysis": "analysis", "risk": "analysis",
            "email": "content", "write": "content", "draft": "content", "translate": "content",
            "learn": "education", "study": "education", "teach": "education", "course": "education",
            "product": "product", "feature": "product", "roadmap": "product", "research": "research", "find": "research",
        }
        domain = next((d for k, d in keywords.items() if k in q), "personal")
        return next(t for t in self.tasks if t.domain == domain)

    async def execute_workflow(self, message: str, threat_level: int = 1) -> dict[str, Any]:
        task = self.route(message)
        return {"status": "completed", "task": task.__dict__,
                "agents": [task.agent, "RiskAnalyzer", "ResourceDispatcher"],
                "threat_level": max(1, min(5, threat_level)),
                "steps": ["Request classified", "Specialist agent selected", "Risk and execution checks prepared"],
                "note": "Planning/routing output only. External actions require explicit integrations and authorization."}

class KnowledgeBase:
    def __init__(self): self.chunks: list[dict[str, Any]] = []
    def ingest(self, text: str, source: str = "manual", chunk_size: int = 900) -> dict:
        words = text.split()
        if not words: return {"added": 0, "source": source}
        added = 0
        for start in range(0, len(words), max(100, chunk_size // 6)):
            part = " ".join(words[start:start + max(100, chunk_size // 6)])
            self.chunks.append({"id": f"doc-{len(self.chunks)+1}", "source": source, "text": part})
            added += 1
        return {"added": added, "source": source, "total_chunks": len(self.chunks)}
    def search(self, query: str, top_k: int = 4) -> list[dict]:
        terms = set(re.findall(r"\w+", query.lower()))
        scored = []
        for item in self.chunks:
            tokens = re.findall(r"\w+", item["text"].lower())
            counts = Counter(tokens)
            score = sum(counts[t] for t in terms) / max(1, len(tokens) ** 0.5)
            if score: scored.append((score, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [{**item, "score": round(score, 4)} for score, item in scored[:max(1, min(10, top_k))]]

class StormBreakModule:
    def run_simulation(self, sector: str = "Sector 7", hazard: str = "cyclone", severity: int = 4) -> dict:
        severity = max(1, min(5, int(severity)))
        return {"sector": sector, "hazard": hazard, "severity": severity, "impact_index": round(severity * 1.8, 1),
                "status": "simulation_only",
                "recommended_exercise": ["Verify local authority alerts", "Map vulnerable groups", "Identify safe shelters",
                    "Prepare communication tree", "Coordinate resources through authorized responders"],
                "disclaimer": "Training simulation only. Follow official emergency services and local authorities during real incidents."}

erix, knowledge, storm = ErixUltimateOrchestrator(), KnowledgeBase(), StormBreakModule()

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    avatar_mode: Literal["cyber_pink", "desi_grace"] = "cyber_pink"
    voice_clone_enabled: bool = False
class IngestRequest(BaseModel):
    text: str = Field(min_length=1, max_length=100000)
    source: str = Field(default="manual", max_length=200)
class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=4, ge=1, le=10)
class StormRequest(BaseModel):
    sector: str = Field(default="Sector 7", max_length=100)
    hazard: str = Field(default="cyclone", max_length=100)
    severity: int = Field(default=4, ge=1, le=5)

async def gemini_answer(prompt: str, context: str = "") -> str | None:
    key = os.getenv("GEMINI_API_KEY")
    if not key: return None
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    prompt_text = f"""You are SANA, a helpful assistant. Be clear and factual. If context is supplied, prioritize it and say when it is insufficient.

Context:
{context}

User:
{prompt}"""
    body = {"contents": [{"parts": [{"text": prompt_text}]}]}
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(url, params={"key": key}, json=body)
            response.raise_for_status()
            data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=f"Gemini request failed: {type(exc).__name__}") from exc

PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SANA AI | ERIX Storm Command</title>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
*{box-sizing:border-box}html,body{margin:0;min-height:100%;background:#070914;color:#f4f5ff;font-family:Inter,system-ui,sans-serif}button,input,textarea{font:inherit}button{cursor:pointer}.shell{max-width:1200px;margin:auto;padding:28px 20px}.top{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;border-bottom:1px solid #252941;padding-bottom:20px}.brand{font-size:clamp(22px,4vw,32px);font-weight:800;letter-spacing:-1px;background:linear-gradient(90deg,#ff78c8,#9d9bff);color:transparent;background-clip:text}.sub{color:#9ba2c3;font-size:12px;margin-top:5px}.pills{display:flex;gap:8px;flex-wrap:wrap}.btn,.tab{border:1px solid #343a5b;background:#151a30;color:#e9eaff;border-radius:10px;padding:10px 13px;font-size:12px}.btn.primary,.tab.active{background:#9b3cba;border-color:#c65ce4}.gridmain{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.1fr);gap:20px;margin-top:22px}.panel{background:#101427;border:1px solid #272d49;border-radius:18px;padding:18px;min-width:0}.panel h2{font-size:14px;margin:0 0 14px;color:#e6b6ff}.chat{height:430px;display:flex;flex-direction:column}.messages{flex:1;overflow:auto;display:flex;flex-direction:column;gap:12px;padding:4px}.bubble{max-width:88%;padding:11px 13px;border-radius:13px;background:#202640;font-size:13px;line-height:1.6;white-space:pre-wrap}.bubble.user{align-self:flex-end;background:#56358e}.composer{display:flex;gap:8px;margin-top:14px}.composer input,.field{min-width:0;flex:1;background:#090d1c;color:white;border:1px solid #333a59;border-radius:10px;padding:12px;outline:none}.muted{color:#9ba2c3;font-size:12px;line-height:1.6}.statrow{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin-top:12px}.stat{background:#0b1020;border:1px solid #252b46;border-radius:12px;padding:12px}.stat strong{display:block;font-size:20px;color:#f5a5e5}.stat span{font-size:10px;color:#9ba2c3}.tabs{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:12px}.result{font-size:12px;line-height:1.6;background:#0a1020;border:1px solid #292f4c;padding:12px;border-radius:12px;margin-top:10px;white-space:pre-wrap;overflow:auto}.notice{font-size:11px;color:#f5cf8d;margin-top:12px}.avatar-wrap{height:370px;position:relative;border:1px solid #733d82;border-radius:16px;overflow:hidden;background:radial-gradient(ellipse at 50% 40%,#39204d,#101427 70%)}.avatar-label{position:absolute;top:12px;left:12px;background:#080a18bb;padding:7px 10px;border-radius:20px;font-size:11px;color:#ffc2ed}.footer{color:#69708e;font-size:11px;text-align:center;margin:24px 0}textarea.field{width:100%;resize:vertical}@media(max-width:800px){.gridmain{grid-template-columns:1fr}.chat{height:390px}.shell{padding:18px 12px}.avatar-wrap{height:310px}}
</style></head><body><main class="shell">
<header class="top"><div><div class="brand">SANA AI · ERIX · STORM BREAK</div><div class="sub">Multi-agent task router · RAG knowledge · Optional Gemini LLM · Interactive 3D avatar</div></div>
<div class="pills"><button id="pink" class="btn primary">Cyber Pink</button><button id="desi" class="btn">Desi Grace</button></div></header>
<section class="gridmain"><div><div class="avatar-wrap" id="avatar"><div class="avatar-label" id="avatarLabel">CYBER PINK · 3D DEMO</div></div>
<div class="statrow"><div class="stat"><strong id="taskCount">—</strong><span>REGISTERED TASKS</span></div><div class="stat"><strong id="backendStatus">CHECKING</strong><span>BACKEND</span></div><div class="stat"><strong id="llmMode">LOCAL</strong><span>LLM MODE</span></div></div>
<p class="notice">Voice cloning is not enabled in this build. Add a consent-based TTS provider separately; no voice is cloned by this demo.</p></div>
<div class="panel chat"><h2>LIVE SANA CHAT</h2><div class="messages" id="messages"><div class="bubble">Namaste! मी SANA AI आहे. Chat, ERIX task routing, RAG आणि Storm Break simulation वापरून पाहा.</div></div>
<form class="composer" id="chatForm"><input id="chatInput" placeholder="Ask SANA or describe a task..." autocomplete="off"><button class="btn primary" id="sendBtn">Send</button></form></div></section>
<section class="panel" style="margin-top:20px"><h2>ERIX CONTROL CENTER</h2><div class="tabs"><button class="tab active" data-tab="agents">Agent Catalog</button><button class="tab" data-tab="rag">RAG Knowledge</button><button class="tab" data-tab="storm">Storm Simulator</button></div>
<div id="agentsPanel"><p class="muted">Registered task templates are routed to specialist agents. These are task definitions, not separate autonomous LLM instances.</p><button class="btn primary" id="loadAgents">Load Agent Catalog</button></div>
<div id="ragPanel" hidden><p class="muted">Paste text to add it to the local in-memory retrieval index. Data resets when the backend restarts.</p><textarea class="field" rows="4" id="docText" placeholder="Paste a document or knowledge text..."></textarea><button class="btn primary" style="margin-top:8px" id="ingestBtn">Ingest Text</button><div class="composer"><input class="field" id="ragQuery" placeholder="Search knowledge base..."><button class="btn" id="searchBtn">Search</button></div></div>
<div id="stormPanel" hidden><p class="muted">Training simulation only. Do not use generated output for real emergency decisions.</p><button class="btn primary" id="simulateBtn">Run Cyclone Scenario</button></div>
<pre class="result" id="result" hidden></pre></section><div class="footer">SANA AI v4 · Use official emergency services for real incidents · Configure API keys server-side only</div></main>
<script type="module">
import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js";
window.THREE=THREE;
const $=id=>document.getElementById(id);let activeModel='cyber_pink',busy=false;
function bubble(text,user=false){const el=document.createElement('div');el.className='bubble'+(user?' user':'');el.textContent=text;$('messages').appendChild(el);$('messages').scrollTop=$('messages').scrollHeight;}
async function api(path,body){const opts=body?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}:{};const r=await fetch(path,opts);const d=await r.json();if(!r.ok)throw new Error(d.detail||'Backend error');return d;}
function showResult(d){$('result').hidden=false;$('result').textContent=typeof d==='string'?d:JSON.stringify(d,null,2);}
async function health(){try{const h=await api('/health');$('taskCount').textContent=h.agent_tasks;$('backendStatus').textContent='ONLINE';$('llmMode').textContent=h.llm_configured?'GEMINI':'LOCAL';}catch(e){$('backendStatus').textContent='OFFLINE';}}
$('chatForm').addEventListener('submit',async e=>{e.preventDefault();const q=$('chatInput').value.trim();if(!q||busy)return;busy=true;bubble(q,true);$('chatInput').value='';$('sendBtn').textContent='...';try{const d=await api('/api/chat',{message:q,avatar_mode:activeModel,voice_clone_enabled:false});bubble(d.response+String.fromCharCode(10,10)+'Agent: '+(d.workflow?.task?.agent||'SANA')+' · Mode: '+d.mode);}catch(err){bubble('Backend connection failed: '+err.message);}finally{busy=false;$('sendBtn').textContent='Send';}});
async function loadAgents(){try{const d=await api('/api/agents');const lines=d.tasks.slice(0,24).map(t=>t.id+' · '+t.name+' · '+t.agent).join(String.fromCharCode(10));showResult(d.count+' registered tasks across '+d.domains.length+' domains'+String.fromCharCode(10,10)+lines+String.fromCharCode(10,10)+'Showing first 24 tasks. Full catalog: GET /api/agents');}catch(e){showResult(e.message);}}
$('loadAgents').onclick=loadAgents;
$('ingestBtn').onclick=async()=>{try{showResult(await api('/api/rag/ingest',{text:$('docText').value,source:'dashboard-upload'}));}catch(e){showResult(e.message);}};
$('searchBtn').onclick=async()=>{try{showResult(await api('/api/rag/search',{query:$('ragQuery').value}));}catch(e){showResult(e.message);}};
$('simulateBtn').onclick=async()=>{try{showResult(await api('/api/storm/simulate',{sector:'Demo Sector',hazard:'cyclone',severity:4}));}catch(e){showResult(e.message);}};
document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-tab]').forEach(x=>x.classList.toggle('active',x===b));['agents','rag','storm'].forEach(t=>$(t+'Panel').hidden=t!==b.dataset.tab);});
$('pink').onclick=()=>setAvatar('cyber_pink');$('desi').onclick=()=>setAvatar('desi_grace');
function setAvatar(mode){activeModel=mode;$('pink').classList.toggle('primary',mode==='cyber_pink');$('desi').classList.toggle('primary',mode==='desi_grace');$('avatarLabel').textContent=(mode==='cyber_pink'?'CYBER PINK':'DESI GRACE')+' · 3D DEMO';initAvatar();}
let renderer,scene,camera,group,ring,raf,observer;
function initAvatar(){const host=$('avatar');if(!window.THREE){host.insertAdjacentHTML('beforeend','<div style="padding:100px 20px;text-align:center">3D preview needs internet access to load Three.js.</div>');return;}
if(raf)cancelAnimationFrame(raf);if(observer)observer.disconnect();if(renderer){renderer.dispose();renderer.domElement.remove();}
scene=new THREE.Scene();camera=new THREE.PerspectiveCamera(42,host.clientWidth/host.clientHeight,.1,100);camera.position.set(0,0,6);renderer=new THREE.WebGLRenderer({alpha:true,antialias:true});renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));renderer.setSize(host.clientWidth,host.clientHeight);renderer.domElement.style.width='100%';renderer.domElement.style.height='100%';host.appendChild(renderer.domElement);scene.add(new THREE.AmbientLight(0xffffff,1.7));const pink=activeModel==='cyber_pink';const key=new THREE.PointLight(pink?0xff55cc:0xffbb88,35);key.position.set(2,3,4);scene.add(key);group=new THREE.Group();scene.add(group);
const skin=pink?0xffb4d6:0xe7ad83,hair=pink?0xff38bd:0x24152b;const head=new THREE.Mesh(new THREE.SphereGeometry(.82,40,32),new THREE.MeshStandardMaterial({color:skin,roughness:.72}));head.position.y=.55;group.add(head);
const cap=new THREE.Mesh(new THREE.SphereGeometry(.87,40,24,0,Math.PI*2,0,Math.PI*.62),new THREE.MeshStandardMaterial({color:hair,roughness:.4,metalness:.12}));cap.position.y=.72;group.add(cap);
const body=new THREE.Mesh(new THREE.CapsuleGeometry(.62,.95,8,20),new THREE.MeshStandardMaterial({color:pink?0x8c3eaa:0x267d72,roughness:.65}));body.position.y=-.95;group.add(body);
const eyeMat=new THREE.MeshStandardMaterial({color:0x20152c});[-.3,.3].forEach(x=>{const eye=new THREE.Mesh(new THREE.SphereGeometry(.065,16,12),eyeMat);eye.position.set(x,.58,.72);group.add(eye);});
ring=new THREE.Mesh(new THREE.TorusGeometry(1.65,.018,8,100),new THREE.MeshBasicMaterial({color:pink?0xf45bd2:0x65e6cb,transparent:true,opacity:.8}));ring.rotation.x=1.15;group.add(ring);
let drag=false,lastX=0;const down=e=>{drag=true;lastX=e.clientX;renderer.domElement.setPointerCapture?.(e.pointerId)},up=()=>drag=false,move=e=>{if(drag){group.rotation.y+=(e.clientX-lastX)*.01;lastX=e.clientX;}};renderer.domElement.addEventListener('pointerdown',down);renderer.domElement.addEventListener('pointerup',up);renderer.domElement.addEventListener('pointercancel',up);renderer.domElement.addEventListener('pointermove',move);
const animate=()=>{raf=requestAnimationFrame(animate);if(!drag)group.rotation.y+=.004;group.position.y=Math.sin(Date.now()*.0012)*.07;ring.rotation.z+=.002;renderer.render(scene,camera);};animate();
const resize=()=>{const w=host.clientWidth,h=host.clientHeight;if(!w||!h)return;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h);};observer=new ResizeObserver(resize);observer.observe(host);
}
initAvatar();health();
</script></body></html>"""

@app.get("/", response_class=HTMLResponse)
def home(): return PAGE

@app.get("/health")
def health():
    return {"status": "healthy", "python_target": "3.11+", "llm_configured": bool(os.getenv("GEMINI_API_KEY")),
            "agent_tasks": len(erix.tasks), "rag_chunks": len(knowledge.chunks)}

@app.get("/api/agents")
def agents(domain: str | None = None):
    items = erix.catalog(domain)
    return {"count": len(items), "domains": list(DOMAINS), "tasks": items}

@app.post("/api/chat")
async def chat(req: ChatRequest):
    task = await erix.execute_workflow(req.message)
    docs = knowledge.search(req.message, 3)
    context = "\n\n".join(f"[{d['source']}] {d['text']}" for d in docs)
    answer = await gemini_answer(req.message, context)
    mode = "gemini_llm_rag" if answer else "local_router"
    if not answer:
        answer = (f"Namaste! मी SANA आहे. तुमची विनंती '{req.message}' साठी {task['task']['agent']} कडे route केली आहे. "
                  f"Task: {task['task']['name']}. नोंदणीकृत Agent Tasks: {len(erix.tasks)}. "
                  + (f"Knowledge base मधून {len(docs)} संबंधित भाग मिळाले." if docs else "Gemini API key दिल्यास LLM उत्तर सक्षम होईल."))
    return {"response": answer, "mode": mode, "workflow": task, "retrieved_context": docs,
            "avatar_mode": req.avatar_mode, "voice_clone": False,
            "voice_note": "Voice cloning is not implemented; use a consent-based TTS provider integration.",
            "expression": "happy"}

@app.post("/api/rag/ingest")
def rag_ingest(req: IngestRequest): return knowledge.ingest(req.text, req.source)

@app.post("/api/rag/search")
def rag_search(req: SearchRequest): return {"results": knowledge.search(req.query, req.top_k)}

@app.post("/api/storm/simulate")
def storm_simulate(req: StormRequest): return storm.run_simulation(req.sector, req.hazard, req.severity)
