from fastapi import APIRouter, HTTPException
from services import storage
from services.llm_service import AGENT_LABELS

router = APIRouter()


@router.get("/")
async def list_debates(limit: int = 20):
    """List recent debates with message counts."""
    return await storage.list_debates(limit)


@router.get("/{debate_id}")
async def get_debate(debate_id: str):
    """Get a full debate with all its messages."""
    debate = await storage.get_debate_full(debate_id)
    if not debate:
        raise HTTPException(status_code=404, detail="Debate not found")

    # Attach friendly agent labels
    for m in debate["messages"]:
        m["agent_label"] = AGENT_LABELS.get(m["agent"], m["agent"])
    return debate
