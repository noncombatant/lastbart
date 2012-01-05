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

  PORT = 8001

  class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def sendheaders(self, code, type):
      self.send_response(code)
      self.send_header("Content-type", type)
      self.send_header("Connection", "close")
      self.end_headers()

    def do_GET(self):
      reload(lastbart)
      
      conn = sqlite3.connect('bart.sqlite')
      if self.path == "/":
        self.sendheaders(200, "text/html")
        self.wfile.write(lastbart.Index(conn).render())
      else:
        urlified_name = self.path.strip("/")
        urlified_name = re.sub(r"\.html$", "", urlified_name)
        try:
          stop = lastbart.Stop(urlified_name)
          self.sendheaders(200, "text/html")
          self.wfile.write(stop.render())
        except lastbart.StopNotFound:
          # Hack: return a bare file. Not necesarily safe but we only listen on
          # localhost.
          file = "html/" + re.sub(r"\.\.", "", urlified_name)
          try:
            contents = open(file).read()
            self.sendheaders(200, "")
            self.wfile.write(contents)
          except IOError:
            self.sendheaders(404, "text/plain")
            self.wfile.write("Fourohfour")

  httpd = SocketServer.TCPServer(("127.0.0.1", PORT), MyHandler)

  print "serving at port", PORT
  httpd.serve_forever()

if __name__ == "__main__":
  main(sys.argv)
