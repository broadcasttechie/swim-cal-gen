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


locationscache = {}

def default_arg(arg, default):
    if arg:
        if arg[0] != '':
            arg = int(arg[0])
        else:
            arg = default
    else:
        arg = default
    return arg


def get_events(facility, activity, days=30):
    url = 'https://birminghamleisure.legendonlineservices.co.uk/birmingham_comm_rg_home/Timetable/GetClassTimeTable'
    headers = { 'Content-Type': 'application/json' }
    payload = {
    'ResourceSubTypeIdList': activity,
    'FacilityLocationIdList': facility,
    'DateFrom': datetime.datetime.now().replace(hour=0,minute=0,second=0,microsecond=0).astimezone().isoformat(),
    'DateTo': (datetime.datetime.now().replace(hour=0,minute=0,second=0,microsecond=0) + timedelta(days=days+1)).astimezone().isoformat()
    }
    #print(payload)
    json_payload = json.dumps(payload)
    activities = []
    response = requests.post(url, headers=headers, data=json_payload)
    for a in response.json()['Results']:
        act = Activity(a['title'], a['start'], a['end'], a['FacilityName'], facility, a['AvailableSlots'], a['Capacity'] )
        activities.append(act)
    return activities


def get_locations():
    url = "https://birminghamleisure.legendonlineservices.co.uk/birmingham_comm_rg_home/filteredlocationhierarchy"
    headers = { 'Content-Type': 'application/json' }
    response = requests.get(url, headers=headers)
    resp = response.json()
    # print(resp)
    # print("======")
    return resp

def get_location_name(id):
    global locationscache
    if id in locationscache:
        #print(id)
        return locationscache[id]
    else:
        raw = get_locations()
        locations = {}
        for r in raw:
            group = r['Name']
            if len(r['Children']) > 0:
                for c in r['Children']:
                    locations[c['Id']] = { "name" : c['Name'], "group" : group}
        
        look = int(id)
        locationscache = locations
        # print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        # print(locations)
        # print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        return locations[look]

def get_activities():
    return

def clean_location(location,facility):
    return location.replace(f"{facility} - ","")

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

@app.template_filter()
def name_cleaner(value):
    value = value.replace("_"," ")
    value = value.replace(" RG","")
    return value

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
    return render_template('facility.html', data=response.json(), facility=id, facilityname=get_location_name(id))


@app.route('/facility/<id>/events')
def events(id):
    activities = request.args.getlist('activity')
    days = default_arg(request.args.getlist('days'), 14)

    results = get_events(id, activities, days)
    return render_template('events.html', data=results, facility=id, activity=activities, days=days, facilityname=get_location_name(id))



###########GENERATE ICALENDAR FILE

@app.route('/facility/<id>/events.ics')
def events_ical(id):

    activities = request.args.getlist('activity')
    days = default_arg(request.args.getlist('days'), 30)
    
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
        event.add("description", f"{a.available}/{a.capacity}\n{clean_location(a.facility,get_location_name(a.location)['name'])}")
        event.add("LOCATION", get_location_name(a.location)['name'])
        cal.add_component(event)

    response = make_response(cal.to_ical())
    if app.debug != True: 
        response.headers['Content-Disposition'] = "attachment; filename=activites.ics"
    return response


