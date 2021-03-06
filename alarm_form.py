import sys
import os
import subprocess
import time
from PyQt4 import QtGui, QtCore
from raspi_threads import AlarmClockThread, SnoozeThread
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


class SnoozeWindow(QtGui.QWidget):

    def __init__(self, main, sound_thread, alarm_id):
        QtGui.QWidget.__init__(self)
        self.main = main
        self.sound_thread = sound_thread
        self.alarm_id = alarm_id
        self.snooze_obj = None

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        self.btnOK = QtGui.QPushButton('Stop', self)
        self.btnOK.clicked.connect(self.stop)
        grid.addWidget(self.btnOK, 1, 0)

        self.btnQuit = QtGui.QPushButton("Snooze", self)
        self.btnQuit.clicked.connect(self.snooze)
        grid.addWidget(self.btnQuit, 2, 0)

        self.setLayout(grid)

        self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('New Alarm')
        self.show()

    def stop(self):
        # stop alarm
        #self.sound_thread.stop()

        # turn radio off
        try:
            os.system("sudo ./codesend 1397844,, -l 445 -p 0")
        except:
            print >> sys.stderr, "Could not turn off radio!"

        # close window
        self.close()

        # remove alarm from alarm tabs
        self.main.on_alarm_removed(self.alarm_id)

    def snooze(self):
        # stop alarm
        #self.sound_thread.stop()

        # turn radio off
        try:
            os.system("sudo ./codesend 1397844,, -l 445 -p 0")
        except:
            print >> sys.stderr, "Could not turn off radio!"



        # restart alarm in specified time
        self.snooze_obj = SnoozeThread(self.main, self.alarm_id)
        self.snooze_obj.onAlarm.connect(self.main.on_alarm)
        self.snooze_obj.start()

        # close window
        self.close()

