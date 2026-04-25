from openenv.core import create_fastapi_app
from environment import BlindWardenEnvironment
from .schema import Action, Observation

# Define a factory function to instantiate the environment per session
def env_factory():
    try:
        return BlindWardenEnvironment()
    except Exception as e:
        print(f"Factory Error: {e}")
        raise e

# Create the standard OpenEnv FastAPI server
app = create_fastapi_app(env_factory, action_cls=Action, observation_cls=Observation)