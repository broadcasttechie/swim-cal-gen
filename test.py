import requests
import json
import datetime
from datetime import timedelta

from objects import Activity

def get_activities(facility, activity, days=30):
    url = 'https://birminghamleisure.legendonlineservices.co.uk/birmingham_comm_rg_home/Timetable/GetClassTimeTable'
    headers = { 'Content-Type': 'application/json' }
    payload = {
    'ResourceSubTypeIdList': activity,
    'FacilityLocationIdList': facility,
    'DateFrom': datetime.datetime.now().astimezone().isoformat(),
    'DateTo': (datetime.datetime.now() + timedelta(days=days)).astimezone().isoformat()
    }
    json_payload = json.dumps(payload)
    activities = []
    response = requests.post(url, headers=headers, data=json_payload)
    for a in response.json()['Results']:
        act = Activity(a['title'], a['start'], a['end'], a['FacilityName'], 4811, a['AvailableSlots'], a['Capacity'] )
        activities.append(act)
    return activities
        

for a in get_activities(4811, [469, 537],5):
    print(a)