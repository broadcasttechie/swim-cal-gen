from flask import Flask, send_file, make_response, jsonify
from flask import request
from flask import render_template
import requests
import json
import datetime
from datetime import  timedelta
from icalendar import Calendar, Event, Timezone
from pytz import UTC
import pytz
from flask_bootstrap import Bootstrap
from dateutil import parser

from objects import Activity, Facility

def get_events(facility, activity, days=30):
    url = 'https://birminghamleisure.legendonlineservices.co.uk/birmingham_comm_rg_home/Timetable/GetClassTimeTable'
    headers = { 'Content-Type': 'application/json' }
    payload = {
    'ResourceSubTypeIdList': activity,
    'FacilityLocationIdList': facility,
    'DateFrom': datetime.datetime.now().replace(hour=0,minute=0,second=0,microsecond=0).astimezone().isoformat(),
    'DateTo': (datetime.datetime.now().replace(hour=0,minute=0,second=0,microsecond=0) + timedelta(days=days+1)).astimezone().isoformat()
    }
    json_payload = json.dumps(payload)
    activities = []
    response = requests.post(url, headers=headers, data=json_payload)
    for a in response.json()['Results']:
        act = Activity(a['title'], a['start'], a['end'], a['FacilityName'], 4811, a['AvailableSlots'], a['Capacity'] )
        activities.append(act)
    return activities


def get_locations():
    return

def get_activities():
    return

def create_app():
  app = Flask("app")
  Bootstrap(app)

  return app


app = create_app()

@app.template_filter()
def format_datetime(value, format='medium'):
    if format == 'full':
        format="%a %-d %b %-H:%M"
    elif format == 'medium':
        format="%a %-d %b %-H:%M"
    timestamp = datetime.datetime.strftime(parser.parse(value), format)
    return timestamp.format(format)


@app.route("/")
def index():
    url = "https://birminghamleisure.legendonlineservices.co.uk/birmingham_comm_rg_home/filteredlocationhierarchy"
    headers = { 'Content-Type': 'application/json' }
    response = requests.get(url, headers=headers)
    return render_template('home.html', sites = response.json())


@app.route('/facility/<id>')
def facility(id):
    url = f"https://birminghamleisure.legendonlineservices.co.uk/birmingham_comm_rg_home/Bookings/ActivitySubTypes?LocationIds={id}&ReturnAll=true&ResourceSubTypeCategoryId="
    headers = { 'Content-Type': 'application/json' }
    response = requests.get(url, headers=headers)
    return render_template('facility.html', data=response.json(), facility=id)


@app.route('/facility/<id>/events')
def activites(id):
    activities = request.args.getlist('activity')
    results = get_events(id, activities)
    return render_template('events.html', data=results, facility=id)



###########GENERATE ICALENDAR FILE

@app.route('/facility/<id>/events.ics')
def activity_ical(id):

    activities = request.args.getlist('activity')
    days = request.args.getlist('days')
    days = int(days[0] if days else 30)
    
    cal = Calendar()
    cal.add("prodid", "-//leisurecalendar//")
    cal.add("version", "2.0")

    timezone = Timezone()
    timezone.add('TZID', 'Europe/London')
    timezone.to_ical()
    cal.add_component(timezone)

    results = get_events(id, activities, days)

    for a in results:
        event = Event()
        event.add("summary", f"{a.title}")
        event.add("dtstart", a.start)#, tzinfo=pytz.timezone("Europe/London"))
        event.add("dtend", a.end)
        event.add("dtstamp", datetime.datetime.now(tz=UTC))
        event.add("priority", 5)
        event.add("description", f"{a.available}/{a.capacity}\n{a.facility}")
        event.add("LOCATION", a.location)
        cal.add_component(event)

    response = make_response(cal.to_ical())
    if app.debug != True: 
        response.headers['Content-Disposition'] = "attachment; filename=activites.ics"
    return response


