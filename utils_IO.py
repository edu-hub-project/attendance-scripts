import csv
import yaml # to install it, it's pip install pyyaml, not pip install yaml
import pdb

def save_participants_as_csv(names, attendances, times, path):
    """Saves the participants of the meeting on a .csv file."""
    with open(path, 'w') as csvfile:
        writer = csv.writer(csvfile)
        first_row = []
        first_row.append("Name")
        for i in range(len(times)):
            first_row.append(f"{times[i]}")
        writer.writerow(first_row)
        for j in range(len(names)):
            csv_row = list(attendances[j])
            csv_row.insert(0, names[j])
            writer.writerow(csv_row)
    print(f"saved to {path}")

def save_participants_lists_csv(names, times, path):
    """Saves a list of participants of each meeting on a .csv file."""
    with open(path, 'w') as csvfile:
        writer = csv.writer(csvfile)
        for j in range(len(names)):
            csv_row = list(names[j])
            csv_row.insert(0, times[j])
            writer.writerow(csv_row)
    print(f"saved to {path}")

def read_YAML(yaml_path):
    """Read the configuration parameters and secrets from the YAML file"""
    with open(yaml_path) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    return config

def read_courses_info_from_csv(csv_path):
    """Read the meetings info and return them as a list of tuples (meeting_id, meeting_name)."""
    courses_info = []
    with open(csv_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                course_name = row[0]
                course_link = row[2]
                #meeting_start_time = row[3]
                start_index = 0 if course_link.find("/j/") < 0 else course_link.find("/j/")+3
                meeting_id = course_link[start_index:]
                courses_info.append((course_name, meeting_id))
                line_count += 1
    print(f'Found meetings for {line_count-1} courses.')
    return courses_info
