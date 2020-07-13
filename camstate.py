#!/usr/bin/env python3
from arlo import Arlo
import argparse
import sys
import settings
import os
from todoist.api import TodoistAPI

parser = argparse.ArgumentParser(description="Arlo Online/Status")
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Enable verbose output')
parser.add_argument('-b', '--blacklist', dest='blacklist', action='store', help='Cameras to skip')
parser.add_argument('-p', '--percent', dest='percent', action='store', help='What percentage of battery is too low')
args = parser.parse_args()

things = {}

def vprint(*arg):
    if args.verbose and len(arg) > 0:
        print(sys.argv[0] + ":", end='')
        for e in arg:
            print(" ", e, end='')
        print("")

def totask(s: str, v: bool) -> (bool):
    if v: print("todoist - ", s)
    api = TodoistAPI(settings.TODOISTTOKEN)
    api.sync()
    inboxid = api.state['projects'][0]['id']
    task = api.quick.add('ChangeBattery: '+ s + " " + settings.TODOISTLABEL,
                         note='auto gen task', remminder='tomorrow')
    True if task["id"] else False

try:
    vprint("Logging in with", settings.USERNAME)
    arlo = Arlo(settings.USERNAME, settings.PASSWORD)

    if not args.percent:
        vprint("Setting battery percent warning to 25%")
        percent = 25
    else:
        percent = args.percent

    vprint("Fetching devices")
    # build a map of device Names to device IDs
    # as names are not exposed in GetCameraState()
    devices = arlo.GetDevices()
    for d in devices:
        _item = d['deviceId']
        things[_item] = {}
        things[_item][d['deviceType']] = d['deviceName']

    # fetch basestations
    vprint("Fetching basestations")
    basestations = arlo.GetDevices('basestation')

    for station in basestations:
        things[station['deviceId']]['connected'] = station['connectivity']['connected']
        vprint("Fetching cameras attached to basestation", station['deviceName'])
        stationcameras = arlo.GetCameraState(station)
        for x in stationcameras['properties']:
            things[x['serialNumber']]['batteryLevel'] = x['batteryLevel']
            things[x['serialNumber']]['connectionState'] = x['connectionState']
            things[x['serialNumber']]['signalStrength'] = x['signalStrength']
            things[x['serialNumber']]['updateAvailable'] = x['updateAvailable']

    # logout
    vprint("Logging out")
    # Logout() emits a newline, which bypasses mail -E
    sys.stdout = open(os.devnull, "w")
    arlo.Logout()
    sys.stdout = sys.__stdout__

    vprint("Building report")
    #vprint(things)
    for i in things:
        t = things[i]
        if 'basestation' in t:
            if bool(t['connected']):
                vprint("basestation", t['basestation'] + ": Connected")
            else:
                vprint("basestation", t['basestation'] + ": Disconnected")
        elif 'camera' in t:
            if t['camera'] == args.blacklist:
                continue
            #
            if t['connectionState'] != 'available':
                s = t['camera'] + " is " + t['connectionState']
                print(s)
                totask(s, args.verbose)
            if t['batteryLevel']:
                if t['batteryLevel'] <= int(percent):
                    s = str(t['camera']) + " is at " + str(t['batteryLevel']) + "%"
                    print(s)
                    totask(s, args.verbose)
                vprint("camera", t['camera'] + ":", str(t['batteryLevel']) + "%", "connection:", t['connectionState'], "signal:", t['signalStrength'])
            else:
                vprint("camera", t['camera'] + "connection:", t['connectionState'], "signal:", t['signalStrength'])


except Exception as e:
    print("Oh no, an Exception")
    print(e)

exit(0)
