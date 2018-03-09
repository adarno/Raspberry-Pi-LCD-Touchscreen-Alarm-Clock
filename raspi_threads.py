from PyQt4 import QtCore
import time
import datetime


class MyThread(QtCore.QThread):
    timeElapsed = QtCore.pyqtSignal()
    quitThread = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(MyThread, self).__init__(parent)
        self.stop_request = False

    def quit(self):
        self.stop_request = True

    def run(self):
        while not self.stop_request:
            self.timeElapsed.emit()
            time.sleep(1)
        self.quitThread.emit()

class StopWatchThread(QtCore.QThread):
    secondElapsed = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(StopWatchThread, self).__init__(parent)
        self.stop_request = False
        self.count = 0
        self.is_running = False
        self.resume = False

    def quit(self):
        self.stop_request = True

    def go(self):
        if self.resume:
            self.start()
        else:
            self.count = 0
            self.start()

    def reset(self):
        self.count = 0

    def run(self):
        while not self.stop_request:
            time.sleep(0.1)
            self.count += 1
            if self.count % 10 == 0:
                self.secondElapsed.emit(self.count/10)
        self.stop_request = False
        self.is_running = False



class TimerThread(QtCore.QThread):
    secondElapsed = QtCore.pyqtSignal(int)
    onFinished = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(TimerThread, self).__init__(parent)
        self.stop_request = False
        self.count = 0
        self.start_count = 0
        self.is_running = False
        self.resume = False
        self.reset_to_zero = False

    def pause(self):
        print("in pause()")
        self.stop_request = True
        self.resume = True

    def go(self, count):
        if self.resume:
            print("resuming " + str(self.count))
            self.start()
        else:
            self.count = 10 * count
            self.start_count = self.count
            self.start()
        self.is_running = True
        print("starting timer with count: " + str(self.count))

    def reset(self):
        self.count = self.start_count
        if not self.stop_request:
            self.start_count = 0
            self.count = 0
            self.reset_to_zero = False

    def run(self):
        while not self.stop_request and self.count > 0:
            time.sleep(0.1)
            self.count -= 1
            if self.count % 10 == 0:
                self.secondElapsed.emit(self.count / 10)

        self.stop_request = False
        self.is_running = False
        if self.count == 0:
            self.onFinished.emit()
            self.resume = False


class AlarmClockThread(QtCore.QThread):

    onAlarm = QtCore.pyqtSignal()

    def __init__(self, id):
        super(AlarmClockThread, self).__init__()
        self.alarm_time = ""
        self.stop_request = False
        self.repeat = False
        self.id = id
        self.btnStop = None

    def set_alarm(self, alarm_time):
        self.alarm_time = alarm_time

    def abort(self):
        print("alarm " + str(self.id) + " aborted.")
        self.stop_request = True

    def run(self):
        print("started alarm thread")
        while not self.stop_request:
            current_time = str(datetime.datetime.today().strftime("%H : %M"))
            if current_time == self.alarm_time:
                self.onAlarm.emit()
                if not self.repeat:
                    break
            time.sleep(5)
