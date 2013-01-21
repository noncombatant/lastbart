#!/usr/bin/python

import cgi
import re
import os
import sys
import stat
import pystache
import datetime
from pysqlite2 import dbapi2 as sqlite3

def urlify_name(name):
  name = re.sub(" BART$", "", name)
  name = name.lower()
  name = re.sub("/", "-", name)
  name = re.sub("\\.", "", name)
  name = re.sub("[^0-9a-z-]", "-", name)
  return name

# Convert a time in GTFS format, e.g. "25:09:00" to a friendly format like
# "1:09 am".
def friendly_time(time_string):
  (hour, minute, second) = time_string.split(":")
  if (int(hour) / 12) % 2:
    am_pm = "pm"
  else:
    am_pm = "am"
  hour = int(hour) % 12
  if hour == 0:
    hour = 12
  return "%d:%s %s" % (hour, minute, am_pm)

class StopNotFound(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)

class Stop(object):
  def __init__(self, stop_name):
    self.conn = sqlite3.connect('bart.sqlite')

    # What a human thinks of as a single stop can be represented as multiple
    # stops in the GTFS format, e.g. MCAR and MCAR_S for north and south
    # platforms respectively. We merge these by name.
    self.all_stop_ids = []
    for (stop_id, stop_name_from_db) in get_stops(self.conn):
      if stop_name == urlify_name(stop_name_from_db):
        self.all_stop_ids.append(stop_id)
        self.stop_name = stop_name_from_db

    if len(self.all_stop_ids) == 0:
      raise StopNotFound(stop_name)
        
    super(Stop, self).__init__()

  def stop_name(self):
    return self.stop_name

  def last_valid_date(self):
    # Note: There are some localtime issues here, but given that the resolution
    # is a day, and we expect the transit feeds to have up-to-date data
    # available before they expire, this shouldn't be an issue.
    c = self.conn.execute("""SELECT end_date FROM calendar ORDER BY end_date DESC limit 1;""", ())
    return c.next()[0]

  def fetch_date(self):
    dt = datetime.datetime.fromtimestamp(os.stat("google_transit.zip")[8])
    return dt.date()

  def shortest_stop_id(self):
    return sorted(self.all_stop_ids, key=lambda x: len(x))[0]

  def service(self):
    for values in self.conn.execute("""SELECT service_id, sunday, monday,
         tuesday, wednesday, thursday, friday, saturday FROM calendar"""):
      service_id = values[0]
      # We have a bit for each weekday indicating whether this schedule is
      # visible on that day.  Zip those bits with a numerical index
      day_tuples = zip(range(0, 7), values[1:])
      # And remove the ones that are zero, so we just have the days that are
      # visible.
      visible_days_tuples = filter(lambda x: x[1] != 0, day_tuples)
      # We use this to add a set of classes to the table that control
      # visibility.
      visible_days = map(lambda x: {"day": "vd%d" % x[0]}, visible_days_tuples)

      departures = list(self.list_departures(service_id))

      if len(departures) > 0:
        yield {"service_id": service_id,
               "visible_days": visible_days,
               "departure": departures}

  def list_departures(self, service_id):
    placeholders = ",".join('?' for i in self.all_stop_ids)
    values = self.all_stop_ids + [service_id]
    c = self.conn.execute("""
        SELECT MAX(departure_time), stop_headsign, service_id
        FROM stop_times JOIN trips ON stop_times.trip_id=trips.trip_id
        WHERE stop_id in (%s) AND service_id=?
        GROUP BY stop_headsign
        ORDER by MAX(departure_time) DESC;
      """ % placeholders, values)

    for (departure_time, stop_headsign, service_id) in c:
      yield {
        "friendly_time": friendly_time(departure_time),
        "headsign": stop_headsign,
        "service_id": service_id
      }
   
def get_stops(conn):
 for (stop_id, stop_name) in conn.execute('SELECT stop_id, stop_name FROM stops ORDER BY stop_name'):
   yield (stop_id, stop_name)

class Index(object):
  def __init__(self, conn):
    self.conn = conn
    super(Index, self).__init__()

  def stop(self):
    # Record shown stops by name so we only show each stop name once. Sometimes
    # the DB has two "stops" with the same name, that actually refer to
    # different platforms of the same station.
    shown_stops = {}
    for stop_id, stop_name in get_stops(self.conn):
      if not stop_name in shown_stops:
        shown_stops[stop_name] = 1
        yield {"stop_name_urlified": urlify_name(stop_name),
               "stop_name": re.sub("BART$", "", stop_name)
               }
    

def main(argv):
  conn = sqlite3.connect('bart.sqlite')

  renderer = pystache.Renderer()

  index_html = open("html/index.html", "w")
  index_html.write(renderer.render(Index(conn)))
  index_html.close()

  for (unused, stop_name) in get_stops(conn):
    f = open("html/" + urlify_name(stop_name) + ".html", "w")
    stop = Stop(urlify_name(stop_name))
    f.write(renderer.render(stop))
    f.close()

if __name__ == "__main__":
  main(sys.argv)
