from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

from app.agent.executor import run_agent

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    system_role: str
    model: Optional[str]=None
    message_content: Optional[list[dict[str, str]]]

@router.post("/chat")
async def chat(req: ChatRequest):
    result = await run_agent(req.message,
                             req.system_role,
                             req.model,
                             req.message_content)
    return {"result": result}