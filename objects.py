import datetime
from dateutil import parser

class Facility:
    def __init(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return f"{self.name}"

class Activity:
    def __init__(self, title, start, end, facility, location, available, capacity):
        self.title = title
        self.start = parser.parse(start)
        self.end = parser.parse(end)
        self.facility = facility
        self.location = location
        self.available = available
        self.capacity = capacity
        self.startshort = datetime.datetime.strftime(self.start, "%a %-d %b %-H:%M")
        self.endshort = datetime.datetime.strftime(self.end, "%a %-d %b %-H:%M")
        self.duration = int(round((self.end - self.start).total_seconds() / 60,0))

    def __str__(self):
        return f"{self.title} ({self.startshort}, {self.duration} mins)"

