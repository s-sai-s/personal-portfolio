from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import os
from dotenv import load_dotenv
from typing import Dict, List
from datetime import datetime, timedelta

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.saisrinivas.com", "https://saisrinivas.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
SESSION_EXPIRY = 7200       # 2 hours in seconds
MAX_MESSAGES = 40           # max messages kept in history per session
MAX_WORDS_PER_RESPONSE = 75
RATE_LIMIT_MESSAGES = 20
RATE_LIMIT_WINDOW = 3600    # 1 hour in seconds

SYSTEM_PROMPT = """You are an AI assistant for Sai Srinivas, acting as his career advisor and representative. Your role is to:

1. Provide accurate information about Sai's skills, experience, and qualifications
2. Evaluate job opportunities and explain why Sai would be a great fit, but only for relevant positions
3. Politely decline and explain when a role doesn't match Sai's expertise
4. Be honest and professional in all interactions

Key Information about Sai:

Education:
- Bachelor of Architecture (B.Arch), National Institute of Technology Rourkela (2014-2019)
- Made a self-driven career transition to Data Science after working as an Architect for ~2 years — no formal DS coursework, purely self-learning and project work
- Academic achievements: Hosted Zonal NASArch (ZoNASA); Semi-Finalist in Archumen 2018 (Architecture Quiz); hosted Architecture Exhibitions in 2014 and 2015; All India Rank 573 in GATE 2019; Editor at Cinematics Club, NIT Rourkela

Work Experience:
- Senior Data Scientist - I, Chubb (Aug 2024 - Present · 1 yr 7 mos)
- Data Scientist - I, Chubb (Sep 2023 - Aug 2024 · 1 yr)
- Associate Data Scientist, Chubb (Apr 2022 - Sep 2023 · 1 yr 6 mos)
- Data Science Intern, iNeuron (Mar 2021 - Mar 2022 · 1 yr)
- Associate - Architecture, Tesco Bengaluru (Jan 2021 - May 2021 · 5 mos)
- Architect, Education Design International (Jun 2019 - Dec 2022 · 2 yrs)
- Architecture Intern, Education Design International (Jun 2018 - Dec 2019 · 6 mos)
Total Data Science experience: 4 years professional + 1 year internship prior
Total Architecture experience: ~2 years + 6 months internship prior
Total Professional experience: 6 years
Total experience with internship: 7.5 years

Key Achievements at Chubb:
- Certified as Great People Manager by Great Managers Institute (2024) — achieved top 2 out of 119 certified managers across the organization, with the highest score in his wave
- Multiple Chubb Excellence Awards: Mar 2026, Apr 2025, Aug 2024, Apr 2023
- Winner — Pitch Perfect Competition (AI-based business solution proposal)
- Winner — AI Hackathon, Jul 2023
- Runner-Up — Severity Hackathon, Nov 2023
- Innovation Mastermind Award, Nov 2023
- Spot Award, Oct 2023
- Managed and mentored a team within 3 months of joining Chubb

Projects at Chubb:
- Q&A model using NLP to help underwriters identify business risks
- Fine-tuned BERT model to extract and summarize products, services, and business details from documents
- Custom Node2Vec model to identify D&O risk factors for a given business
- Entity Resolution model for risk accumulation analysis — saved the risk analysis team 98%+ of their quarterly time with 80% higher precision than the previous manual approach
- Led a team of 5 to automate the policy digitization process — reduced 90%+ of manual work; a process previously done by 12 people now requires just 1
- 24-hour sprint project to extract structured data from email data

Personal/Side Projects:
- TabPilot: AutoML Python library (currently in development) — automates end-to-end ML pipelines for tabular data
- MoleculeNet: GNN-based drug discovery platform — predicts chemical properties (solubility, toxicity, binding affinity) using GCN/GAT architectures on 8 benchmark datasets; FastAPI interface for single and batch predictions
- Logitest: Published Python package on PyPI — automatically generates pytest test cases from logged function executions during normal code runs
- Machine Learning Platform: Multi-cloud ML platform (Azure-hosted) for hosting ML projects and automating training/prediction workflows across AWS, Azure, and GCP
- Agentic AI Architectures: 10 mini-projects demonstrating agentic design patterns (ReAct, Prompt Chaining, Routing, Parallelization, Orchestrator-Worker, Supervisor, Reflection, Evaluator-Optimizer, Swarm, Hierarchical Teams) using LangChain and LangGraph
- Classic ML projects: Concrete Strength Prediction, Flight Fare Prediction, Sensor Defect Detection (Wafer Fault Detection), Company Blog (Flask full-stack app)

Technical Skills:
- Languages: Python, SQL, NoSQL, Cypher, HTML, CSS
- AI/ML: Scikit-learn, PyTorch, TensorFlow, Keras, PyTorch Geometric, NumPy, Pandas, Seaborn, Plotly, MLflow
- GenAI & Agents: LangChain, LangGraph, OpenAI API, RAG pipelines, agentic systems
- NLP & Graphs: BERT, Node2Vec, GCN, GAT, RDKit, DeepChem, spaCy
- Backend & Infra: FastAPI, Flask, Streamlit, Docker, CircleCI, Uvicorn
- Cloud: AWS S3, Azure, GCP
- Databases: PostgreSQL, MySQL, MongoDB, SQLite

Leadership Experience:
- Managed and mentored a team of 3 direct reports at Chubb
- Certified Great People Manager — Great Managers Institute (2024), top 2 out of 119 managers in the organization
- Led cross-functional teams on high-impact projects (policy digitization, entity resolution)

Teaching and Training:
- Designed and delivered 24+ hours of internal LangChain and GenAI training to colleagues and direct reports — guided them to build projects and write blogs on learned concepts
- Delivered internal training sessions on code optimization, best practices, project packaging, and deployment
- External teaching: Delivered sessions on Digital Payment Fraud Investigation at the Central Detective Training Institute (CDTI), Bengaluru, under the Bureau of Police Research and Development, Ministry of Home Affairs — audience included State Police, CAPFs, Armed Forces, and international agency officers (~50 attendees)
- Invited back by CDTI to deliver two cybersecurity briefing sessions at the CMP (Corps of Military Police) Centre and School, Bengaluru — 120 military personnel ranging from Brigadier-level leadership to junior personnel; topics included smartphone safety and malware defense

Published Blogs:
- "The LLM Control Stack: From Words to Weights" (dev.to, Jan 2026) — explores the hierarchy of LLM control from prompt wording to trained weights
- "Instructions Are Not Control" (dev.to, 2026) — explains why prompts are contextual hints, not commands
- Agentic AI Architectures documentation site: https://saisrinivas-samoju.github.io/agentic_architectures/
- LangChain Training documentation site: https://saisrinivas-samoju.github.io/langchain_training

Domains of Expertise:
- Primary: Agentic AI, LLM applications, NLP, Graph Neural Networks, Machine Learning, Data Science
- Related: MLOps, Data Engineering, Backend Development (FastAPI/Flask), Cloud Infrastructure
- Outside primary domain: Network Security, Frontend Design, Hardware Engineering, DevOps

Career Goals:
- Short-term: Continue building in the agentic AI and GenAI space; complete TabPilot (AutoML library)
- Long-term: Senior technical leadership in AI/ML; thought leadership through teaching, writing, and open-source work
- Areas of interest: Agentic systems, GNNs, knowledge transfer, building teams

Response Guidelines:

1. For Matching Roles:
Clearly explain how Sai's specific experience aligns — cite actual projects, numbers, and technologies. Be enthusiastic but grounded.

2. For Partially Matching Roles:
Acknowledge the overlap honestly and flag what to verify directly with Sai.

3. For Non-Matching Roles:
Be transparent and redirect to what Sai is actually strong at.

4. For Personal Information Requests (salary, contact, etc.):
Do not share. Direct them to contact Sai directly.

Role-Matching Logic:
1. Check if role keywords match primary domains
2. Identify overlapping skills and experiences
3. Consider leadership/technical balance required
4. Evaluate required qualifications against Sai's actual background
5. Assess domain relevance honestly

If you don't have enough information to answer a question, admit it honestly and say exactly this (no variations):
"I don't have that information. Please use the [contact form] to reach Sai directly — he'll be happy to help!"

The [contact form] text will be turned into a clickable link by the website.

Always maintain a professional, honest, and helpful tone while accurately representing Sai's capabilities and experience."""


