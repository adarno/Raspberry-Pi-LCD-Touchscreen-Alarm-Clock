import sys
from PyQt4 import QtGui, QtCore
from raspi_threads import AlarmClockThread


class AlarmForm(QtGui.QWidget):


    def __init__(self, main_window):
        super(AlarmForm, self).__init__()

        self.main_window = main_window

        # set layout
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        # buttons
        self.btnOK = QtGui.QPushButton('OK', self)
        self.btnOK.clicked.connect(self.add_alarm)
        grid.addWidget(self.btnOK, 4, 0)

        self.btnQuit = QtGui.QPushButton("Abbrechen", self)
        self.btnQuit.clicked.connect(self.quit)
        grid.addWidget(self.btnQuit, 4, 1)

        # lable
        self.label_hour = QtGui.QLabel("00 : 00", self)
        self.label_hour.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        self.label_hour.setAlignment(QtCore.Qt.AlignCenter)

        grid.addWidget(self.label_hour, 2, 1)

        self.setLayout(grid)

        self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('New Alarm')
        self.show()

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
