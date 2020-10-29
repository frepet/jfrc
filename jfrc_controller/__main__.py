"""
Python program to control a JF-RC Robot using a gamepad.

Author: Fredrik Peteri, fredrik@peteri.se
"""
from PySide2.QtCore import Slot, Qt
from PySide2.QtWidgets import *
from sys import argv

from JFRCRobotConnection import JFRCRobotConnection


keymap = {
	"turn_left": Qt.Key_A,
	"turn_right": Qt.Key_D
}


class JFRCController(QWidget):
	jfrc_robot_connection = None
	is_connected = False

	def __init__(self):
		super().__init__()
		# Set up the main window
		self.setWindowTitle("JF-RC Controller")

		# Add the 'Connect' button
		connect_button = QPushButton(parent=self, text="Connect")
		connect_button.released.connect(self.connect_dialog)
		connect_button.show()

		# Add the Current URL label
		self.current_url = QLabel(parent=self, text="")
		self.current_url.show()

		# Set the layout of the main window
		main_layout = QGridLayout()
		main_layout.addWidget(connect_button, 0, 0)
		main_layout.addWidget(self.current_url, 0, 1)
		self.setLayout(main_layout)
		self.show()

	def keyPressEvent(self, event):
		if event.isAutoRepeat() or not self.is_connected:
			return

		key_press = {
			keymap["turn_left"]: self.jfrc_robot_connection.steering_left,
			keymap["turn_right"]: self.jfrc_robot_connection.steering_right
		}

		if event.key() in key_press:
			key_press[event.key()]()

	def keyReleaseEvent(self, event):
		if event.isAutoRepeat() or not self.is_connected:
			return

		key_release = {
			keymap["turn_left"]: self.jfrc_robot_connection.steering_forward,
			keymap["turn_right"]: self.jfrc_robot_connection.steering_forward
		}

		if event.key() in key_release:
			key_release[event.key()]()

	@Slot()
	def connect_dialog(self):
		"""
		Triggers when the user clicks the 'Connect' button, will try to set up a connection with an JF-RC Robot
		"""
		text, ok = QInputDialog().getText(self, "Connect", "URL", QLineEdit.Normal)
		if ok and text:
			try:
				self.jfrc_robot_connection = JFRCRobotConnection(url=text)
				self.current_url.setText(f"Connected to: {text}")
				self.is_connected = True
			except RuntimeError as e:
				self.current_url.setText(str(e))


if __name__ == '__main__':
	app = QApplication(argv)
	jfrc_controller = JFRCController()

	app.exec_()
