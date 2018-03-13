
import sys
import os
import subprocess

try:
    from PyQt4 import QtCore, QtGui, uic
except:
    print >> sys.stderr, "PyQt4 not installed\n"

from raspi_threads import MyThread, TimerThread, StopWatchThread, SoundThread
from alarm_form import AlarmForm, SnoozeWindow
import datetime
from alarm_window import Ui_Alarm_window

try:
    import rpi_backlight as bl
except:
    print >> sys.stderr, "Python modlue 'rpi_backlight' not installed." \
                         "\nVisit https://github.com/linusg/rpi-backlight.git to install."

# convert mainwindow.ui to pyhton
qtCreatorFile = "mainwindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MyApp(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        #self.showFullScreen()      # show window in full screen
        self.setWindowTitle("Clock")
        self.setupUi(self)
        try:
            print(bl.get_power())
        except:
            print("could not get power")

        # settings for widgets
        # buttons settings
        self.btnScreenOff.clicked.connect(self.onScreenOff)
        self.btnQuit.clicked.connect(self.onQuit)
        self.wifi_enabled = True
        self.btnWifi.clicked.connect(self.on_wifi_btn)

        # intialize slider
        self.brightnessSlider.setMinimum(12)
        self.brightnessSlider.setMaximum(255)
        try:
            self.brightnessSlider.setValue(bl.get_actual_brightness())
        except:
            print("could not get brightness")

        self.brightnessSlider.valueChanged.connect(self.on_update_brightness)

        # clock
        #self.labelTime.clicked.connect(self.onScreenOff())
        #self.labelDate.clic

        # buttons stop watch
        self.btnStartStopWatch.clicked.connect(self.startStopWatch)
        self.stopWatchrunning = False
        self.btnResetStopWatch.clicked.connect(self.resetStopWatch)

        # variables timer
        self.timerH = 0
        self.timerM = 0
        self.timerS = 0

        # buttons timer
        self.btnHourPlus.clicked.connect(self.hour_plus)
        self.btnHourMin.clicked.connect(self.hour_min)
        self.btnMinPlus.clicked.connect(self.min_plus)
        self.btnMinMin.clicked.connect(self.min_min)
        self.btnSecPlus.clicked.connect(self.sec_plus)
        self.btnSecMin.clicked.connect(self.sec_min)

        # set timer buttons checkable
        self.btnHourPlus.setCheckable(True)

        self.btnTimer.clicked.connect(self.start_timer)
        self.btnTimerReset.clicked.connect(self.reset_timer)

        # buttons alarm
        self.btnNewAlarm.clicked.connect(self.new_alarm)
        self.alarms = []

        ### threads ####

        # clock thread
        self.myThread = MyThread(self)
        self.myThread.timeElapsed.connect(self.on_myThread_updateTime)
        self.myThread.quitThread.connect(self.exit)
        self.myThread.start()

        # stopwatch thread
        self.stopWatchThread = StopWatchThread()
        self.stopWatchThread.secondElapsed.connect(self.onSecondElapsed)

        # timer thread
        self.timerThread = TimerThread()
        self.timerThread.secondElapsed.connect(self.onTimerSecondElapsed)
        self.timerThread.onFinished.connect(self.timer_finished)

        # sound
        self.sound_thread = None

    ##### Uhr  #####
    @QtCore.pyqtSlot(int)
    def on_myThread_updateTime(self):
        self.labelDate.setText(str(datetime.date.today().strftime("%a %b %d %Y")))
        self.labelTime.setText(str(datetime.datetime.today().strftime("%H:%M:%S")))

    ##### Wecker  #####

    def new_alarm(self):

        # open new window to set alarm

        self.alarm_wind = AlarmForm(self)

    def on_alarm_added(self, alarm_id):
        # display alarms

        # add horizontal layout to tabs containing time and stop button
        self.alarms[alarm_id].layout = QtGui.QHBoxLayout()

        self.verticalLayout_7.addLayout(self.alarms[alarm_id].layout)

        self.alarms[alarm_id].alarm_label = QtGui.QLabel(self.alarms[alarm_id].alarm_time, self)
        self.alarms[alarm_id].btnStop = QtGui.QPushButton("Stop", self)
        self.alarms[alarm_id].btnStop.clicked.connect(self.alarms[alarm_id].abort)
        self.alarms[alarm_id].removeAlarm.connect(self.on_alarm_removed)
        self.alarms[alarm_id].layout.addWidget(self.alarms[alarm_id].alarm_label)
        self.alarms[alarm_id].layout.addWidget(self.alarms[alarm_id].btnStop)

    def on_alarm_removed(self, alarm_id):
        print("removing")
        self.alarms[alarm_id].btnStop.deleteLater()
        self.alarms[alarm_id].alarm_label.deleteLater()
        self.alarms[alarm_id].layout.deleteLater()

    def on_alarm(self, alarm_id):

        print("alarm")
        # turn screen on
        try:
            bl.set_power(True)
            bl.set_power(True)
        except:
            print >> sys.stderr, "could not turn screen on"

        # play sound
        self.sound_thread = SoundThread("sounds/alarm1.m4a")
        self.sound_thread.start()

        # open window to stop alarm or snooze
        self.snooze = SnoozeWindow(self, self.sound_thread)




    ##### Stoppuhr ######

    def onSecondElapsed(self, count):
        seconds = count % 60
        minutes  = count/60
        hours    = count/3600

        if seconds < 10:
            seconds = "0"+str(seconds)
        if minutes < 10:
            minutes = "0"+str(minutes)
        if hours < 10:
            hours = "0"+str(hours)

        self.labelStop.setText(str(hours)+" : "+str(minutes)+" : "+str(seconds))

    def startStopWatch(self):
        if not self.stopWatchThread.is_running:
            print("starting stop watch")
            self.stopWatchThread.go()
            self.stopWatchThread.is_running = True
            self.btnStartStopWatch.setText("Stop")
        else:
            print("stopping stop watch")
            self.stopWatchThread.quit()
            self.stopWatchThread.is_running = False
            self.stopWatchThread.resume     = True
            self.btnStartStopWatch.setText("Resume")

    def resetStopWatch(self):
        self.labelStop.setText("00 : 00 : 00")
        self.btnStartStopWatch.setText("Start")
        self.stopWatchThread.reset()


    ##### Timer #####

    # todo: fix reset button issue

    def show_timer(self):

        seconds = self.timerS % 60
        minutes = self.timerM % 60
        hours = self.timerH % 60

        if seconds < 10:
            seconds = "0"+str(seconds)
        if minutes < 10:
            minutes = "0"+str(minutes)
        if hours < 10:
            hours = "0"+str(hours)

        self.labelTimer.setText(str(hours)+" : "+str(minutes)+" : "+str(seconds))

    def onTimerSecondElapsed(self, count):
        seconds = count % 60
        minutes = (count / 60) % 60
        hours = count / 3600

        if seconds < 10:
            seconds = "0" + str(seconds)
        if minutes < 10:
            minutes = "0" + str(minutes)
        if hours < 10:
            hours = "0" + str(hours)

        self.labelTimer.setText(str(hours) + " : " + str(minutes) + " : " + str(seconds))

    def start_timer(self):
        if not self.timerThread.is_running:
            print("starting timer")
            count = self.timerH * 3600 + self.timerM * 60 + self.timerS
            self.timerThread.go(count)
            print("initial count " + str(count))
            self.btnTimer.setText("Stop")
        else:
            print("stopping timer now")
            self.timerThread.pause()
            self.timerThread.is_running = False
            self.timerThread.resume     = True
            self.btnTimer.setText("Resume")

    def reset_timer(self):
        self.onTimerSecondElapsed(self.timerThread.start_count/10)
        self.timerThread.reset()

        count = self.timerThread.count/10
        self.timerS = count % 60
        self.timerM = (count / 60)
        self.timerH = count / 3600

    def timer_finished(self):
        self.labelTimer.setText("00 : 00 : 00")
        self.btnTimer.setText("Start")
        self.timerThread.reset()
        self.timerS = 0
        self.timerM = 0
        self.timerH = 0

    def hour_plus(self):
        self.timerH += 1
        self.show_timer()

    def hour_min(self):
        if self.timerH > 0:
            self.timerH -= 1
        self.show_timer()

    def min_plus(self):
        self.timerM += 1
        self.show_timer()

    def min_min(self):
        if self.timerM > 0:
            self.timerM -= 1
        self.show_timer()

    def sec_plus(self):
        self.timerS += 1
        self.show_timer()

    def sec_min(self):
        if self.timerS > 0:
            self.timerS -= 1
        self.show_timer()


    ##### Einstellungen #####

    def on_update_brightness(self):
        print("brightness changed: " + str(self.brightnessSlider.value()))
        try:
            bl.set_brightness(self.brightnessSlider.value())
        except:
            print("error changing brightness")

    def onScreenOff(self):
        try:
            bl.set_power(not bl.get_power())
        except:
            print("could not change screen")

    def onQuit(self):
        """request clock thread to stop. thread will quit program via calling exit."""
        try:
            if bl.get_power():
                self.myThread.quit()
        except:
                self.myThread.quit()

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_Enter:
            self.onScreenOff()

    def disable_wifi(self):
        try:
            os.system("sudo sh -c 'echo 1-1.2 > /sys/bus/usb/drivers/usb/unbind'")
            self.wifi_enabled = False
            return True
        except:
            print ("could not disable wifi")
            return False

    def enable_wifi(self):
        try:
            os.system("sudo sh -c 'echo 1-1.2 > /sys/bus/usb/drivers/usb/bind'")
            self.wifi_enabled = True
            return True
        except:
            print("could not enable wifi")
            return False


    def on_wifi_btn(self):
        if self.wifi_enabled:
            if self.disable_wifi():
                self.btnWifi.setText("Wifi anschalten")
        else:
            if self.enable_wifi():
                self.btnWifi.setText("Wifi ausschalten")

    @QtCore.pyqtSlot(int)
    def exit(self):
        self.enable_wifi()
        sys.exit()



def main():
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
