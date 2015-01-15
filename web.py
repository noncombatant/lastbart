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

  PORT = 8002

  class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
      reload(lastbart)
      renderer = pystache.Renderer()
      self.send_response(200)
      self.send_header("Content-type", "text/html")
      self.send_header("Connection", "close")
      self.end_headers()
      conn = sqlite3.connect('bart.sqlite')
      if self.path == "/":
        self.wfile.write(renderer.render(lastbart.Index(conn)))
      else:
        urlified_name = self.path.strip("/").rstrip(".html")
        try:
          stop = lastbart.Stop(urlified_name)
          self.wfile.write(renderer.render(stop))
        except lastbart.StopNotFound:
          self.wfile.write("nope")

  httpd = SocketServer.TCPServer(("", PORT), MyHandler)

  print "serving at port", PORT
  httpd.serve_forever()

if __name__ == "__main__":
  main(sys.argv)
