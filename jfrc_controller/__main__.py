"""
Python program to control a JF-RC Robot using a gamepad.

Author: Fredrik Peteri, fredrik@peteri.se
"""
import threading

from PySide2.QtCore import Slot, Qt, QUrl
from PySide2.QtWidgets import *
from PySide2.QtWebEngineWidgets import QWebEngineView
from sys import argv

from JFRCModel import JFRCModel
from JFRCRobotConnection import JFRCRobotConnection

camera_size = (800, 600)
keymap = {
	"turn_left": Qt.Key_A,
	"turn_right": Qt.Key_D,
	"turn_center": Qt.Key_C,
}


class JFRCController(QWidget):
	jfrc_robot_connection = None
	is_connected = False
	jfrc_model = JFRCModel()

	def __init__(self):
		super().__init__()

		# Prepare update thread for sending commands to robot
		self.update_thread = None

		# Set up the main window
		self.setWindowTitle("JF-RC Controller")
		self.setGeometry(0, 0, 1000, 1000)

		# Add the 'Connect' button
		connect_button = QPushButton(parent=self, text="Connect")
		connect_button.released.connect(self.connect_dialog)
		connect_button.show()

		# Add the Current URL label
		self.current_url = QLabel(parent=self, text="")
		self.current_url.show()

		# Add camera view
		self.camera = QWebEngineView()
		self.camera.width = camera_size[0]
		self.camera.height = camera_size[1]
		self.camera.show()

		# Add slider for the steering
		self.steering_indicator = QSlider(orientation=Qt.Horizontal)
		self.steering_indicator.setRange(0, 255)
		self.steering_indicator.show()
		self.steering_indicator.setEnabled(False)
		self.jfrc_model.steering_updated.connect(lambda val: self.steering_indicator.setValue(val))

		# Set the layout of the main window
		main_layout = QGridLayout()
		main_layout.addWidget(connect_button, 0, 0)
		main_layout.addWidget(self.current_url, 0, 1)
		main_layout.addWidget(self.camera, 1, 0, 1, 2)
		main_layout.addWidget(self.steering_indicator, 2, 0, 1, 2)
		self.setLayout(main_layout)
		self.show()

	def show_camera(self, url=""):
		self.camera.load(QUrl(f"http://{url}:8080"))

	def keyPressEvent(self, event):
		if event.isAutoRepeat() or not self.is_connected:
			return

		key_press = {
			keymap["turn_left"]: self.jfrc_model.left,
			keymap["turn_right"]: self.jfrc_model.right,
			keymap["turn_center"]: self.jfrc_model.center,
		}

		if event.key() in key_press:
			key_press[event.key()]()

	def keyReleaseEvent(self, event):
		if event.isAutoRepeat() or not self.is_connected:
			return

		key_release = {
			keymap["turn_left"]: self.jfrc_model.left_stop,
			keymap["turn_right"]: self.jfrc_model.right_stop,
			keymap["turn_center"]: self.jfrc_model.center_stop,
		}

		if event.key() in key_release:
			key_release[event.key()]()

	def start_updates(self):
		self.update_thread = threading.Thread(target=self.jfrc_robot_connection.start)
		self.update_thread.start()

	def stop_updates(self):
		self.jfrc_robot_connection.stop()
		self.update_thread.join()

	@Slot()
	def connect_dialog(self):
		"""
		Triggers when the user clicks the 'Connect' button, will try to set up a connection with an JF-RC Robot
		"""
		text, ok = QInputDialog().getText(self, "Connect", "URL", QLineEdit.Normal)
		if ok and text:
			try:
				self.jfrc_robot_connection = JFRCRobotConnection(model=self.jfrc_model, url=text)
				self.current_url.setText(f"Connected to: {text}")
				self.is_connected = True
				self.show_camera(text)
				self.start_updates()
			except RuntimeError as e:
				self.current_url.setText(str(e))


if __name__ == '__main__':
	app = QApplication(argv)
	jfrc_controller = JFRCController()

	app.exec_()
	jfrc_controller.stop_updates()
