# from pydantic import BaseModel
# from typing import List, Dict, Any, Optional

# class Action(BaseModel):
#     agent_id: str
#     action_type: str
#     content: str

# class WardenObservation(BaseModel):
#     chat_logs: List[Dict[str, str]]
#     system_metrics: Dict[str, float]
#     file_metadata: List[str]
#     reward: float
#     done: bool

from pydantic import BaseModel
from typing import List, Dict

class Action(BaseModel):
    agent_id: str
    content: str

class Observation(BaseModel):
    chat_logs: List[Dict[str, str]]
    system_metrics: Dict[str, float]
    logs: Dict[str, str]
    reward: float
    done: bool