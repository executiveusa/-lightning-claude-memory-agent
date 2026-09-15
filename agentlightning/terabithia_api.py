"""Terabithia fleet adapter for Agent Lightning.

Lightning is an evaluator, not an authority. These endpoints accept bounded
fleet evaluation missions and return findings/corrections without mutating the
originating mission or shared memory.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import HTTPException, Request
from litellm.proxy.proxy_server import app


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mission(payload: Dict[str, Any]) -> Dict[str, Any]:
    candidate = payload.get("mission") if isinstance(payload.get("mission"), dict) else payload
    if not isinstance(candidate, dict):
        raise HTTPException(status_code=400, detail="Mission envelope is required")
    for key in ("mission_id", "request_id", "trace_id", "target", "route", "user_intent"):
        if not str(candidate.get(key, "")).strip():
            raise HTTPException(status_code=400, detail=f"{key} is required")
    if candidate["target"] != "lightning" or candidate["route"] != "evaluation":
        raise HTTPException(status_code=409, detail="Lightning only accepts evaluation missions targeted to lightning")
    return candidate


@app.get("/health")
async def terabithia_lightning_health() -> Dict[str, Any]:
    return {
        "ok": True,
        "agent": "lightning",
        "role": "evaluation",
        "authority": "advisory",
        "timestamp": _now(),
    }


@app.post("/api/terabithia/invoke")
async def terabithia_lightning_invoke(request: Request) -> Dict[str, Any]:
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON body") from exc

    mission = _mission(payload)
    evaluated_result = payload.get("evaluated_result") if isinstance(payload.get("evaluated_result"), dict) else None
    evaluated_mission = payload.get("evaluated_mission") if isinstance(payload.get("evaluated_mission"), dict) else None

    failures = []
    correction = None
    verdict = "insufficient_evidence"

    if evaluated_result:
        status = str(evaluated_result.get("status", "unknown"))
        evidence = evaluated_result.get("evidence") or []
        failures = [str(item) for item in (evaluated_result.get("failures") or [])]
        if status == "done" and evidence and not failures:
            verdict = "pass"
        elif status in {"failed", "blocked", "needs_human"} or failures:
            verdict = "needs_correction"
            correction = evaluated_result.get("next_action") or "Inspect the failure evidence, correct the responsible runtime, and retry through Terabithia."
        else:
            verdict = "needs_evidence"
            correction = "Require concrete evidence references before accepting the originating mission as complete."

    subject_id = None
    if evaluated_mission:
        subject_id = evaluated_mission.get("mission_id")

    summary = f"Lightning evaluation: {verdict}."
    if correction:
        summary += f" Recommended correction: {correction}"

    return {
        "mission_id": mission["mission_id"],
        "request_id": mission["request_id"],
        "trace_id": mission["trace_id"],
        "agent_id": "lightning",
        "status": "done",
        "summary": summary,
        "artifacts": [],
        "evidence": [
            {
                "type": "trace",
                "ref": f"trace://{mission['trace_id']}",
                "summary": "Lightning evaluation trace",
            }
        ],
        "failures": [],
        "human_blocker": None,
        "handoff": None,
        "memory_candidate": (
            {
                "type": "lesson",
                "summary": summary,
                "context_refs": [f"mission://{subject_id}"] if subject_id else [],
            }
            if verdict == "needs_correction"
            else None
        ),
        "next_action": correction,
        "completed_at": _now(),
        "evaluation": {
            "verdict": verdict,
            "subject_mission_id": subject_id,
            "observed_failures": failures,
            "authority": "advisory",
        },
    }
