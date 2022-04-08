#!/usr/bin/env python3
'''Arm or Disarm Arlo base stations'''
import os
import sys
import argparse
import yaml
import arlo

def _decode_mode(mode: dict) -> str:
    mode_names = {
        'mode0': '[default] Disarmed',
        'mode1': '[default] Armed',
        'mode2': '[default] All motion on'
    }

    if mode['activeModes']:
        return mode_names[mode['activeModes'][0]]
    if mode['activeSchedules']:
        return f'[Schedule] {mode["activeSchedules"][0]}'
    return '[????] Unknown'

def _set_mode(api: arlo.Arlo, mode: str, dev: dict) -> dict():
    res = api.Arm(dev) if mode.lower() == 'arm' else api.Disarm(dev)
    return res


parser = argparse.ArgumentParser(description="Arlo Arming robot")
parser.add_argument('-s', '--settings', type=str, default='/settings.yaml',
                    help='Path to settings.yaml')
parser.add_argument('-c', '--confirm', action='store_true',
                    help='Confirm changes')
parser.add_argument('-m', '--mode', choices=['arm','disarm'], action='store',
                    help='Arm or Disarm Mode for the Arlo', required=True)
args = parser.parse_args()

if not os.path.isfile(args.settings):
    print('Error: You have not setup your settings.yaml file')
    sys.exit(1)
with open(args.settings) as yamlconf:
    CONF_FROM_FILE = yaml.safe_load(yamlconf)

if 'arlo' not in CONF_FROM_FILE:
    print(f'No \'arlo\' conf setting in {args.settings}')
    sys.exit(1)
ARLO_CONF = CONF_FROM_FILE['arlo']
arlo = arlo.Arlo(ARLO_CONF['username'], ARLO_CONF['password'])

base_devices = arlo.GetDevices()
for station_mode in arlo.GetModesV2():
    here = [x for x in base_devices if x['uniqueId'] == station_mode['uniqueId']][0]
    current = _decode_mode(station_mode)

    if args.confirm:
        print(f'Device {here["deviceName"]} (a {here["deviceType"]}) is currently {current}')
        prompt = input(f'Do you want to {args.mode} device {here["deviceName"]} [yes/No]: ')
        if prompt.lstrip().lower()[:1] == 'y':
            setarm = _set_mode(arlo, args.mode, here)
        else:
            print('OK - Skipped')
            continue
    else:
        setarm = _set_mode(arlo, args.mode, here)
    print(f'Device {here["deviceName"]} has been {args.mode}ed. ')

arlo.Logout()
sys.exit(0)
