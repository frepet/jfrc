#!/usr/bin/env python
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from time import sleep, time
from sys import argv
from threading import Thread


HTTP_PORT = 65520

FAILSAFE_TIMEOUT = 0.5 # Seconds
failsafe_last = time()

state = {
    "toggles" : {
        "A" : False
    },
    "pwms" : {
        0: 0,
    },
}

class JFRCRestServer(BaseHTTPRequestHandler):
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
                if value not in range(0, 2500):
                    bad_request = True
                    break
                if not int(key) in state["pwms"]:
                    bad_request = True
                    break

            # Update all the values if request is good
            if bad_request == False:
                failsafe_ping()
                with open("/dev/servoblaster", "w") as sb:
                    for key, value in post_json.items():
                        self.set_pwm(int(key), int(value), sb)
                        state["pwms"][int(key)] = int(value)

            if bad_request is True:
                self.send_response(400)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
            else:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(state['pwms']).encode())

    def set_pwm(self, channel: int, value: int, servo_blaster):
            value = value//2
            print(f"{channel}={value}us", file=servo_blaster)

def failsafe_ping():
    global failsafe_last
    failsafe_last = time()

def failsafe_time():
    global failsafe_last
    return time() - failsafe_last


class Failsafe:
    def __init__(self):
        self.failsafe_thread = Thread(target = self.failsafe)
        self.running = True
        self.failsafe_thread.start()

    def failsafe(self):
        while(self.running):
            # Use Toggle A as a Failsafe indicator
            state["toggles"]["A"] = failsafe_time() > FAILSAFE_TIMEOUT
            sleep(FAILSAFE_TIMEOUT/10)

    def stop(self):
        self.running = False
        self.failsafe_thread.join()


class JFRCServer:
    def __init__(self, server_class=HTTPServer, handler_class=JFRCRestServer, port=HTTP_PORT):
        failsafe = Failsafe()

        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()

        failsafe.stop()


if __name__ == '__main__':
    if len(argv) == 2:
        jfrc_server = JFRCServer(port=int(argv[1]))
    else:
        jfrc_server = JFRCServer()

