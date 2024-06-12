from flask import Flask
from flask import request
from flask import render_template
import requests
import json
import datetime
from datetime import timedelta
import babel

app = Flask("app")

@app.template_filter()
def format_datetime(value, format='medium'):
    timestamp = datetime(value, format)
    if format == 'full':
        format="EEEE, d. MMMM y 'at' HH:mm"
    elif format == 'medium':
        format="EE dd.MM.y HH:mm"
    return timestamp.format(format)




@app.route("/")
def index():
    url = "https://birminghamleisure.legendonlineservices.co.uk/birmingham_comm_rg_home/filteredlocationhierarchy"
    headers = { 'Content-Type': 'application/json' }
    response = requests.get(url, headers=headers)
    test = datetime.datetime.now().astimezone().replace(microsecond=0).replace(second=0).replace(minute=0).replace(hour=0).isoformat()
    return render_template('home.html', sites = response.json(), test=test)


@app.route('/facility/<id>')
def facility(id):
    url = f"https://birminghamleisure.legendonlineservices.co.uk/birmingham_comm_rg_home/Bookings/ActivitySubTypes?LocationIds={id}&ReturnAll=true&ResourceSubTypeCategoryId="
    headers = { 'Content-Type': 'application/json' }
    response = requests.get(url, headers=headers)
    return render_template('facility.html', data=response.json(), facility=id)


@app.route('/facility/<id>/activity/<activity>')
def activity(id, activity):
    url = 'https://birminghamleisure.legendonlineservices.co.uk/birmingham_comm_rg_home/Timetable/GetClassTimeTable'
    headers = { 'Content-Type': 'application/json' }
    payload = {
    'ResourceSubTypeIdList': activity,
    'FacilityLocationIdList': id,
    'DateFrom': datetime.datetime.now().astimezone().isoformat(),
    'DateTo': (datetime.datetime.now() + timedelta(days=30)).astimezone().isoformat()
    }



    json_payload = json.dumps(payload)
    response = requests.post(url, headers=headers, data=json_payload)
    return render_template('activity.html', data=response.json(), facility=id)


@app.route("/events")
def events():
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
    return response.json()['Results']