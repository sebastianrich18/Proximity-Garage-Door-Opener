from pyicloud import PyiCloudService
from geopy import distance
import sys
import secret
from time import sleep
import datetime
import asyncio
from aiohttp import ClientSession
import pymyq

table = {} # this var stores who is home and who isn't
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

def main():
    global shouldClose, shouldOpen
    asyncio.get_event_loop().run_until_complete(garage())
    for user in secret.users:
        api = login(secret.users[user])
        loc = getLocation(api, secret.users[user])
        loc = (loc['latitude'], loc['longitude'])

        isHome = True if (getDist(loc) < 50) else False
        
        # print(user, "is home:", isHome, '\n')
        if table[user] != isHome:
            print(datetime.datetime.now())
            table[user] = isHome
            if isHome:
                print(user, 'arived home')
                shouldOpen = True
            else:
                print(user, 'left home')
                shouldClose = True
    

def getDist(loc):
    homeCoords = (42.9291606, -78.655094)
    dist = distance.distance(homeCoords, loc)
    return dist.m

def getLocation(api, user):
    devices = api.devices
    for device in devices.keys():
        if device == user['deviceId']:
            location = devices[device].location()
            while True:
                # print('checking location accuracy')
                if not location['isInaccurate'] and not location['isOld'] and location['locationFinished']:
                    # print('location accurate')
                    return location
                else:
                    # print("location inaccurate, checking again")
                    location = devices[device].location()
            

def login(user):
    api = PyiCloudService(user['email'], password=user['password'])   
    if api.requires_2fa:
        print("Two-factor authentication required.")
        code = input("Enter the code you received of one of your approved devices: ")
        result = api.validate_2fa_code(code)
        print("Code validation result: %s" % result)
        if not result:
            print("Failed to verify security code")
            sys.exit(1)
        if not api.is_trusted_session:
            print("Session is not trusted. Requesting trust...")
            result = api.trust_session()
            print("Session trust result %s" % result)
            if not result:
                print("Failed to request trust. You will likely be prompted for the code again in the coming weeks")
    elif api.requires_2sa:
        import click
        print("Two-step authentication required. Your trusted devices are:")
        devices = api.trusted_devices
        for i, device in enumerate(devices):
            print ("  %s: %s" % (i, device.get('deviceName',
                "SMS to %s" % device.get('phoneNumber'))))
        device = click.prompt('Which device would you like to use?', default=0)
        device = devices[device]
        if not api.send_verification_code(device):
            print("Failed to send verification code")
            sys.exit(1)
        code = click.prompt('Please enter validation code')
        if not api.validate_verification_code(device, code):
            print("Failed to verify verification code")
            sys.exit(1)
    return api

if __name__ == '__main__':
    for user in secret.users:
        table[user] = True
    while True:
        main()
        sleep(5)