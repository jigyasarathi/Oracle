from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from oracle.service import ask

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("oracle.api")

app = FastAPI(title="ORACLE", version="0.1.0")


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    session_id: str | None = None


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ask")
async def ask_endpoint(req: AskRequest) -> dict:
    try:
        return await ask(req.question, session_id=req.session_id)
    except Exception:
        log.exception("ask failed")
        raise HTTPException(status_code=500, detail="Internal error while answering.") from None
