#!/usr/bin/env python3
"""Arlo battery state -> todoist task"""
import os
import sys
from datetime import datetime,timedelta
import yaml
import todoist_api_python
from todoist_api_python.api import TodoistAPI
import arlo


def _add_task_project(
                    api: todoist_api_python.api.TodoistAPI,
                    taskname: str,
                    duedate: str) -> todoist_api_python.models.Task:
    if 'project' in TODOIST_CONF:
        for project in api.get_projects():
            if project.name == TODOIST_CONF['project']:
                return tapi.add_task(content=taskname,
                                    project_id=project.id,
                                    due_date=duedate)
    return tapi.add_task(content=taskname,
                        due_date=duedate)


SETTINGS_FILE='settings.yaml'
if not os.path.isfile(SETTINGS_FILE):
    print('Error: You have not setup your settings.yaml file')
    sys.exit(1)
with open(SETTINGS_FILE) as yamlconf:
    CONF_FROM_FILE = yaml.safe_load(yamlconf)

if 'arlo' not in CONF_FROM_FILE:
    print(f'No \'arlo\' conf setting in {SETTINGS_FILE}')
    sys.exit(1)
if 'todoist' not in CONF_FROM_FILE:
    print(f'No \'todoist\' conf setting in {SETTINGS_FILE}')
    sys.exit(1)

ARLO_CONF = CONF_FROM_FILE['arlo']
TODOIST_CONF = CONF_FROM_FILE['todoist']

arlo = arlo.Arlo(ARLO_CONF['username'], ARLO_CONF['password'])
tapi = TodoistAPI(TODOIST_CONF['token'])

tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
devices = {}

# Devices - no battery or connection details
alldevices = arlo.GetDevices()

# battery / connection is via the base station
base_devices = []
for station in arlo.GetDevices('basestation'):
    devices.update({station['deviceId']: station['deviceName']})
    station_devices = arlo.GetCameraState(station)

    for this_device in station_devices['properties']:
        base_devices.append(this_device)

# match the types
for camera in base_devices:
    if 'batteryLevel' in camera:
        deva = [ x for x in alldevices if x['deviceId'] == camera['serialNumber']][0]
        total = { **camera, **deva}

        if total['batteryLevel'] < int(ARLO_CONF['battery']):

            task = _add_task_project(tapi,
                f'ARLO: {total["deviceName"]} is at {total["batteryLevel"]}% battery',
                tomorrow
            )

arlo.Logout()
sys.exit()
