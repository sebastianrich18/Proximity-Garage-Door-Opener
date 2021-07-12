import asyncio
from aiohttp import ClientSession
import pymyq
import secret

shouldOpen = False
shouldClose = False

async def garage() -> None:
    global shouldClose, shouldOpen
    """Create the aiohttp session and run."""
    async with ClientSession() as websession:
      myq = await pymyq.login(secret.garage['email'], secret.garage['password'], websession)
      
      if shouldOpen:
        await list(myq.covers.items())[0][1].open()
        shouldOpen = False

      if shouldClose:
        await list(myq.covers.items())[0][1].close()
        shouldClose = False


asyncio.get_event_loop().run_until_complete(garage())