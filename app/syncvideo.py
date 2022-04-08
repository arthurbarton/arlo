#!/usr/bin/env python3
'''Download Arlo remote recordings'''
import os
import sys
import argparse
import datetime
from datetime import timedelta, date, datetime
import yaml
import arlo


parser = argparse.ArgumentParser(description="Arlo Video Download robot")
parser.add_argument('-s', '--settings', type=str, default='/settings.yaml',
                    help='Path to settings.yaml')
parser.add_argument('-o', '--output', required=True, type=str,
                    help='Local path to store downloads in')
parser.add_argument('-d', '--delete', action='store_true',
                    help='Delete remote video library after downloading')
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


if not os.path.isdir(args.output):
#    print(f"Output path - {args.output} - does not exist. Creating it")
    os.makedirs(args.output)

# This is the 7 day free limit for the cloud library
today = (date.today() - timedelta(days=0)).strftime("%Y%m%d")
seven_days_ago = (date.today() - timedelta(days=7)).strftime("%Y%m%d")

remote_library = arlo.GetLibrary(seven_days_ago, today)
for remote_vid in remote_library:
    # url
    stream = arlo.StreamRecording(remote_vid['presignedContentUrl'])
    # datestamp for by-day folder storage
    stream_datestamp = remote_vid['createdDate']
    if not os.path.isdir(args.output + '/' + stream_datestamp):
        os.makedirs(args.output + '/' + stream_datestamp)
    stream_fn = datetime.fromtimestamp(
        int(remote_vid['name']) // 1000).strftime('%H-%M-%S'
    ) + '_' + remote_vid['uniqueId'] + '.mp4'

    localpath = args.output + '/' + stream_datestamp + '/' + stream_fn
    if os.path.isfile(localpath):
        print(f'Video {remote_vid["name"]} Already exists at {localpath}')
        continue

    with open(localpath, 'wb') as localf:
        for chunk in stream:
            localf.write(chunk)
    localf.close()

    if args.delete and os.path.isfile(localpath):
        arlo.DeleteRecording(remote_vid)

arlo.Logout()
sys.exit(0)
