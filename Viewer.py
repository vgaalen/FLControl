from PyQt6.QtCore import QDateTime, Qt, QTimer
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QInputDialog, QPlainTextEdit)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvas
import numpy as np
import threading
from time import sleep
from datetime import datetime

global DEMO
DEMO = True

if not DEMO:
    from Capture import capture
    import mappings

class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)
        if not DEMO:
            self.cam = mappings.Start()

        self.originalPalette = QApplication.palette()
        self.createViewGroupBox()
        self.createControlGroupBox()
        self.createCaptureControlGroupBox()
        self.createProgressBar()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.ViewGroupBox, 1, 0, 2, 1)
        mainLayout.addWidget(self.ControlGroupBox, 1, 1)
        mainLayout.addWidget(self.CaptureGroupBox, 2, 1)
        mainLayout.addWidget(self.progressBar, 3, 0, 1, 2)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)
        self.setWindowTitle("Styles")

        if not DEMO:
            self.context = self.cam.start()
            self.Start()

    def advanceProgressBar(self):
        curVal = self.progressBar.value()
        maxVal = self.progressBar.maximum()
        self.progressBar.setValue(curVal + (maxVal - curVal) // 100)

    def createViewGroupBox(self):
        self.ViewGroupBox = QGroupBox("Live Viewer")

        self.figure = Figure(figsize=(5,3))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.subplots()
        self.vmin = 0
        self.vmax = 100
        cmap = self.ax.imshow(np.zeros((100,100)), vmin=self.vmin, vmax=self.vmax)
        self.cbar = self.figure.colorbar(cmap, ax=self.ax)

        self.auto_scale_button = QPushButton("Auto Scale")
        self.auto_scale_button.setDefault(True)
        self.auto_scale_button.clicked.connect(self.auto_scale)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.auto_scale_button)
        layout.addStretch(1)
        self.ViewGroupBox.setLayout(layout)

    def createControlGroupBox(self):
        self.ControlGroupBox = QGroupBox("Control Panel")

        # Settings Panel
        self.set_point_label = QLabel("Set Point")
        self.cam_status_label = QLabel("Status")
        self.fps_in = QLineEdit("100")
        self.fps_label = QLabel("&FPS:")
        self.fps_label.setBuddy(self.fps_in)
        self.fps_out = QLabel("?")
        self.gain_in = QLineEdit("1")
        self.gain_label = QLabel("&Gain:")
        self.gain_label.setBuddy(self.gain_in)
        self.gain_out = QLabel("?")
        self.temp_in = QLineEdit("20")
        self.temp_label = QLabel("&Temperature")
        self.temp_label.setBuddy(self.temp_in)
        self.temp_out = QLabel("?")
        self.roi_in = QLineEdit("[0,0,0,0,0]")
        self.roi_label = QLabel("&Region of Interest:")
        self.roi_label.setBuddy(self.roi_in)
        self.roi_out = QLabel("?")
        self.shutter_in = QComboBox()
        self.shutter_in.addItems(['Global', 'Rolling'])
        self.shutter_label = QLabel("&Shutter Mode:")
        self.shutter_label.setBuddy(self.shutter_in)
        self.shutter_out = QLabel("?")

        self.vmin_slider = QSlider(Qt.Orientation.Horizontal, self.ControlGroupBox)
        self.vmin_slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.vmin_slider.setRange(0,2**16)
        self.vmin_slider.setValue(0)
        self.vmin_slider.valueChanged.connect(self.apply_vmin)
        self.vmin_label = QLabel("&Vmin:")
        self.vmin_label.setBuddy(self.vmin_slider)
        self.vmin_value = QLabel("0")
        self.vmax_slider = QSlider(Qt.Orientation.Horizontal, self.ControlGroupBox)
        self.vmax_slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.vmax_slider.setRange(0,2**16)
        self.vmax_slider.setValue(100)
        self.vmax_slider.valueChanged.connect(self.apply_vmax)
        self.vmax_label = QLabel("&Vmax:")
        self.vmax_label.setBuddy(self.vmax_slider)
        self.vmax_value = QLabel("100")

        self.apply_button = QPushButton("Apply")
        self.apply_button.setDefault(True)
        self.apply_button.clicked.connect(self.Apply)

        self.start_button = QPushButton("Start")
        self.start_button.setDefault(True)
        self.start_button.clicked.connect(self.Start)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setDefault(True)
        self.stop_button.clicked.connect(self.Stop)
        self.shutdown_button = QPushButton("Shutdown")
        self.shutdown_button.setDefault(True)
        self.shutdown_button.clicked.connect(self.Shutdown)

        layout = QGridLayout()
        layout.addWidget(self.set_point_label, 0, 1)
        layout.addWidget(self.cam_status_label, 0, 2)
        layout.addWidget(self.fps_label, 1, 0)
        layout.addWidget(self.fps_in, 1, 1)
        layout.addWidget(self.fps_out, 1, 2)
        layout.addWidget(self.gain_label, 2, 0)
        layout.addWidget(self.gain_in, 2, 1)
        layout.addWidget(self.gain_out, 2, 2)
        layout.addWidget(self.temp_label, 3, 0)
        layout.addWidget(self.temp_in, 3, 1)
        layout.addWidget(self.temp_out, 3, 2)
        layout.addWidget(self.roi_label, 4, 0)
        layout.addWidget(self.roi_in, 4, 1)
        layout.addWidget(self.roi_out, 4, 2)
        layout.addWidget(self.shutter_label, 5, 0)
        layout.addWidget(self.shutter_in, 5, 1)
        layout.addWidget(self.shutter_out, 5, 2)
        layout.addWidget(self.vmin_label, 6, 0)
        layout.addWidget(self.vmin_slider, 6, 1)
        layout.addWidget(self.vmin_value, 6, 2)
        layout.addWidget(self.vmax_label, 7, 0)
        layout.addWidget(self.vmax_slider, 7, 1)
        layout.addWidget(self.vmax_value, 7, 2)
        
        layout.addWidget(self.apply_button, 9, 1)
        layout.addWidget(self.start_button, 9, 0)
        layout.addWidget(self.stop_button, 9, 2)
        layout.addWidget(self.shutdown_button, 9, 3)
        
        self.ControlGroupBox.setLayout(layout)
    
    def createCaptureControlGroupBox(self):
        self.CaptureGroupBox = QGroupBox("Control Panel")

        self.nframes = QLineEdit()
        self.nframes_label = QLabel("&# of Frames")
        self.nframes_label.setBuddy(self.nframes)
        self.filename = QLineEdit(f"{datetime.now():%Y%m%d-%H%M%S}.fits")
        self.filename_label = QLabel("&Write to File")
        self.filename_label.setBuddy(self.filename)

        self.capture_button = QPushButton("Capture")
        self.capture_button.setDefault(True)
        self.capture_button.clicked.connect(self.Capture)
        self.capture_status = QLabel(" ")

        layout = QGridLayout()
        layout.addWidget(self.nframes_label, 1, 0)
        layout.addWidget(self.nframes, 1, 1)
        layout.addWidget(self.filename_label, 2, 0)
        layout.addWidget(self.filename, 2, 1)
        layout.addWidget(self.capture_status, 3, 1)
        layout.addWidget(self.capture_button, 3, 0)
        self.CaptureGroupBox.setLayout(layout)

    def createProgressBar(self): # TODO attach to capture progress
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 10000)
        self.progressBar.setValue(0)
    
    def updateProgressBar(self, itt=None, range=None):
        if range is not None:
            self.progressBar.setRange(0,range)
        if itt is not None:
            self.progressBar.setValue(itt)
    
    def Start(self, interval=1):
        self.running = True
        self.context = self.cam.Start()
        loop = threading.Thread(target = self.Update)#, args = (interval))
        loop.start()
    
    def Stop(self):
        self.running = False
        self.cam.stop(self.context)
    
    def Shutdown(self):
        self.Stop()
        self.cam.shutdown(self.context)
        self.close()
    
    def Update(self, interval=0.1): # TODO: update deamon
        while self.running:
            #print('a')
            # update image
            cmap = self.ax.imshow(self.cam.getImage, vmin=self.vmin, vmax=self.vmax)
            #cmap = self.ax.imshow(np.zeros((100,100)), vmin=self.vmin, vmax=self.vmax)
            self.cbar.remove()
            self.cbar = self.figure.colorbar(cmap, ax=self.ax)

            # fetch camera metadata
            #self.fps_out.setText(self.shm['fps'].get_data(check=True))
            self.fps_out.setText(str(self.cam.getFps(self.context)))
            self.gain_out.setText(str(self.cam.getGain(self.context)))
            self.temp_out.setText(str(self.cam.getTemp(self.context)))
            self.roi_out.setText(str(self.cam.getRoi(self.context)))
            sleep(interval)

    def Apply(self):
        # change camera settings
        if self.fps_in.isModified():
            fps = self.fps_in.text()
            try:
                self.cam.setFps(self.context,float(fps))#getDouble())
            except ValueError:
                print(f"FPS is not a Float: {fps}")
        
        if self.gain_in.isModified():
            gain = self.gain_in.text()
            try:
                self.cam.setGain(self.context,float(gain))
            except ValueError:
                print(f"Gain is not a Float: {gain}")
        
        if self.temp_in.isModified():
            temp = self.temp_in.text()
            try:
                self.cam.setTemp(self.context,float(temp))
            except ValueError:
                print(f"Temp is not a Float: {temp}")
        
        if self.roi_in.isModified():
            roi = np.fromstring(self.roi_in.text())
            try:
                self.cam.setRoi(self.context,roi)
            except ValueError:
                print(f"Region of Interest not in proper format [toggle on/off, x0, y0, width, height]: {roi}")
        #self.vmin = self.vmin_slider.getValue()
        #self.vmax = self.vmax_slider.getValue()
    
    def apply_vmin(self, value):
        self.vmin = value
        self.vmin_value.setText(f"{value}")
    
    def apply_vmax(self, value):
        self.vmax = value
        self.vmax_value.setText(f"{value}")
    
    def Capture(self): 
        self.capture_status.setText("Recording")
        nframes = self.nframes.text()
        self.updateProgressBar(itt=0, range=nframes)
        try:
            res = capture(self.cam,int(nframes),self.updateProgressBar)
            if res==1:
                self.capture_status.setText("Complete")
            else:
                self.capture_status.setText("Failed")
        except ValueError:
            self.capture_status.setText("Failed")
            print(f"Nframes has to be an integer: {nframes}")
    
    def auto_scale(self):
        print("set scale")
        img = np.zeros((100,100))#cam.getImage
        img[1,1]= 1
        self.vmin = np.mean(img)-3*np.std(img)
        self.vmax = np.mean(img)+3*np.std(img)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.show()
    sys.exit(app.exec())