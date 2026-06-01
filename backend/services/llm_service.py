import os
from typing import AsyncGenerator
from groq import AsyncGroq

# Best free-tier quality model on Groq as of 2026.
# Alternatives: "llama-3.1-8b-instant" (faster), "openai/gpt-oss-120b" (reasoning)
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

_client = None


def get_client():
    """Lazily create the Groq client so GROQ_API_KEY is read after .env loads."""
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Get a free key at https://console.groq.com/keys "
                "and add it to backend/.env"
            )
        _client = AsyncGroq(api_key=api_key)
    return _client


AGENT_SYSTEM_PROMPTS = {
    "scientist": """You are the Scientist agent in a structured multi-agent debate.
Argue strictly from empirical evidence, peer-reviewed research, data, and scientific consensus.
Challenge claims that lack evidence. Cite the types of studies/evidence where relevant.
Be rigorous and willing to update positions based on data.
Keep responses to 4-5 focused sentences. Be direct.""",

    "critic": """You are the Critic agent in a structured multi-agent debate.
Identify logical flaws, unintended consequences, risks, and weaknesses in ALL positions.
Be intellectually honest: acknowledge strong points before attacking weak ones.
Do not simply oppose everything - find the genuine vulnerabilities.
Keep responses to 4-5 focused sentences. Be sharp and specific.""",

    "ethicist": """You are the Ethicist agent in a structured multi-agent debate.
Analyze through moral philosophy - utilitarian, deontological, virtue ethics, and justice frameworks.
Focus on who bears risks, who benefits, vulnerable populations, and long-term societal values.
Be analytically rigorous, like a philosopher - not preachy.
Keep responses to 4-5 focused sentences. Be nuanced.""",

    "optimizer": """You are the Optimizer agent in a structured multi-agent debate.
Argue from systems thinking, cost-benefit analysis, scalability, and practical implementation.
Focus on what actually works at scale in the real world.
Challenge solutions that are elegant but unimplementable. Be quantitative where possible.
Keep responses to 4-5 focused sentences. Be pragmatic.""",

    "consensus": """You are a neutral synthesis agent.
Read all debate arguments and produce a balanced, nuanced consensus position.
Acknowledge the strongest points from each perspective.
Propose a concrete, actionable conclusion. Be honest about remaining disagreements.
Write 4-6 sentences.""",
}

AGENT_LABELS = {
    "scientist": "🔬 Scientist",
    "critic": "⚔️ Critic",
    "ethicist": "⚖️ Ethicist",
    "optimizer": "⚡ Optimizer",
    "consensus": "⬡ Board Consensus",
}


async def stream_agent(agent: str, topic: str, context: str = "") -> AsyncGenerator[str, None]:
    """Stream a single agent's response token by token using Groq."""
    system = AGENT_SYSTEM_PROMPTS[agent]

    if context:
        user_msg = (
            f'Topic under debate: "{topic}"\n\n'
            f"Context from previous discussion:\n{context}\n\n"
            "Give your response now."
        )
    else:
        user_msg = f'Topic under debate: "{topic}"\n\nGive your initial position.'

    stream = await get_client().chat.completions.create(
        model=MODEL,
        max_tokens=400,
        temperature=0.8,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ],
        stream=True,
    )

    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
