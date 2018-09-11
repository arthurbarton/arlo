#!/usr/bin/env python3
from Arlo import Arlo
import argparse
import sys
import os
from datetime import timedelta, date
import datetime
import settings

parser = argparse.ArgumentParser(description="Arlo Arming robot")
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Enable verbose output')
parser.add_argument('-d', '--delete', dest='delete', action='store_true', help='Delete video library after downloading')
args = parser.parse_args()

# This is the 7 day free limit for the cloud library
today = (date.today() - timedelta(days=0)).strftime("%Y%m%d")
seven_days_ago = (date.today() - timedelta(days=7)).strftime("%Y%m%d")
print("today:", today, "seven...:", seven_days_ago)

if not os.path.exists(settings.VIDEO_DIR):
    if args.verbose:
        print(sys.argv[0] + ": Creating video dir at", settings.VIDEO_DIR)
    os.makedirs(settings.VIDEO_DIR)

if args.verbose:
    print(sys.argv[0] + ": Downloading video library (" + seven_days_ago + ") till now into", settings.VIDEO_DIR)
    if args.delete:
        print(sys.argv[0] + ":      Deleting the remote library afterwards")

try:
    if args.verbose:
        print(sys.argv[0] + ": Logging in with", settings.USERNAME)
    arlo = Arlo(settings.USERNAME, settings.PASSWORD)

    if args.verbose:
        print(sys.argv[0] + ": Fetching Arlo Library contents")
    library = arlo.GetLibrary(seven_days_ago, today)

    # Iterate through the recordings in the library.
    for recording in library:
        # Get video as a chunked stream; this function returns a generator.
        stream = arlo.StreamRecording(recording['presignedContentUrl'])
        videofilename = datetime.datetime.fromtimestamp(
            int(recording['name']) // 1000).strftime(
                '%Y-%m-%d %H-%M-%S') + ' ' + recording['uniqueId'] + '.mp4'
        with open(settings.VIDEO_DIR + '/' + videofilename, 'wb') as f:
            for chunk in stream:
                f.write(chunk)
            f.close()

        if args.verbose:
            print(sys.argv[0] + ': Downloaded video '
                  + videofilename + ' from ' + recording['createdDate'] + '.')


    if args.verbose and args.delete:
        print(sys.argv[0] + ": Deleting Arlo Remote Library")
        result = arlo.BatchDeleteRecordings(library)

    arlo.Logout()
    if args.verbose:
        print(sys.argv[0] + ": Logged out")

except Exception as e:
    print(e)

exit(0)
