from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio

from services import storage
from services.llm_service import stream_agent, AGENT_LABELS

router = APIRouter()

DEBATE_AGENTS = ["scientist", "critic", "ethicist", "optimizer"]


class DebateRequest(BaseModel):
    topic: str


class DebateResponse(BaseModel):
    debate_id: str
    topic: str
    status: str


@router.post("/start", response_model=DebateResponse)
async def start_debate(req: DebateRequest):
    """Create a new debate session and return its ID."""
    if not req.topic or len(req.topic.strip()) < 10:
        raise HTTPException(status_code=400, detail="Topic must be at least 10 characters")

    record = await storage.create_debate(req.topic.strip())
    return DebateResponse(debate_id=record["id"], topic=record["topic"], status=record["status"])


@router.get("/stream/{debate_id}")
async def stream_debate(debate_id: str):
    """SSE endpoint - streams the full debate in real time."""
    topic, status = await storage.get_debate_topic(debate_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="Debate not found")
    if status == "complete":
        raise HTTPException(status_code=400, detail="Debate already completed")

    async def event_generator():
        await storage.set_debate_status(debate_id, "running")
        round_context = ""

        try:
            for round_num in range(1, 3):
                yield f"data: {json.dumps({'type': 'round_start', 'round': round_num})}\n\n"
                await asyncio.sleep(0.1)

                round_messages = []
                for agent in DEBATE_AGENTS:
                    yield f"data: {json.dumps({'type': 'agent_thinking', 'agent': agent, 'agent_label': AGENT_LABELS[agent], 'round': round_num})}\n\n"

                    full_response = ""
                    async for token in stream_agent(agent, topic, round_context):
                        full_response += token
                        yield f"data: {json.dumps({'type': 'token', 'agent': agent, 'agent_label': AGENT_LABELS[agent], 'round': round_num, 'token': token})}\n\n"

                    yield f"data: {json.dumps({'type': 'message_complete', 'agent': agent, 'agent_label': AGENT_LABELS[agent], 'round': round_num, 'content': full_response})}\n\n"

                    await storage.save_message(debate_id, agent, round_num, full_response)
                    round_messages.append(f"{AGENT_LABELS[agent]}: {full_response}")
                    await asyncio.sleep(0.3)

                round_context += f"\n\nRound {round_num}:\n" + "\n\n".join(round_messages)

            yield f"data: {json.dumps({'type': 'round_start', 'round': 3, 'label': 'Consensus'})}\n\n"
            yield f"data: {json.dumps({'type': 'agent_thinking', 'agent': 'consensus', 'agent_label': AGENT_LABELS['consensus'], 'round': 3})}\n\n"

            consensus_text = ""
            async for token in stream_agent("consensus", topic, round_context):
                consensus_text += token
                yield f"data: {json.dumps({'type': 'token', 'agent': 'consensus', 'agent_label': AGENT_LABELS['consensus'], 'round': 3, 'token': token})}\n\n"

            yield f"data: {json.dumps({'type': 'message_complete', 'agent': 'consensus', 'agent_label': AGENT_LABELS['consensus'], 'round': 3, 'content': consensus_text})}\n\n"

            await storage.save_message(debate_id, "consensus", 3, consensus_text)
            await storage.set_debate_status(debate_id, "complete")

            yield f"data: {json.dumps({'type': 'debate_complete', 'debate_id': debate_id})}\n\n"

        except Exception as e:
            await storage.set_debate_status(debate_id, "error")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
