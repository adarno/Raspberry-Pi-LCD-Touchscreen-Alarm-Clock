import sys
from PyQt4 import QtGui, QtCore
from raspi_threads import AlarmClockThread
from alarm_window import Ui_Alarm_window


class AlarmForm(QtGui.QDialog, Ui_Alarm_window):

    def __init__(self, main_window):
        QtGui.QWidget.__init__(self)

        self.main_window = main_window

        self.ui = Ui_Alarm_window()
        self.ui.setupUi(self)
        self.ui.btnOK.setDefault(True)

        self.ui.btnOK.clicked.connect(self.add_alarm)
        self.ui.btnQuit.clicked.connect(self.quit)

        self.ui.btnHourPlus.clicked.connect(self.hour_plus)
        self.ui.btnHourMinus.clicked.connect(self.hour_min)
        self.ui.btnMinPlus.clicked.connect(self.min_plus)
        self.ui.btnMinMinus.clicked.connect(self.min_min)

        self.timeM = 0
        self.timeH = 0

        self.show()

    def show_wake_time(self):

        minutes = self.timeM % 60
        hours = self.timeH % 24


        if minutes < 10:
            minutes = "0"+str(minutes)
        if hours < 10:
            hours = "0"+str(hours)

        self.ui.label_wake_time.setText(str(hours)+" : "+str(minutes))

    def hour_plus(self):
        self.timeH += 1
        self.show_wake_time()

    def hour_min(self):
        if self.timeH > 0:
            self.timeH -= 1
        self.show_wake_time()

    def min_plus(self):
        self.timeM += 1
        self.show_wake_time()

    def min_min(self):
        if self.timeM > 0:
            self.timeM -= 1
        self.show_wake_time()


    def add_alarm(self):
        alarm_id = len(self.main_window.alarms)
        alarm = AlarmClockThread(alarm_id)
        self.main_window.alarms.append(alarm)
        self.main_window.alarms[alarm_id].set_alarm(self.ui.label_wake_time.text())
        self.main_window.alarms[alarm_id].onAlarm.connect(self.main_window.on_alarm)
        self.main_window.alarms[alarm_id].start()
        self.main_window.on_alarm_added(alarm_id)

        self.close()

    def quit(self):
        self.close()
