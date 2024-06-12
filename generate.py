import requests
import json
import time
from flask import Flask

app = Flask(__name__)




url = 'https://birminghamleisure.legendonlineservices.co.uk/birmingham_comm_rg_home/Timetable/GetClassTimeTable'


headers = {
    'Content-Type': 'application/json'
}

payload = {
    'ResourceSubTypeIdList': '469',
    #'ResourceSubTypeIdList': '537',
    'FacilityLocationIdList': '4811',
    'DateFrom': '2024-06-13T00:00:00+01:00',
    'DateTo': '2024-06-14T00:00:00+01:00'
}


json_payload = json.dumps(payload)
#print(json_payload)
response = requests.post(url, headers=headers, data=json_payload)


for event in  response.json()['Results']:
    print(event['title'])




@app.route("/")
def index():
    return "Hello World!"