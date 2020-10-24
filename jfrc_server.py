#!/usr/bin/env python
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

HTTP_PORT = 8081
SERIAL_PORT = "/dev/ttypACM0"

state = {
	"toggles" : {
		"led0" : False
	},
	"pwms" : {
		"pwm0" : 0.5,
		"pwm1" : 0.5,
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
				if type(value) != float:
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

if __name__ == '__main__':
	from sys import argv

	if len(argv) == 2:
		run(port=int(argv[1]))
	else:
		run()
