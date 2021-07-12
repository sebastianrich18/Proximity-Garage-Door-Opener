from pyicloud import PyiCloudService
from geopy import distance
import sys
import secret
from time import sleep
import datetime


def main():
    api = login(secret.sebastian)
    sebastianLoc = getLocation(api, secret.sebastian)
    sebastianLoc = (sebastianLoc['latitude'], sebastianLoc['longitude'])
    print(sebastianLoc)

    # api = login(secret.victoria)
    # victoriaLoc = getLocation(api, secret.victoria)
    # victoriaLoc = (victoriaLoc['latitude'], victoriaLoc['longitude'])

    # api = login(secret.mom)
    # momLoc = getLocation(api, secret.mom)
    # momLoc = (momLoc['latitude'], momLoc['longitude'])

    print("sebastian's distance", getDist(sebastianLoc).m)
    # print("victoia's distance", getDist(victoriaLoc).m)
    # print("mom's distance", getDist(momLoc).m)
    print()

def getDist(loc):
    homeCoords = (42.9291606, -78.655094)
    dist = distance.distance(homeCoords, loc)
    return dist


def getLocation(api, user):
    devices = api.devices
    for device in devices.keys():
        if device == user['deviceId']:
            location = devices[device].location()
            while True:
                # print('checking location accuracy')
                if not location['isInaccurate'] and not location['isOld'] and location['locationFinished']:
                    print(datetime.datetime.now())
                    print('location accurate')
                    return location
                else:
                    print("location inaccurate, checking again")
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
    while True:
        main()
        sleep(5)