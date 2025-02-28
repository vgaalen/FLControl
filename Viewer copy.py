import sys
#from PySide6 import QtCore, QtWidgets, GtGui, uic
from PyQt6.QtCore import QDateTime, Qt, QTimer
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit, QDial, QDialog, QGridLayout, 
                             QGroupBox,  QHBoxLayout, QLabel, QLineEdit, QProgressBar, QPushButton, QRadioButton, 
                             QScrollBar, QSizePolicy, QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, 
                             QTextEdit, QVBoxLayout, QWidget, QInputDialog, QPlainTextEdit)
import os
os.environ['QT_DEBUG_PLUGINS']='1'
#import dao
import pickle
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvas
import numpy as np
from cblue import *
from os.path import isfile
from Capture import capture
import threading


class Viewer(QDialog):
    def __init__(self):
        super(Viewer, self).__init__()

        self.context = None#Start()

        self.originalPalette = QApplication.palette()      
        
        #self.setupUi(self)
        #self.scale = 100
        #self.shm = shm

        # Image Frmae
        # self.imagebox = pg.ViewBox()
        # self.graphicsView.setCentralItem(self.vb)
        # self.vb.setAspectLocked()
        # self.img = pg.ImageItem()
        # self.imagebox.addItem(self.img)
        self.figure = Figure(figsize=(5,3))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.subplots()
        self.vmin = 0
        self.vmax = 100
        cmap = self.ax.imshow(np.zeros((100,100)), vmin=self.vmin, vmax=self.vmax)
        self.figure.colorbar(cmap, ax=self.ax)

        self.create_control_panel()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.canvas, 0, 0)
        mainLayout.addWidget(self.control_panel, 0, 1)
    
    def Start(self, interval=1):
        threading.Thread(target = self.Update, args = (self, interval))

    def create_control_panel(self):
        self.control_panel = QGroupBox("Group 1")

        # Settings Panel
        self.fps_in = QInputDialog()#.DoubleInput()
        self.fps_label = QLabel("&FPS:")
        self.fps_label.setBuddy(self.fps_in)
        self.fps_out = QPlainTextEdit()
        self.gain_in = QInputDialog()#.DoubleInput()
        self.gain_label = QLabel("&Gain:")
        self.gain_label.setBuddy(self.gain_in)
        self.gain_out = QPlainTextEdit()
        self.temp_in = QInputDialog()#.DoubleInput()
        self.temp_label = QLabel("&Temperature")
        self.temp_label.setBuddy(self.temp_in)
        self.temp_out = QPlainTextEdit()
        self.roi_in = QInputDialog()#.TextInput()
        self.roi_label = QLabel("&Region of Interest:")
        self.roi_label.setBuddy(self.roi_in)
        self.roi_out = QPlainTextEdit()
        self.shutter_in = QInputDialog()#.IntInput()
        self.shutter_label = QLabel("&Shutter Mode:")
        self.shutter_label.setBuddy(self.shutter_in)
        self.shutter_out = QPlainTextEdit()

        self.vmin_slider = QSlider(Qt.Orientation.Horizontal, self.control_panel)
        self.vmin_slider.setValue(0)
        self.vmin_label = QLabel("&Vmin:")
        self.vmin_label.setBuddy(self.vmin_slider)
        self.vmax_slider = QSlider(Qt.Orientation.Horizontal, self.control_panel)
        self.vmax_slider.setValue(100)
        self.vmax_label = QLabel("&Vmax:")
        self.vmax_label.setBuddy(self.vmax_slider)

        self.apply_button = QPushButton("Apply")
        self.apply_button.setDefault(True)
        self.apply_button.clicked.connect(self.Apply)

        self.nframes = QInputDialog()#.IntInput()
        self.capture_button = QPushButton("Capture")
        self.capture_button.setDefault(True)
        self.capture_button.clicked.connect(self.Capture)

        layout = QGridLayout()
        layout.addWidget(self.fps_in, 0, 0)
        layout.addWidget(self.fps_out, 0, 1)
        layout.addWidget(self.gain_in, 1, 0)
        layout.addWidget(self.gain_out, 1, 1)
        layout.addWidget(self.temp_in, 2, 0)
        layout.addWidget(self.temp_out, 2, 1)
        layout.addWidget(self.roi_in, 3, 0)
        layout.addWidget(self.roi_out, 3, 1)
        layout.addWidget(self.shutter_in, 4, 0)
        layout.addWidget(self.shutter_out, 4, 1)
        layout.addWidget(self.vmin_slider, 5, 0)
        layout.addWidget(self.vmax_slider, 6, 0)
        layout.addWidget(self.apply_button, 7, 0)
        layout.addWidget(self.nframes, 7, 1)
        layout.addWidget(self.capture_button, 8, 1)

        self.control_panel.setLayout(layout)


    def Update(self, interval): # TODO: update deamon
        while 1:
            # update image
            cmap = self.ax.imshow(getImage, vmin=self.vmin, vmax=self.vmax)
            self.figure.colorbar(cmap, ax=self.ax)

            # fetch camera metadata
            #self.fps_out.setText(self.shm['fps'].get_data(check=True))
            self.fps_out.setPlainText(str(getFps(self.context)))
            self.gain_out.setPlainText(str(getGain(self.context)))
            self.temp_out.setPlainText(str(getTemp(self.context)))
            self.roi_out.setPlainText(str(getRoi(self.context)))

            sleep(interval)

    def Apply(self):
        # change camera settings
        fps = self.fps_in.text()
        try:
            setFps(self.context,float(fps))#getDouble())
        except ValueError:
            print(f"FPS is not a Float: {fps}")
        gain = self.gain_in.text()
        try:
            setGain(self.context,float(gain))
        except ValueError:
            print(f"Gain is not a Float: {gain}")
        temp = self.temp_in.text()
        try:
            setTemp(self.context,float(temp))
        except ValueError:
            print(f"Temp is not a Float: {temp}")
        roi = np.fromstring(self.roi.text())
        try:
            setRoi(self.context,roi)
        except ValueError:
            print(f"Region of Interest not in proper format [toggle on/off, x0, y0, width, height]: {roi}")
        self.vmin = self.vmin_slider.getValue()
        self.vmax = self.vmax_slider.getValue()
    
    def Capture(self): 
        capture(self.context,int(self.nframes.text()))

if __name__=="__main__":
    #with open('shm.pkl', 'r') as f:
    #    shm = pickle.load('shm.pkl')
    #shm = loadShm()

    app = QApplication(sys.argv)
    window = Viewer()
    window.show()
    window.Start()
    app.exec() 
