""" server.py

    Handles communication with Android app.
"""

import SimpleHTTPServer
import SocketServer
from urlparse import urlparse, parse_qs
from PyQt4 import QtCore
import threading

PORT = 8760


class CommunicationHandler:
    changeScreen = False


class CallbackServer(QtCore.QThread):

    def __init__(self):
        super(CallbackServer, self).__init__()

    def run(self):
        """Start the server."""
        server_address = ("192.168.188.21", PORT)
        server = SocketServer.TCPServer(server_address, TestHandler)
        server.serve_forever()

        print ("Exiting " + self.name)


class TestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """The test example handler."""

    def do_POST(self):
        """Handle a post request"""
        #print(self.headers)
        #length = int(self.headers.get_all('content-length')[0])
        #print(self.headers.get_all('content-length'))
        data_string = self.rfile.read()
        print(data_string.decode())
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Allow-Control-Methods", "GET, POST, OPTIONS, HEAD")
        self.end_headers()
        #self.flush_headers()
        self.wfile.write("This is the response!".encode())

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")

    def do_GET(self):

        parsed = urlparse(self.path)
        code = parse_qs(parsed.query)['q']
        code = code[0]

        if code == "screen":
            print("set screen " + str(not CommunicationHandler.changeScreen))
            CommunicationHandler.changeScreen = not CommunicationHandler.changeScreen


        self.send_response(200, 'OK')
        self.send_header('Content-type', 'html')
        self.end_headers()
        self.wfile.write("worked".encode())
