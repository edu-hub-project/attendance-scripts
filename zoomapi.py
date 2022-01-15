import time
from typing import Optional, Dict, Union, Any
import requests
from authlib.jose import jwt
from requests import Response
import json
from datetime import datetime
import math
import csv
from collections import defaultdict
from urllib.parse import quote_plus


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

    ### WRAPPERS
    # They use the Zoom Methods (below),
    # loads the response from json into a dict
    # and return it as a list of dict with only information needed
    # for an easier visualization and usage.
    def get_past_meeting_participants(self, meetingUUID):
        participants_response = self.zoom_get_past_meeting_participants(
            meetingUUID)
        participants = json.loads(participants_response.text)['participants']
        return participants

    def get_users_with_id(self):
        """Returns a list of (user, userID) from the main account."""
        users_res = self.zoom_get_users()
        zoom_users = json.loads(users_res.text)['users']
        users_info = []
        for user in zoom_users:
            user_name = f"{user['first_name']} {user['last_name']}"
            users_info.append((user_name, user['id']))
        return users_info

    def get_users_with_mail(self):
        """
        Returns a list of dicts with keys:
        first_name, last_name and mail
        from the main account.
        """
        users_res = self.zoom_get_users()
        zoom_users = json.loads(users_res.text)['users']
        users_info = []
        for user in zoom_users:
            user_name = {'first_name': user['first_name'],
                         'last_name': user['last_name'],
                         'id': user['id'],
                         'email': user['email']}
            users_info.append(user_name)
        return users_info

    def zoom_get_meeting_report(self, meeting_id: str) -> requests.Response:
        url: str = f"{self.reports_url}/{meeting_id}"
        r: requests.Response = requests.get(url,
                                            headers={"Authorization": f"Bearer {self.jwt_token.decode('utf-8')}"})
        return r

    def get_list_of_meetings(self, userID: str):
        """Returns a list of dicts of meetings with uuid, id, host_id, topic, start_time, created_at and join_url"""
        meetings_dicts = []
        meetings_response = self.zoom_get_list_of_meetings(userID)
        meetings = json.loads(meetings_response.text)['meetings']
        for meeting in meetings:
            meeting_dict = defaultdict()
            meeting_dict['id'] = meeting['id']
            meeting_dict['host_id'] = meeting['host_id']
            meeting_dict['uuid'] = meeting['uuid']
            meeting_dict['topic'] = meeting['topic']
            if 'start_time' in meeting.keys():
                meeting_dict['start_time'] = meeting['start_time']
            meeting_dict['created_at'] = meeting['created_at']
            meeting_dict['join_url'] = meeting['join_url']
        return meetings

    def get_meeting_instances(self, meetingId):
        """Returns a list (of dicts with uuid and start_time) of occurrences/instances of a (recurrent) meeting."""
        meeting_instances_response = self.zoom_get_meeting_instances(meetingId)
        if meeting_instances_response.status_code == 200:
            meetings = json.loads(meeting_instances_response.text)['meetings']
            meeting_instances = []
            for meeting in meetings:
                meeting_instance = meeting
                meeting_instances.append(meeting_instance)
        else:
            raise Exception(
                f"GET REQUEST not successful!\nResponse {meeting_instances_response}\n{meeting_instances_response.text}")
        return meetings

    ### ZOOM METHODS
    # API requests
    # they all return the URL Response without manipulation
    # name starts with zoom_ + the name of the above wrapper method (almost)
    def zoom_get_past_meeting_participants(self, meetingUUID: str,
                                           next_page_token: Optional[str] = None) -> Response:
        double_encoded_UUID = quote_plus(quote_plus(meetingUUID))
        url: str = f"{self.base_url}/past_meetings/{double_encoded_UUID}/participants"
        query_params: Dict[str, Union[int, str]] = {"page_size": 3000}
        if next_page_token:
            query_params.update({"next_page_token": next_page_token})

        r: Response = requests.get(url,
                                   headers={
                                       "Authorization": f"Bearer {self.jwt_token.decode('utf-8')}"},
                                   params=query_params)

        return r

    def zoom_get_meeting_details(self, meetingUUID: str):
        """meetingUUID needs to be double URL-Encoded"""
        double_encoded_UUID = quote_plus(quote_plus(meetingUUID))
        url: str = f"{self.base_url}/past_meetings/{double_encoded_UUID}"
        r: Response = requests.get(url,
                                   headers={"Authorization": f"Bearer {self.jwt_token.decode('utf-8')}"})
        return r

    def zoom_get_meeting_participants(self, meeting_id: str,
                                      next_page_token: Optional[str] = None) -> Response:
        url: str = f"{self.reports_url}/{meeting_id}/participants"
        query_params: Dict[str, Union[int, str]] = {"page_size": 3000}
        if next_page_token:
            query_params.update({"next_page_token": next_page_token})

        r: Response = requests.get(url,
                                   headers={
                                       "Authorization": f"Bearer {self.jwt_token.decode('utf-8')}"},
                                   params=query_params)

        return r

    def zoom_get_meeting_instances(self, meetingId: str) -> Response:
        url: str = f"{self.base_url}/past_meetings/{meetingId}/instances"
        r: Response = requests.get(url,
                                   headers={"Authorization": f"Bearer {self.jwt_token.decode('utf-8')}"})
        return r

    def zoom_get_list_of_meetings(self, userId: str) -> Response:
        url: str = f"{self.base_url}/users/{userId}/meetings"
        r: Response = requests.get(url,
                                   headers={"Authorization": f"Bearer {self.jwt_token.decode('utf-8')}"})
        return r

    def zoom_get_users(self) -> Response:
        url: str = f"{self.base_url}/users/"
        r: Response = requests.get(url,
                                   headers={"Authorization": f"Bearer {self.jwt_token.decode('utf-8')}"})
        return r

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

    def get_id_from_link(zoom_link):
        if zoom_link[:4] == 'http':
            meeting_id = zoom_link.split('/j/')[1]
        if meeting_id.find('?') > 0:
            meeting_id = meeting_id[:meeting_id.index('?')]
        if len(meeting_id) > 9 and len(meeting_id) < 13:
            return meeting_id
        return None
