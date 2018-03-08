import sys
from PyQt4 import QtGui, QtCore
from raspi_threads import AlarmClockThread
from alarm_window import Ui_Alarm_window


class AlarmForm(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.btn = QtGui.QPushButton("OK", self)


    def add_alarm(self):
        alarm_id = len(self.main_window.alarms)
        alarm = AlarmClockThread(alarm_id)
        self.main_window.alarms.append(alarm)
        self.main_window.alarms[alarm_id].set_alarm("21:01")
        self.main_window.alarms[alarm_id].onAlarm.connect(self.main_window.on_alarm)
        self.main_window.alarms[alarm_id].start()

        self.close()

    def quit(self):
        self.close()
