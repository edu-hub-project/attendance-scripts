import zoomapi as zapi
import json
from datetime import datetime
import math
import os
import csv
import pdb
from collections import defaultdict
import numpy as np

"""
It generates a .csv for each user (of the Zoom account) with the meeting that the user created (some information like topic and time are written).

It requires:
- the zoomapi module (the zoomapi.py file in the repo)
- the config.yaml file with the secrets.
- the utils_IO module (the utils_IO.py file), actually only one line to read the yaml file
"""

print("Reading config")
if not os.path.exists('config.yaml'):
    print("Config file not found! There should be a config.yaml file for the secrets!")
config = io.read_YAML('config.yaml')
print("generating token")
zz = zapi.Zoom()
zz.set_api_key(config['api-key'])
zz.set_api_secret(config['api-secret'])
zz.set_jwt_token(zz.generate_jwt_token())

cur_folder = os.getcwd()
output_folder = os.path.join(cur_folder, "meetings_per_user")
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# import pdb
users_info = zz.get_users_with_id()
print("Opencampus users:")
for i, user in enumerate(users_info):
    print(f"User #{i}: {user[0]}")
    user_id = user[1]
    meetings_list = zz.get_list_of_meetings(user_id)
    csv_name = os.path.join(output_folder, f"{user[0]}.csv")
    with open(csv_name, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Topic', 'id', 'creation_time', 'start_time'])
        for i, meeting in enumerate(meetings_list):
            info_row = [meeting['topic'], meeting['id'], meeting['created_at']]
            if 'start_time' in meeting.keys():
                info_row.append(meeting['start_time'])
            else:
                info_row.append("")
            writer.writerow(info_row)
            print(f"{i}: {meeting['topic']} ({meeting['id']}) - created {meeting['created_at']}")
    print(f"finished user {user[0]}!")
