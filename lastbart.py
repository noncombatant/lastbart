#!/usr/bin/python

from pysqlite2 import dbapi2 as sqlite3
import cgi
import re
import os
import sys
import pystache

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

class Stop(pystache.View):
  def __init__(self, stop_id, stop_name, last_valid_date):
    self.stop_name = stop_name
    self.stop_id = stop_id
    self.last_valid_date = last_valid_date
    self.conn = sqlite3.connect('bart.sqlite')
    super(Stop, self).__init__()

  def stop_name(self):
    return self.stop_name

  def last_valid_date(self):
    return self.last_valid_date

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
    c = self.conn.cursor()
    c.execute("""
        SELECT MAX(departure_time), stop_headsign, service_id
        FROM stop_times JOIN trips ON stop_times.trip_id=trips.trip_id
        WHERE stop_id=? AND service_id=?
        GROUP BY stop_headsign
        ORDER by MAX(departure_time) DESC;
      """, (self.stop_id, service_id))

    for (departure_time, stop_headsign, service_id) in c:
      yield {
        "friendly_time": friendly_time(departure_time),
        "headsign": stop_headsign,
        "service_id": service_id
      }
   
def last_valid_date(conn):
  # Note: There are some localtime issues here, but given that the resolution
  # is a day, and we expect the transit feeds to have up-to-date data
  # available before they expire, this shouldn't be an issue.
  c = conn.execute("""SELECT end_date FROM calendar ORDER BY end_date DESC limit 1;""", ())
  return c.next()[0]

def get_stops(conn):
 for (stop_id, stop_name) in conn.execute('SELECT stop_id, stop_name FROM stops ORDER BY stop_name'):
   yield (stop_id, stop_name)

class Index(pystache.View):
  def __init__(self, conn):
    self.conn = conn
    super(Index, self).__init__()

  def stop(self):
    for stop_id, stop_name in get_stops(self.conn):
      yield {"stop_name_urlified": urlify_name(stop_name),
             "stop_name": re.sub("BART$", "", stop_name)
             }
    

def main(argv):
  conn = sqlite3.connect('bart.sqlite')

  index_html = open("html/index.html", "w")
  index_html.write(Index(conn).render())
  index_html.close()

  for (stop_id, stop_name) in get_stops(conn):
    f = open("html/" + urlify_name(stop_name) + ".html", "w")
    stop = Stop(stop_id, stop_name, last_valid_date(conn))
    f.write(stop.render())
    f.close()

if __name__ == "__main__":
  main(sys.argv)
