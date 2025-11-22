"""Main FastAPI application for Company Research Assistant"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import os

from app.config import get_settings
from app.agent import ConversationalAgent
from app.researcher import CompanyResearcher
from app.synthesizer import DataSynthesizer
from app.account_plan import AccountPlanGenerator

# Initialize FastAPI app
app = FastAPI(
    title="Company Research Assistant",
    description="AI-powered company research and account plan generator",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize settings
settings = get_settings()

# Initialize components
agent = ConversationalAgent(
    api_key=settings.groq_api_key,
    model=settings.groq_model
)

researcher = CompanyResearcher(
    serpapi_key=settings.serpapi_key,
    max_sources=settings.max_research_sources
)

synthesizer = DataSynthesizer(
    api_key=settings.groq_api_key,
    model=settings.groq_model
)

plan_generator = AccountPlanGenerator(
    api_key=settings.groq_api_key,
    model=settings.groq_model
)

# Store active sessions
sessions: Dict[str, Dict] = {}


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    response: str
    intent: Optional[Dict] = None
    context: Optional[Dict] = None


class ResearchRequest(BaseModel):
    company_name: str
    session_id: Optional[str] = "default"


class UpdatePlanRequest(BaseModel):
    section_path: str
    new_content: Any
    session_id: Optional[str] = "default"


# Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint for conversational interaction"""
    try:
        # Get or create session
        if request.session_id not in sessions:
            sessions[request.session_id] = {
                "agent": ConversationalAgent(settings.groq_api_key, settings.groq_model),
                "context": {}
            }

        session = sessions[request.session_id]
        session_agent = session["agent"]

        # Extract intent
        intent = session_agent.extract_intent(request.message)

        # Get response with context
        response = session_agent.get_response(
            request.message,
            context=session.get("context")
        )

        return ChatResponse(
            response=response,
            intent=intent,
            context=session.get("context")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/research")
async def research_company(request: ResearchRequest):
    """Initiate company research"""
    try:
        # Conduct research
        research_data = researcher.research_company(request.company_name)

        # Synthesize findings
        synthesized = synthesizer.synthesize_research(
            research_data,
            request.company_name
        )

        # Check for conflicts
        conflicts = synthesizer.identify_conflicts(research_data)
        if conflicts:
            synthesized["potential_conflicts"] = conflicts

        # Generate summary
        summary = synthesizer.generate_summary(synthesized)

        # Store in session context
        if request.session_id not in sessions:
            sessions[request.session_id] = {
                "agent": ConversationalAgent(settings.groq_api_key, settings.groq_model),
                "context": {}
            }

        sessions[request.session_id]["context"]["research_data"] = research_data
        sessions[request.session_id]["context"]["synthesized_data"] = synthesized

        return {
            "status": "success",
            "company_name": request.company_name,
            "summary": summary,
            "synthesized_data": synthesized,
            "conflicts": conflicts,
            "total_sources": len(research_data.get("sources", []))
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-plan")
async def generate_account_plan(request: ResearchRequest):
    """Generate account plan from research data"""
    try:
        # Check if we have synthesized data
        if request.session_id not in sessions:
            raise HTTPException(
                status_code=400,
                detail="No research data found. Please conduct research first."
            )

        session = sessions[request.session_id]
        synthesized_data = session.get("context", {}).get("synthesized_data")

        if not synthesized_data:
            raise HTTPException(
                status_code=400,
                detail="No research data found. Please conduct research first."
            )

        # Generate account plan
        account_plan = plan_generator.generate_plan(
            request.company_name,
            synthesized_data
        )

        # Save plan
        filepath = plan_generator.save_plan(account_plan)

        # Store in session
        session["context"]["account_plan"] = account_plan

        # Format as text
        formatted_plan = plan_generator.format_plan_as_text(account_plan)

        return {
            "status": "success",
            "account_plan": account_plan,
            "formatted_plan": formatted_plan,
            "saved_to": filepath
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/update-plan")
async def update_plan_section(request: UpdatePlanRequest):
    """Update a specific section of the account plan"""
    try:
        if request.session_id not in sessions:
            raise HTTPException(
                status_code=400,
                detail="No active session found."
            )

        session = sessions[request.session_id]
        account_plan = session.get("context", {}).get("account_plan")

        if not account_plan:
            raise HTTPException(
                status_code=400,
                detail="No account plan found. Please generate a plan first."
            )

        # Update the section
        updated_plan = plan_generator.update_section(
            account_plan,
            request.section_path,
            request.new_content
        )

        # Save updated plan
        filepath = plan_generator.save_plan(updated_plan)

        # Update session
        session["context"]["account_plan"] = updated_plan

        # Format as text
        formatted_plan = plan_generator.format_plan_as_text(updated_plan)

        return {
            "status": "success",
            "message": f"Section '{request.section_path}' updated successfully",
            "saved_to": filepath,
            "updated_plan": updated_plan,
            "formatted_plan": formatted_plan
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/plans")
async def list_plans():
    """List all saved account plans"""
    try:
        plans = plan_generator.list_plans()
        return {
            "status": "success",
            "plans": plans,
            "total": len(plans)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/plans/{filename}")
async def get_plan(filename: str):
    """Get a specific account plan"""
    try:
        plan = plan_generator.load_plan(filename)
        formatted = plan_generator.format_plan_as_text(plan)

        return {
            "status": "success",
            "account_plan": plan,
            "formatted_plan": formatted
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Plan not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reset-session")
async def reset_session(session_id: str = "default"):
    """Reset a session"""
    if session_id in sessions:
        sessions[session_id]["agent"].reset_conversation()
        sessions[session_id]["context"] = {}

    return {"status": "success", "message": "Session reset"}


# WebSocket for real-time chat
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()

    # Initialize session if needed
    if session_id not in sessions:
        sessions[session_id] = {
            "agent": ConversationalAgent(settings.groq_api_key, settings.groq_model),
            "context": {}
        }

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)

            message = message_data.get("message", "")
            action = message_data.get("action", "chat")

            session = sessions[session_id]

            if action == "chat":
                # Get response
                response = session["agent"].get_response(
                    message,
                    context=session.get("context")
                )

                await websocket.send_json({
                    "type": "response",
                    "content": response
                })

            elif action == "research":
                company_name = message_data.get("company_name", message)

                # Send progress update
                await websocket.send_json({
                    "type": "status",
                    "content": f"Researching {company_name}..."
                })

                # Conduct research
                research_data = researcher.research_company(company_name)

                await websocket.send_json({
                    "type": "status",
                    "content": "Synthesizing findings..."
                })

                # Synthesize
                synthesized = synthesizer.synthesize_research(
                    research_data,
                    company_name
                )

                # Check conflicts
                conflicts = synthesizer.identify_conflicts(research_data)

                if conflicts:
                    await websocket.send_json({
                        "type": "conflict",
                        "content": conflicts
                    })

                # Store in context
                session["context"]["research_data"] = research_data
                session["context"]["synthesized_data"] = synthesized

                summary = synthesizer.generate_summary(synthesized)

                await websocket.send_json({
                    "type": "research_complete",
                    "content": summary,
                    "data": synthesized
                })

    except WebSocketDisconnect:
        pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    )
