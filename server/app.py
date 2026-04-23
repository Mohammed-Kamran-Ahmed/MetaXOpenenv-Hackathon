from fastapi import FastAPI
from openenv.core import create_fastapi_app
from engine import WardenEngine
from schema import AgentAction, WardenObservation

class BlindWardenEnv:
    def __init__(self):
        self.engine = WardenEngine()

    def reset(self, episode_id: str = None, seed: int = None):
        """Standard sync reset."""
        self.engine = WardenEngine()
        return WardenObservation(
            chat_logs=[],
            system_metrics={"cpu": 0.0, "network_io": 0.0},
            file_metadata=[],
            reward=0.0,
            done=False
        )

    # FIX: Make this async and return the result of the sync reset
    async def reset_async(self, episode_id: str = None, seed: int = None):
        """Async wrapper for reset."""
        return self.reset(episode_id=episode_id, seed=seed)

    def step(self, action: AgentAction):
        reward = self.engine.process_action(action)
        return WardenObservation(
            chat_logs=self.engine.chat_history,
            system_metrics={"cpu": 12.5, "network_io": 1.0 if self.engine.network_active else 0.0},
            file_metadata=["system logs updated"],
            reward=reward,
            done=self.engine.is_done
        )

    # FIX: Make this async just in case
    async def step_async(self, action: AgentAction):
        """Async wrapper for step."""
        return self.step(action)

    def close(self):
        """No-op cleanup."""
        pass

# Pass the Class
app = create_fastapi_app(BlindWardenEnv, AgentAction, WardenObservation)