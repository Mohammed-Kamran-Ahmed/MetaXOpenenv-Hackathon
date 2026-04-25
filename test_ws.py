import asyncio
from openenv.core import GenericEnvClient

async def test():
    c = GenericEnvClient('http://127.0.0.1:8000')
    try:
        await c.reset()
        print('Reset success!')
    except Exception as e:
        print(f'Error: {e}')

asyncio.run(test())
