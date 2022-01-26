import zoomapi as zapi
import utils_IO as io
import json
from datetime import datetime
import math
import os, sys
import pdb
from collections import defaultdict
import numpy as np

CSV_FILE = 'meetings_SoSe22.csv'
if len(sys.argv) > 1:
    CSV_FILE = sys.argv[1]

print("********")
print(f"reading participants from the the .csv file {CSV_FILE}.\nIf the file is named differently, change line 11!")
print("********")

print("Reading config")
if not os.path.exists('config.yaml'):
    print("Config file not found! There should be a config.yaml file for the secrets!")
config = io.read_YAML('config.yaml')
print("generating token")
zz = zapi.Zoom()
zz.set_api_key(config['api-key'])
zz.set_api_secret(config['api-secret'])
zz.set_jwt_token(zz.generate_jwt_token())
print("reading meetings id")
courses_info = io.read_courses_info_from_csv(CSV_FILE)
print("Done!\nCalling the API to get the participants list")
cur_folder = os.getcwd()
output_folder = os.path.join(cur_folder, "participants_lists_WiSe2122")
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# do we need end time?
end_time = datetime.strptime("2022-01-31 19:00", "%Y-%m-%d %H:%M")

for i, (course_name, course_ID) in enumerate(courses_info):
    print(f"Course: {course_name}")
    meeting_instances = zz.get_meeting_instances(course_ID)
    meeting_instances_sorted = sorted(meeting_instances, key=lambda k: k['start_time'])
    print(f"Found {len(meeting_instances)} Meetings")
    participants_names = []
    meeting_times = []
    last_meeting_time = ''
    names_current_meeting = []
    for j, meeting_inst in enumerate(meeting_instances_sorted):
        participants = zz.get_past_meeting_participants(meeting_inst['uuid'])
        print(f"Meeting {j}: starting time {meeting_inst['start_time']}")
        starting_time = meeting_inst['start_time']
        if starting_time != last_meeting_time:
            meeting_times.append(starting_time)
            names_current_meeting = []
            for part in participants:
                part_name = part['name']
                if part_name not in participants_names:
                    names_current_meeting.append(part_name)

            last_meeting_time = starting_time
            participants_names.append(names_current_meeting)
        else:
            for part in participants:
                part_name = part['name']
                if part_name not in participants_names:
                    names_current_meeting.append(part_name)

    csv_name = os.path.join(output_folder, f"participation_{course_name}_{i}.csv")
    io.save_participants_lists_csv(participants_names, meeting_times, csv_name)
    #pdb.set_trace()
