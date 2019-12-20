#!/usr/bin/env python3
from arlo import Arlo
import argparse
import sys
import settings

parser = argparse.ArgumentParser(description="Arlo Device Listererer")
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Enable verbose output')
args = parser.parse_args()

device_map = {}

try:
    if args.verbose:
        print(sys.argv[0] + ": Logging in with", settings.USERNAME)
    arlo = Arlo(settings.USERNAME, settings.PASSWORD)

    if args.verbose:
        print(sys.argv[0] + ": Fetching devices")
    # build a map of device Names to device IDs
    # as names are not exposed in GetCameraState()
    devices = arlo.GetDevices()
    for d in devices:
        _deviceId = d['deviceId']
        device_map[_deviceId] = {}
        device_map[_deviceId]['name'] = d['deviceName']

    # fetch basestations
    if args.verbose:
        print(sys.argv[0] + ": Fetching basestations")
    basestations = arlo.GetDevices('basestation')

    for station in basestations:
        if station['connectivity']['connected'] == True:
            if args.verbose:
                print(sys.argv[0] + ": Fetching cameras attached to basestation", station['deviceName'])
            stationcameras = arlo.GetCameraState(station)
            for camera in stationcameras['properties']:
                _serialNumber = camera['serialNumber']
                _batteryLevel = camera['batteryLevel']
                device_map[_serialNumber]['batteryLevel'] = camera['batteryLevel']
                device_map[_serialNumber]['connectionState'] = camera['connectionState']
                device_map[_serialNumber]['signalStrength'] = camera['signalStrength']
                device_map[_serialNumber]['baseStation'] = station['deviceName']


    # logout
    if args.verbose:
        print(sys.argv[0] + ": Logging out")
    arlo.Logout()

except Exception as e:
    print("Oh no, an Exception")
    print(e)


if args.verbose:
    print(sys.argv[0] + ": Building report")

for device in device_map:
    if device_map[device].get("batteryLevel") != None:
        print("Camera: " + device_map[device]['name'])
        print("Battery -> " + str(device_map[device]['batteryLevel']), "%")
        print("Connection -> " + device_map[device]['connectionState'])
        print("Signal -> " + str(device_map[device]['signalStrength']))
        print()


exit(0)
