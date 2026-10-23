"""The smallest SentinelIQ maintenance decision flow."""

from __future__ import annotations

from dataclasses import dataclass

from .decider import DeciderClient


@dataclass(frozen=True)
class MaintenanceDecision:
    action: str
    confidence: float | None
    sensor_anomaly: float


def decide_maintenance_action(client: DeciderClient, sensor_summary: str) -> MaintenanceDecision:
    answers = client.decide(
        sensor_summary,
        {
            "sensor_anomaly": {
                "type": "noul",
                "instructions": "Are these sensor readings indicating an abnormal condition?",
            },
            "action": {
                "type": "choice",
                "instructions": "What maintenance action should be taken next?",
                "criteria": {
                    "monitor": "continue monitoring; no immediate intervention",
                    "inspect": "schedule an inspection to investigate the condition",
                    "shutdown": "safely shut down the asset and escalate urgently",
                },
            },
        },
    )
    anomaly = answers["sensor_anomaly"]
    action = answers["action"]
    return MaintenanceDecision(
        action=action["choice"],
        confidence=action.get("confidence"),
        sensor_anomaly=float(anomaly["noul"]),
    )
