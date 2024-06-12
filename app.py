from flask import Flask, send_file, make_response, jsonify
from flask import request
from flask import render_template
import requests
import json
import datetime
from datetime import  timedelta
from icalendar import Calendar, Event, Timezone
from pytz import UTC
from flask_bootstrap import Bootstrap


def create_app():
  app = Flask("app")
  Bootstrap(app)

  return app


app = create_app()

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
    test = datetime.datetime.strptime("2024-06-13T06:30:00", "%Y-%m-%dT%H:%M:%S")
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

    activites = {}

    #for a in response.json()["Results"]:
    #    activites[a.ActivityInstanceId]["title"] = a.title

    return render_template('activity.html', data=response.json(), facility=id)





@app.route('/facility/<id>/activity/<activity>.ics')
def activity_ical(id, activity):
    cal = Calendar()
    cal.add("prodid", "-//leisurecalendar//")
    cal.add("version", "2.0")

    timezone = Timezone()
    timezone.add('TZID', 'Europe/London')
    timezone.to_ical()
    cal.add_component(timezone)

    url = 'https://birminghamleisure.legendonlineservices.co.uk/birmingham_comm_rg_home/Timetable/GetClassTimeTable'
    headers = { 'Content-Type': 'application/json' }
    payload = {
    'ResourceSubTypeIdList': activity,
    'FacilityLocationIdList': id,
    'DateFrom': datetime.datetime.now().astimezone().isoformat(),
    'DateTo': (datetime.datetime.now() + timedelta(days=90)).astimezone().isoformat()
    }



    json_payload = json.dumps(payload)
    response = requests.post(url, headers=headers, data=json_payload)




    for a in response.json()['Results']:
        event = Event()
        event.add("summary", a["title"])
        event.add("dtstart", datetime.datetime.strptime(a["start"], "%Y-%m-%dT%H:%M:%S"))
        event.add("dtend", datetime.datetime.strptime(a["end"], "%Y-%m-%dT%H:%M:%S"))
        event.add("dtstamp", datetime.datetime.now(tz=UTC))
        event.add("priority", 5)
        cal.add_component(event)

    response = make_response(cal.to_ical())
    response.headers["Content-Disposition"] = "attachment; filename=activites.ics"
    return response


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