"""
Storage layer that works with OR without a database.

- If USE_DATABASE is true (default locally), debates persist to SQLite/PostgreSQL.
- If USE_DATABASE is false (e.g. on free Render), debates are kept in memory only.
  Live debates work identically; only long-term History persistence differs.
"""
import os
import uuid
from datetime import datetime, timezone

# Persist to a database locally, but allow turning it off for stateless cloud hosting.
USE_DATABASE = os.getenv("USE_DATABASE", "true").lower() in ("1", "true", "yes")

# ── In-memory fallback store ───────────────────────────────────────
_mem_debates = {}   # debate_id -> dict
_mem_messages = {}  # debate_id -> list[dict]


def _now():
    return datetime.now(timezone.utc)


async def create_debate(topic: str) -> dict:
    debate_id = str(uuid.uuid4())
    record = {
        "id": debate_id,
        "topic": topic,
        "status": "pending",
        "created_at": _now(),
        "completed_at": None,
    }
    if USE_DATABASE:
        from db.database import AsyncSessionLocal
        from models.models import Debate
        async with AsyncSessionLocal() as db:
            d = Debate(id=debate_id, topic=topic, status="pending")
            db.add(d)
            await db.commit()
    else:
        _mem_debates[debate_id] = record
        _mem_messages[debate_id] = []
    return record


async def get_debate_topic(debate_id: str):
    if USE_DATABASE:
        from db.database import AsyncSessionLocal
        from models.models import Debate
        from sqlalchemy import select
        async with AsyncSessionLocal() as db:
            res = await db.execute(select(Debate).where(Debate.id == debate_id))
            d = res.scalar_one_or_none()
            return (d.topic, d.status) if d else (None, None)
    else:
        d = _mem_debates.get(debate_id)
        return (d["topic"], d["status"]) if d else (None, None)


async def set_debate_status(debate_id: str, status: str):
    if USE_DATABASE:
        from db.database import AsyncSessionLocal
        from models.models import Debate
        from sqlalchemy import select
        async with AsyncSessionLocal() as db:
            res = await db.execute(select(Debate).where(Debate.id == debate_id))
            d = res.scalar_one_or_none()
            if d:
                d.status = status
                if status == "complete":
                    d.completed_at = _now()
                await db.commit()
    else:
        if debate_id in _mem_debates:
            _mem_debates[debate_id]["status"] = status
            if status == "complete":
                _mem_debates[debate_id]["completed_at"] = _now()


async def save_message(debate_id: str, agent: str, round_num: int, content: str):
    if USE_DATABASE:
        from db.database import AsyncSessionLocal
        from models.models import DebateMessage
        async with AsyncSessionLocal() as db:
            db.add(DebateMessage(
                debate_id=debate_id, agent=agent,
                round_num=round_num, content=content
            ))
            await db.commit()
    else:
        _mem_messages.setdefault(debate_id, []).append({
            "agent": agent,
            "round_num": round_num,
            "content": content,
            "created_at": _now(),
        })


async def list_debates(limit: int = 20):
    if USE_DATABASE:
        from db.database import AsyncSessionLocal
        from models.models import Debate, DebateMessage
        from sqlalchemy import select, desc, func
        async with AsyncSessionLocal() as db:
            res = await db.execute(select(Debate).order_by(desc(Debate.created_at)).limit(limit))
            debates = res.scalars().all()
            out = []
            for d in debates:
                c = await db.execute(
                    select(func.count(DebateMessage.id)).where(DebateMessage.debate_id == d.id)
                )
                out.append({
                    "id": d.id, "topic": d.topic, "status": d.status,
                    "created_at": d.created_at, "completed_at": d.completed_at,
                    "message_count": c.scalar() or 0,
                })
            return out
    else:
        out = []
        for d in sorted(_mem_debates.values(), key=lambda x: x["created_at"], reverse=True)[:limit]:
            out.append({
                **d,
                "message_count": len(_mem_messages.get(d["id"], [])),
            })
        return out


async def get_debate_full(debate_id: str):
    if USE_DATABASE:
        from db.database import AsyncSessionLocal
        from models.models import Debate, DebateMessage
        from sqlalchemy import select
        async with AsyncSessionLocal() as db:
            res = await db.execute(select(Debate).where(Debate.id == debate_id))
            d = res.scalar_one_or_none()
            if not d:
                return None
            mres = await db.execute(
                select(DebateMessage).where(DebateMessage.debate_id == debate_id).order_by(DebateMessage.id)
            )
            msgs = mres.scalars().all()
            return {
                "id": d.id, "topic": d.topic, "status": d.status,
                "created_at": d.created_at, "completed_at": d.completed_at,
                "messages": [
                    {"agent": m.agent, "round_num": m.round_num, "content": m.content, "created_at": m.created_at}
                    for m in msgs
                ],
            }
    else:
        d = _mem_debates.get(debate_id)
        if not d:
            return None
        return {**d, "messages": _mem_messages.get(debate_id, [])}
