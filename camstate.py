#!/usr/bin/env python3
from arlo import Arlo
import argparse
import sys
import settings
import os

parser = argparse.ArgumentParser(description="Arlo Online/Status")
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Enable verbose output')
parser.add_argument('-b', '--blacklist', dest='blacklist', action='store', help='Cameras to skip')
parser.add_argument('-p', '--percent', dest='percent', action='store', help='What percentage of battery is too low')
args = parser.parse_args()

things = {}

try:
    if args.verbose:
        print(sys.argv[0] + ": Logging in with", settings.USERNAME)
    arlo = Arlo(settings.USERNAME, settings.PASSWORD)

    if not args.percent:
        if args.verbose:
            print(sys.argv[0] + ": Setting battery percent warning to 25%")
        percent = 25
    else:
        percent = args.percent

    if args.verbose:
        print(sys.argv[0] + ": Fetching devices")
    # build a map of device Names to device IDs
    # as names are not exposed in GetCameraState()
    devices = arlo.GetDevices()
    for d in devices:
        _item = d['deviceId']
        things[_item] = {}
        things[_item][d['deviceType']] = d['deviceName']

    # fetch basestations
    if args.verbose:
        print(sys.argv[0] + ": Fetching basestations")
    basestations = arlo.GetDevices('basestation')

    for station in basestations:
        things[station['deviceId']]['connected'] = station['connectivity']['connected']
        if args.verbose:
            print(sys.argv[0] + ": Fetching cameras attached to basestation", station['deviceName'])
        stationcameras = arlo.GetCameraState(station)
        for x in stationcameras['properties']:
            things[x['serialNumber']]['batteryLevel'] = x['batteryLevel']
            things[x['serialNumber']]['connectionState'] = x['connectionState']
            things[x['serialNumber']]['signalStrength'] = x['signalStrength']
            things[x['serialNumber']]['updateAvailable'] = x['updateAvailable']

    # logout
    if args.verbose:
        print(sys.argv[0] + ": Logging out")
    # Logout() emits a newline, which bypasses mail -E
    sys.stdout = open(os.devnull, "w")
    arlo.Logout()
    sys.stdout = sys.__stdout__

    if args.verbose:
        print(sys.argv[0] + ": Building report")
        print(things)
    for i in things:
        t = things[i]
        if 'basestation' in t:
            if bool(t['connected']):
                if args.verbose:
                    print("basestation", t['basestation'] + ": Connected")
            else:
                if args.verbose:
                    print("basestation", t['basestation'] + ": Disconnected")
        elif 'camera' in t:
            if t['camera'] == args.blacklist:
                continue
            #
            if t['connectionState'] != 'available':
                print("Warning: Camera", t['camera'], "is", t['connectionState'])
            if t['batteryLevel']:
                if t['batteryLevel'] <= int(percent):
                    print("Warning: Camera", t['camera'], "is at", str(t['batteryLevel']) + "%")
                if args.verbose:
                    print("camera", t['camera'] + ":", str(t['batteryLevel']) + "%", "connection:", t['connectionState'], "signal:", t['signalStrength'])
            else:
                if args.verbose:
                    print("camera", t['camera'] + "connection:", t['connectionState'], "signal:", t['signalStrength'])


except Exception as e:
    print("Oh no, an Exception")
    print(e)

exit(0)
