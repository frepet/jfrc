#!/usr/bin/env python
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from time import sleep, time
import smbus

HTTP_PORT = 65520
SERIAL_HZ = 25

FAILSAFE_TIMEOUT = 0.2 # Seconds
failsafe_last = time()

state = {
	"toggles" : {
		"A" : False
	},
	"pwms" : {
		16: 127,
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
				failsafe_ping()
				for key, value in post_json.items():
					state["toggles"][key] = value

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
			

			# Validate that all the keys are correct and values are ints 
			for key, value in post_json.items():
				if type(value) != int:
					bad_request = True
					break
				if value not in range(256):
					bad_request = True
					break
				if not int(key) in state["pwms"]:
					bad_request = True
					break

			# Update all the values if request is good
			if bad_request == False:
				failsafe_ping()
				for key, value in post_json.items():
					state["pwms"][int(key)] = value

			if bad_request is True:
				self.send_response(400)
				self.send_header("Content-type", "text/plain")
				self.end_headers()
			else:
				self.send_response(200)
				self.send_header("Content-type", "application/json")
				self.end_headers()
				self.wfile.write(json.dumps(state['pwms']).encode())

def failsafe_ping():
	global failsafe_last
	failsafe_last = time()

def failsafe_time():
	global failsafe_last
	return time() - failsafe_last

def run(server_class=HTTPServer, handler_class=JFRCServer, port=HTTP_PORT):
	server_address = ('', port)
	httpd = server_class(server_address, handler_class)
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	httpd.server_close()


class I2CCommunicator:
	def __init__(self, state):
		self.bus = smbus.SMBus(1)
		self.arduino_thread = Thread(target = self.loop)
		self.state = state
		self.running = True

	def start(self):
		self.arduino_thread.start()

	def loop(self):
		while(self.running):
			# Use Toggle A as a Failsafe indicator
			state["toggles"]["A"] = failsafe_time() > FAILSAFE_TIMEOUT

			for key, val in state["pwms"].items():
				self.bus.write_byte(int(key), int(val))
				
			sleep(1/SERIAL_HZ)

	def stop(self):
		self.running = False
		self.arduino_thread.join()
		self.bus.close()


if __name__ == '__main__':
	from sys import argv
	from threading import Thread
	
	i2c = I2CCommunicator(state = state)
	i2c.start()

	if len(argv) == 2:
		run(port=int(argv[1]))
	else:
		run()

	i2c.stop()
