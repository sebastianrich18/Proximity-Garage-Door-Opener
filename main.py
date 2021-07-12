import asyncio

from aiohttp import ClientSession

import pymyq

import secret


async def main() -> None:
    """Create the aiohttp session and run."""
    async with ClientSession() as websession:
      myq = await pymyq.login(secret.garage['email'], secret.garage['password'], websession)
      
      devices = myq.covers
      for key in devices.keys():
        print(devices[key])


asyncio.get_event_loop().run_until_complete(main())