from PyQt6.QtCore import QDateTime, Qt, QTimer
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QInputDialog, QPlainTextEdit)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import threading
from time import sleep
from datetime import datetime

plt.ion()

# TODO: Put parameter setpoints in fill-in sections

global DEMO
DEMO = False#True

if not DEMO:
    from Capture import capture
    from Execute import execute
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
        if DEMO:
            self.setWindowTitle("DEMO MODE: NOT CONNECTING TO CAMERA")
        else:
            self.setWindowTitle("FLControl - Live Viewer")

        if not DEMO:
            print('a')
            self.context = self.cam.Start()
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
        #self.figure.show(block=False)

        self.mean_label = QLabel("Mean Pixel Value")
        self.mean_value = QLabel("?")

        self.auto_scale_button = QPushButton("Auto Scale")
        self.auto_scale_button.setDefault(True)
        self.auto_scale_button.clicked.connect(self.auto_scale)

        layout = QGridLayout()
        layout.addWidget(self.canvas, 0, 0, 1, 3)
        layout.addWidget(self.mean_label, 1, 0)
        layout.addWidget(self.mean_value, 1, 1)
        layout.addWidget(self.auto_scale_button, 1, 2)
        #layout.addStretch(1)
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
        self.roi_in = QLineEdit("0,0,0,0,0")
        self.roi_label = QLabel("&Region of Interest:")
        self.roi_label.setBuddy(self.roi_in)
        self.roi_out = QLabel("?")
        self.shutter_in = QComboBox()
        if DEMO:
            self.shutter_in.addItems(['Global', 'Rolling'])
        else:
            self.shutter_in.addItems(list(self.cam.ShutterMap.keys()))
        self.shutter_label = QLabel("&Shutter Mode:")
        self.shutter_label.setBuddy(self.shutter_in)
        self.shutter_out = QLabel("?")
        self.shutter = self.shutter_in.currentText()

        self.hdr_in = QComboBox()
        if DEMO:
            self.hdr_in.addItems(['On', 'Off'])
        else:
            self.shutter_in.addItems(list(self.cam.HdrMap.keys()))
        self.hdr_label = QLabel("&HDR Mode:")
        self.hdr_label.setBuddy(self.hdr_in)
        self.hdr_out = QLabel("?")
        self.hdr = self.hdr_in.currentText()

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
        layout.addWidget(self.hdr_label, 6, 0)
        layout.addWidget(self.hdr_in, 6, 1)
        layout.addWidget(self.hdr_out, 6, 2)
        layout.addWidget(self.vmin_label, 7, 0)
        layout.addWidget(self.vmin_slider, 7, 1)
        layout.addWidget(self.vmin_value, 7, 2)
        layout.addWidget(self.vmax_label, 8, 0)
        layout.addWidget(self.vmax_slider, 8, 1)
        layout.addWidget(self.vmax_value, 8, 2)
        
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

        self.execute_button = QPushButton("Execute Runplan")
        self.execute_button.setDefault(True)
        self.execute_button.clicked.connect(self.Execute)
        self.execute_status = QLabel(" ")

        layout = QGridLayout()
        layout.addWidget(self.nframes_label, 1, 0)
        layout.addWidget(self.nframes, 1, 1)
        layout.addWidget(self.filename_label, 2, 0)
        layout.addWidget(self.filename, 2, 1)
        layout.addWidget(self.capture_status, 3, 2)
        layout.addWidget(self.capture_button, 3, 1)
        layout.addWidget(self.execute_button, 3, 0)
        self.CaptureGroupBox.setLayout(layout)

    def createProgressBar(self): 
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
        self.loop = threading.Thread(target = self.Update)#, args = (interval))
        self.loop.start()
        #self.Update()
    
    def Stop(self):
        self.cam.Stop()
    
    def Shutdown(self):
        self.Stop()
        self.cam.shutdown()
        self.running = False
        self.loop.join(timeout=60)
        self.close()
    
    def Update(self, interval=0.1): 
        while self.running:
            # update image
            img = self.cam.getImage()
            cmap = self.ax.imshow(img, vmin=self.vmin, vmax=self.vmax)
            #cmap = self.ax.imshow(np.zeros((100,100)), vmin=self.vmin, vmax=self.vmax)
            self.cbar.remove()
            self.cbar = self.figure.colorbar(cmap, ax=self.ax)
            self.mean_value.setText(str(np.mean(img)))

            self.canvas.draw()
            #plt.pause(0.1)

            # fetch camera metadata
            #self.fps_out.setText(self.shm['fps'].get_data(check=True))
            self.fps_out.setText(str(self.cam.getFps()))
            self.gain_out.setText(str(self.cam.getGain()))
            self.temp_out.setText(str(self.cam.getTemp()))
            self.roi_out.setText(str(self.cam.getRoi()))
            self.shutter_out.setText(str(self.cam.getShutter()))
            self.hdr_out.setText(str(self.cam.getHdr()))
            #sleep(interval)

    def Apply(self):
        # change camera settings
        if self.fps_in.isModified():
            fps = self.fps_in.text()
            try:
                self.cam.setFps(float(fps))#getDouble())
            except ValueError:
                print(f"FPS is not a Float: {fps}")
        
        if self.gain_in.isModified():
            gain = self.gain_in.text()
            try:
                self.cam.setGain(gain)
            except ValueError:
                print(f"Gain is not a Float: {gain}")
        
        if self.temp_in.isModified():
            temp = self.temp_in.text()
            try:
                self.cam.setTemp(float(temp))
            except ValueError:
                print(f"Temp is not a Float: {temp}")
        
        if self.roi_in.isModified():
            roi = np.fromstring(self.roi_in.text(),sep=',')
            try:
                self.cam.setRoi(*roi)
            except ValueError:
                print(f"Region of Interest not in proper format [toggle on/off, x0, y0, width, height]: {roi}")
        
        if self.shutter_in.currentText() != self.shutter:
            self.cam.setShutter(self.shutter_in.currentText())
        
        if self.hdr_in.currentText() != self.hdr:
            self.cam.setHdr(self.hdr_in.currentText())
    
    def apply_vmin(self, value):
        self.vmin = value
        self.vmin_value.setText(f"{value}")
    
    def apply_vmax(self, value):
        self.vmax = value
        self.vmax_value.setText(f"{value}")
    
    def Capture(self): 
        self.capture_status.setText("Recording")
        nframes = int(self.nframes.text())
        file = self.filename.text()
        self.updateProgressBar(itt=0, range=nframes)
        try:
            res = capture(self.cam,nframes,self.updateProgressBar,file=file)
            if res==1:
                self.capture_status.setText("Complete")
            else:
                self.capture_status.setText("Failed")
        except ValueError:
            self.capture_status.setText("Failed")
            print(f"Nframes has to be an integer: {nframes}")
    
    def Execute(self):
        self.capture_status.setText("Recording")
        self.updateProgressBar(itt=0)
        try:
            #res = execute(self.cam)
            self.ExecThread = threading.Thread(target = execute, args=[self.cam], kwargs = {'progress_func': self.updateProgressBar, 'exit_status_func': self.capture_status.setText})
            self.ExecThread.start()
            #if res==1:
            #    self.capture_status.setText("Complete")
            #else:
            #    self.capture_status.setText("Failed")
        except ValueError:
            self.capture_status.setText("Failed")
    
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