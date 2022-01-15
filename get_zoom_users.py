import zoomapi as zapi
import json
from datetime import datetime
import math
import os
import csv
from collections import defaultdict
import numpy as np
import utils_IO as io


"""
It generates a .csv for each user (of the Zoom account) with the info about the user (id, name, emails).

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
output_folder = os.path.join(cur_folder, "users_info")
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# import pdb
users_info = zz.get_users_with_mail()
csv_name = os.path.join(output_folder, "users_info.csv")
with open(csv_name, 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['id', 'first_name', 'last_name', 'email'])
    print("Opencampus users:")
    for user in users_info:
        print(f"User: {user['first_name']}")
        info_row = [user['id'], user['first_name'],
                    user['last_name'], user['email']]
        writer.writerow(info_row)
        print(f"finished user {user['first_name']}!")
