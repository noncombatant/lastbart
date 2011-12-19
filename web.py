#!/usr/bin/python

from pysqlite2 import dbapi2 as sqlite3
import cgi
import re
import os
import sys
import pystache
import lastbart

def main(argv):
  import SimpleHTTPServer
  import SocketServer

  PORT = 8000

  class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
      reload(lastbart)
      self.send_response(200)
      self.send_header("Content-type", "text/html")
      self.end_headers()
      conn = sqlite3.connect('bart.sqlite')
      if self.path == "/":
        self.wfile.write(lastbart.generate_index(conn))
      else:
        urlified_name = self.path.strip("/").rstrip(".html")
        for (stop_id, stop_name) in lastbart.get_stops(conn):
          if urlified_name == lastbart.urlify_name(stop_name):
            stop = lastbart.Stop(stop_id, stop_name, lastbart.last_valid_date(conn))
            self.wfile.write(stop.render())

  httpd = SocketServer.TCPServer(("", PORT), MyHandler)

  print "serving at port", PORT
  httpd.serve_forever()

if __name__ == "__main__":
  main(sys.argv)
