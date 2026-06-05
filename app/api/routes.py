from fastapi import APIRouter
from pydantic import BaseModel

from app.agent.executor import run_agent

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat(req: ChatRequest):
    result = await run_agent(req.message)
    return {"result": result}