#!/usr/bin/env python3
from Arlo import Arlo
import argparse
import sys
import settings

parser = argparse.ArgumentParser(description="Arlo Arming robot")
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Enable verbose output')
parser.add_argument('-m', '--mode', choices=['arm','disarm'], dest='mode', action='store', help='Arm or Disarm Mode for the Arlo', required=True)
args = parser.parse_args()

if args.verbose:
    print(sys.argv[0] + ": We are going to", args.mode.title(), "the Arlo")

try:
    if args.verbose:
        print(sys.argv[0] + ": Logging in with", settings.USERNAME)
    arlo = Arlo(settings.USERNAME, settings.PASSWORD)

    if args.verbose:
        print(sys.argv[0] + ": Fetching basestations")
    basestations = arlo.GetDevices('basestation')

    if args.verbose:
        print(sys.argv[0] + ":", args.mode.title() + "ing the Arlo")
    if args.mode.lower() == "arm":
        arlo.Arm(basestations[0])
    elif args.mode.lower() == "disarm":
        arlo.Disarm(basestations[0])

    if args.verbose:
        print(sys.argv[0] + ":", args.mode.title() + "ed!")

    arlo.Logout()
    if args.verbose:
        print(sys.argv[0] + ": Logged out")

except Exception as e:
    print(e)

exit(0)