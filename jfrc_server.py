#!/usr/bin/env python
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from time import sleep
import serial

HTTP_PORT = 8081
SERIAL_PORT = "/dev/ttyACM0"
SERIAL_BAUD = 9600
SERIAL_HZ = 50

state = {
	"toggles" : {
		"led0" : False
	},
	"pwms" : {
		"a" : 127,
		"b" : 127,
	},
}

class JFRCServer(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path == "/jfrc-test":
			self.send_response(200)
			self.send_header("Content-type", "text/plain")
			self.end_headers()
			self.wfile.write("Online".encode())
		elif self.path == "/jfrc-toggles":
			self.send_response(200)
			self.send_header("Content-type", "application/json")
			self.end_headers()
			self.wfile.write(json.dumps(state['toggles']).encode())
		elif self.path == "/jfrc-pwms":
			self.send_response(200)
			self.send_header("Content-type", "application/json")
			self.end_headers()
			self.wfile.write(json.dumps(state['pwms']).encode())

	def do_POST(self):
		if self.path == "/jfrc-toggles":
			bad_request = False

			if self.headers['content-type'] != "application/json":
				bad_request = True
			
			content_length = int(self.headers['Content-Length'])
			post_data = self.rfile.read(content_length)
			post_json = json.loads(post_data.decode())
			

			# Validate that all the keys are correct and values are bools
			for key, value in post_json.items():
				if type(value) != bool:
					bad_request = True
					break
				if not key in state["toggles"]:
					bad_request = True
					break

			# Update all the values if request is good
			if bad_request == False:
				for key, value in post_json.items():
					state["toggles"][key] = value
					print("toggles, " + key + ":" + str(value))

			if bad_request is True:
				self.send_response(400)
				self.send_header("Content-type", "text/plain")
				self.end_headers()
			else:
				self.send_response(200)
				self.send_header("Content-type", "application/json")
				self.end_headers()
				self.wfile.write(json.dumps(state['toggles']).encode())

		elif self.path == "/jfrc-pwms":
			bad_request = False

			if self.headers['content-type'] != "application/json":
				bad_request = True
			
			content_length = int(self.headers['Content-Length'])
			post_data = self.rfile.read(content_length)
			post_json = json.loads(post_data.decode())
			

			# Validate that all the keys are correct and values are floats
			for key, value in post_json.items():
				if type(value) != int:
					bad_request = True
					break
				if value not in range(256):
					bad_request = True
					break
				if not key in state["pwms"]:
					bad_request = True
					break

			# Update all the values if request is good
			if bad_request == False:
				for key, value in post_json.items():
					state["pwms"][key] = value
					print("pwm, " + key + ":" + str(value))

			if bad_request is True:
				self.send_response(400)
				self.send_header("Content-type", "text/plain")
				self.end_headers()
			else:
				self.send_response(200)
				self.send_header("Content-type", "application/json")
				self.end_headers()
				self.wfile.write(json.dumps(state['pwms']).encode())


def run(server_class=HTTPServer, handler_class=JFRCServer, port=8081):
	server_address = ('', port)
	httpd = server_class(server_address, handler_class)
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	httpd.server_close()


class SerialCommunicator:
	STX = 2
	ETX = 3
	def __init__(self, port, baud, state):
		self.serial = serial.Serial(port, baud, timeout=0)
		self.arduino_thread = Thread(target = self.loop)
		self.state = state
		self.running = True

	def start(self):
		self.arduino_thread.start()

	def loop(self):
		while(self.running):
			for key, val in state["pwms"].items():
				self.serial.write(b"%c%c%c%c" % (self.STX, ord(key), int(val), self.ETX))
			sleep(1/SERIAL_HZ)

	def stop(self):
		self.running = False
		self.arduino_thread.join()
		self.serial.close()


if __name__ == '__main__':
	from sys import argv
	from threading import Thread
	
	sc = SerialCommunicator(port = SERIAL_PORT, baud = SERIAL_BAUD, state = state)
	sc.start()

	if len(argv) == 2:
		run(port=int(argv[1]))
	else:
		run()

	sc.stop()