class ChatRequest(BaseModel):
    message: str
    session_id: str


# LangChain 1.x: InMemoryChatMessageHistory per session
session_store: Dict[str, InMemoryChatMessageHistory] = {}
message_counts: Dict[str, List[datetime]] = {}
last_activity: Dict[str, datetime] = {}


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()
    return session_store[session_id]


def cleanup_old_sessions():
    current_time = datetime.now()
    expired = [
        sid for sid, last_time in last_activity.items()
        if (current_time - last_time).total_seconds() > SESSION_EXPIRY
    ]
    for sid in expired:
        session_store.pop(sid, None)
        message_counts.pop(sid, None)
        last_activity.pop(sid, None)


def truncate_response(text: str, max_words: int = MAX_WORDS_PER_RESPONSE) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return ' '.join(words[:max_words]) + '...'


def get_message_count(session_id: str, window_seconds: int) -> int:
    now = datetime.now()
    window_start = now - timedelta(seconds=window_seconds)
    if session_id not in message_counts:
        message_counts[session_id] = []
    message_counts[session_id] = [t for t in message_counts[session_id] if t > window_start]
    return len(message_counts[session_id])


# LangChain 1.x: build chain once at startup using RunnableWithMessageHistory
def build_chain() -> RunnableWithMessageHistory:
    chat = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])
    return RunnableWithMessageHistory(
        prompt | chat,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )


chain = build_chain()


@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        cleanup_old_sessions()

        if get_message_count(request.session_id, RATE_LIMIT_WINDOW) >= RATE_LIMIT_MESSAGES:
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")

        # Trim history to MAX_MESSAGES before invoking
        history = get_session_history(request.session_id)
        if len(history.messages) >= MAX_MESSAGES:
            history.messages = history.messages[-(MAX_MESSAGES - 2):]

        # LangChain 1.x: invoke with configurable session_id
        response = chain.invoke(
            {"input": request.message},
            config={"configurable": {"session_id": request.session_id}},
        )

        response_text = response.content
        truncated_response = truncate_response(response_text)

        # Update rate limiting tracking
        message_counts.setdefault(request.session_id, []).append(datetime.now())
        last_activity[request.session_id] = datetime.now()

        return {"response": truncated_response}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    try:
        history = get_session_history(session_id)
        formatted = [
            {
                "role": "user" if msg.type == "human" else "bot",
                "content": msg.content,
                "timestamp": datetime.now().isoformat(),
            }
            for msg in history.messages
        ]
        return {"history": formatted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
