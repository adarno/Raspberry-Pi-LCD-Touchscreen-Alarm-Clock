from PyQt4 import QtCore
import time
import datetime
import os
import signal
import subprocess
import pygame

from server import CommunicationHandler


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

    onAlarm = QtCore.pyqtSignal(int)
    removeAlarm = QtCore.pyqtSignal(int)

    def __init__(self, id):
        super(AlarmClockThread, self).__init__()
        self.alarm_time = ""
        self.stop_request = False
        self.repeat = False
        self.id = id
        self.btnStop = None
        self.layout = None

    def set_alarm(self, alarm_time):
        self.alarm_time = alarm_time

    def abort(self):
        print("alarm " + str(self.id) + " aborted.")
        self.stop_request = True
        self.removeAlarm.emit(self.id)

    def run(self):
        print("started alarm thread")
        while not self.stop_request:
            current_time = str(datetime.datetime.today().strftime("%H : %M"))
            if current_time == self.alarm_time:
                self.onAlarm.emit(self.id)
                if not self.repeat:
                    break
            time.sleep(5)
        self.abort()

class SnoozeThread(QtCore.QThread):

    onAlarm = QtCore.pyqtSignal(int)

    def __init__(self, main, alarm_id):
        super(SnoozeThread, self).__init__()
        self.alarm_id = alarm_id

    def run(self):
        time.sleep(60)
        self.onAlarm.emit(self.alarm_id)



class SoundThread(QtCore.QThread):

    def __init__(self, sound):
        super(SoundThread, self).__init__()
        self.sound = sound  # path to sound
        self.player = None  # player object
        #self.lock = QtCore.QMutex()

    def run(self):
        # start sound play back
        #self.lock.lock()
        self.pro = subprocess.Popen("cvlc " + self.sound, stdout=subprocess.PIPE,
                               shell=True, preexec_fn=os.setsid)
        #self.lock.unlock()

    def stop(self):
        # stop current sound playback
        os.killpg(os.getpgid(self.pro.pid), signal.SIGTERM)  # Send the signal to all the process groups


class CommandsThread(QtCore.QThread):

    """ Listens for incoming commands on HTTP server."""

    onChangeScreen = QtCore.pyqtSignal()

    def __init__(self, main_window):
        super(CommandsThread, self).__init__()
        self.main_window = main_window

    def run(self):

        while True:
            if CommunicationHandler.changeScreen:
                # change screen
                print("changing screen")
                try:
                    self.onChangeScreen.emit()
                except:
                    self.main_window.onScreenOff()
                CommunicationHandler.changeScreen = False
            time.sleep(0.1)

