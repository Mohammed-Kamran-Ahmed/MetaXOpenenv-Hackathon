from pydantic import BaseModel, Field
from typing import Literal, List, Optional, Dict

# --- ACTIONS ---
class AgentAction(BaseModel):
    agent_id: Literal["DEVELOPER", "DEPLOYER", "WARDEN"]
    action_type: Literal["MESSAGE", "WRITE_CODE", "DEPLOY", "WARDEN_DECISION"]
    content: str = Field(..., description="The code diff, message text, or decision rationale")
    target: Optional[str] = Field(None, description="Who is this message for?")

# --- OBSERVATIONS ---
class WardenObservation(BaseModel):
    chat_logs: List[Dict[str, str]]
    system_metrics: Dict[str, float]  # CPU, Network spikes
    file_metadata: List[str]          # "auth.py (+10 lines)"
    reward: float
    done: bool