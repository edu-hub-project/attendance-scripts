# Useful Local Scripts

Some extra functions in case something goes wrong or some data needs to be double checked.
They are meant to be used as local python scripts to download attendances in `.csv` (human-readable) or `.json` (to upload) files.

## Get Zoom users

It generates a .csv for each user (of the Zoom account) with the info about the user (id, name, emails).
Launch with
```
python get_zoom_users.py
```

It requires:
- the zoomapi module (the zoomapi.py file in the repo)
- the config.yaml file with the secrets.
- the utils_IO module (the utils_IO.py file), actually only one line to read the yaml file

## Get Zoom meetings
It generates a .csv for each user (of the Zoom account) with the meeting that the user created (some information like topic and time are written).
Launch with
```
python get_zoom_meetings.py
```

It requires:
- the zoomapi module (the zoomapi.py file in the repo)
- the config.yaml file with the secrets.
- the utils_IO module (the utils_IO.py file), actually only one line to read the yaml file

## Get participants of more meetings
It generates a file with names of participaants of all the meetings.
Launch with
```
python get_participants_csv.py zoom-meetings.csv
```
or
```
python get_participants_json.py zoom-meetings.csv
```
depending whether you want the results on `.csv` or `.json` files.
The json version is slightly different because it was meant to be compatible with the upload in the platform.

NOTE: You can also launch only with `python get_participants_csv.py` without specifiying the path to the `.csv` file, then it will try to read the standard one (`zoom-meetings-id_wise2122.csv`). To change this, check line 11 of the code.

It reads all the meeting related to a single course (from zoom) and saves a single file with all meeting (each meeting is a row with date and the names of the participants).
It works with multiple courses, so if you list all the courses and launch it once, it will save one file for each course

It requires a `.csv` file with the following information:
```
title_course,
id_course,
link_zoom-meeting,
time-start
```
Actually, `id_course` is not yet used, so it can be skipped.

Example (without `id_course`, see the double `,`):
```
VR Sessions Part II - 3,,23137084582,2020-12-18T16:55:37Z,2020-12-18T17:00:00Z
```
(the zoom meeting was changed, it's most likely not valid). Of course you can write more than one course, just one for each line.


## Get report of single Zoom meeting
Wrapper in a single file (no dependencies from other file in the directory, if needed to be uploaded in gcloud) to get the participants report of a single meeting (if the meeting is recurrent, it gets only the last one) using the [`get /report/meetings/{meetingId}/participants` method from the Zoom API](https://marketplace.zoom.us/docs/api-reference/zoom-api/reports/reportmeetingparticipants).
It expects two arguments, one string for the name of the meeting and the zoom link (in this order). Link can be full address or only meeting id.

Launch with
```
python3 standalone_get_single_meeting_participants.py "course name" "meeting id or link"
```

It saves a report from a single meeting, both in a human readable `.csv` and a `.json` that was uploaded in the old platform (unsure if this will still be relevant, but usually easier to manipulate via code).

There is another version which also includes the time in the information of the meeting. Because of this, the information changes slightly.
It does not give back the participant reports, it gives back a full report of the meeting calling the [`get /meetings/{meetingId}` method of the Zoom API](https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/meeting).
It expects the same arguments.

Launch with
```
python3 standalone_get_single_meeting_participants_with_time.py "course name" "meeting id or link"
```

It requires the `meeting_id` (the zoom one). At the moment it does not include limesurvey.


## Zoom API file (`zoomapi.py`)
Methods to communicate with the Zoom API to get users, meetings and participants

## Input/Ouptut Functions (`utils_IO.py`)
Utility functions to read and write csv and YAML file (config)
