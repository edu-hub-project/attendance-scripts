#from datetime import datetime
import os
import sys
import time
from typing import Optional, Dict, Union, Any
import requests
from authlib.jose import jwt
import json
import yaml
import csv
import datetime
import pdb

CONFIG_FILE = 'config.yaml'
OUTPUT_FOLDER = 'reports/timing'

class Zoom:
    def __init__(self):
        self.api_key = ""
        self.api_secret = ""
        self.base_url = "https://api.zoom.us/v2"
        self.reports_url = f"{self.base_url}/report/meetings"
        self.jwt_token_exp = 1800
        self.jwt_token_algo = "HS256"
        self.jwt_token = ""

    def set_api_key(self, api_key: str):
        self.api_key = api_key
    def set_api_secret(self, api_secret: str):
        self.api_secret = api_secret
    def set_jwt_token(self, jwt_token: str):
        self.jwt_token = jwt_token
    def get_jwt_token(self):
        return self.jwt_token
    def generate_jwt_token(self) -> bytes:
        iat = int(time.time())
        jwt_payload: Dict[str, Any] = {
            "aud": None,
            "iss": self.api_key,
            "exp": iat + self.jwt_token_exp,
            "iat": iat
        }
        header: Dict[str, str] = {"alg": self.jwt_token_algo}
        jwt_token: bytes = jwt.encode(header, jwt_payload, self.api_secret)

        return jwt_token
    def zoom_get_meeting_participants(self, meeting_id: str,
                                 next_page_token: Optional[str] = None) -> requests.Response:
        url: str = f"{self.reports_url}/{meeting_id}/participants"
        query_params: Dict[str, Union[int, str]] = {"page_size": 3000}
        if next_page_token:
            query_params.update({"next_page_token": next_page_token})

        r: requests.Response = requests.get(url,
                                   headers={"Authorization": f"Bearer {self.jwt_token.decode('utf-8')}"},
                                   params=query_params)

        return r

    def zoom_get_meeting_report(self, meeting_id: str) -> requests.Response:
        url: str = f"{self.reports_url}/{meeting_id}"
        r: requests.Response = requests.get(url,
                                   headers={"Authorization": f"Bearer {self.jwt_token.decode('utf-8')}"})
        return r

def read_yaml(yaml_path):
    """Read the configuration parameters and secrets from the YAML file"""
    with open(yaml_path) as file:
        yaml_config = yaml.load(file, Loader=yaml.FullLoader)
    return yaml_config

def save_list(parts, csvfile):
    """Saves the participants of the meeting on a .csv file."""
    with open(csvfile, 'w') as csvfile:
        writer = csv.writer(csvfile)
        first_row = ['id', 'user_id', 'name', 'user_email', 'join_time', 'leave_time', 'duration', 'attentiveness_score']
        writer.writerow(first_row)
        for part in parts:
            csv_row = [part['id'], part['user_id'], part['name'], part['user_email'],
                        part['join_time'], part['leave_time'], part['duration'], part['attentiveness_score']]
            writer.writerow(csv_row)
    return True

if __name__ == "__main__":

    requirements = True
    print("Reading config")
    if not os.path.exists(CONFIG_FILE):
        print(f"Config file not found! There should be a {CONFIG_FILE} file for the secrets!")
        requirements = False
    else:
        config = read_yaml(CONFIG_FILE)

    if requirements:
        if (len(sys.argv) < 3):
            print(f"Missing the meeting id or the meeting naem as parameter")
            requirements = False
        else:
            meeting_name = sys.argv[1]
            meeting_id = sys.argv[2]
            print("meeting name is:", meeting_name)

            #pdb.set_trace()
            if meeting_id[:4] == 'http':
                meeting_id = meeting_id.split('/j/')[1]
            if meeting_id.find('?') > 0:
                meeting_id = meeting_id[:meeting_id.index('?')]
            print("meeting id is:", meeting_id)

    if requirements:
        print("generating token")
        zz = Zoom()
        zz.set_api_key(config['api-key'])
        zz.set_api_secret(config['api-secret'])
        zz.set_jwt_token(zz.generate_jwt_token())
        API_response = zz.zoom_get_meeting_participants(meeting_id)
        print(f"got response {API_response}")
        #pdb.set_trace()
        if API_response.status_code == 200:
            meeting_report_API_response = zz.zoom_get_meeting_report(meeting_id)
            meeting_report = json.loads(meeting_report_API_response.text)
            participants_report = json.loads(API_response.text)
            #print(f"text {API_response.text}")
            participants = participants_report['participants']
            meeting_report['participants_report'] = participants_report
            if not os.path.exists(OUTPUT_FOLDER):
                os.mkdir(OUTPUT_FOLDER)
            today = datetime.datetime.now().date()
            csv_output_name = os.path.join(OUTPUT_FOLDER, f"{meeting_name}_{meeting_id}_{today}.csv")
            json_output_name = os.path.join(OUTPUT_FOLDER, f"{meeting_name}_{meeting_id}_{today}.json")
            with open(json_output_name, 'w') as json_file:
                json.dump(meeting_report, json_file)
            ok = save_list(participants, csv_output_name)
            if ok:
                print(f"finished, saved in {csv_output_name[:-4]}\n\n")
        else:
            print(f"API answered with {API_response} \n\nFull Message: {API_response.text}")
