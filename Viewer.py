import sys
#from PySide6 import QtCore, QtWidgets, GtGui, uic
from PyQt6.QtCore import QDateTime, Qt, QTimer
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit, QDial, QDialog, QGridLayout, 
                             QGroupBox,  QHBoxLayout, QLabel, QLineEdit, QProgressBar, QPushButton, QRadioButton, 
                             QScrollBar, QSizePolicy, QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, 
                             QTextEdit, QVBoxLayout, QWidget, QInputDialog, QPlainTextEdit)
import dao
import pickle
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvas
import numpy as np
from cblue import loadShm
from os.path import isfile
class Viewer(QDialog):
    def __init__(self, shm):
        super(Viewer, self).__init__()

        self.originalPalette = QApplication.palette()      
        
        #self.setupUi(self)
        #self.scale = 100
        self.shm = shm

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
        cmap = self.ax.imshow(self.shm['img'].get_data(check=True), vmin=self.vmin, vmax=self.vmax)
        self.figure.colorbar(cmap, ax=self.ax)

        self.create_control_panel()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.canvas, 0, 0)
        mainLayout.addWidget(self.control_panel, 0, 1)

    def create_control_panel(self):
        self.control_panel = QGroupBox("Group 1")

        # Settings Panel
        fps_in = QInputDialog.DoubleInput()
        self.fps_label = QLabel("&FPS:")
        self.fps_label.setBuddy(fps_in)
        self.fps_out = QPlainTextEdit()
        self.gain_in = QInputDialog.DoubleInput()
        self.gain_label = QLabel("&Gain:")
        self.gain_label.setBuddy(self.gain_in)
        self.gain_out = QPlainTextEdit()
        self.temp_in = QInputDialog.DoubleInput()
        self.temp_label = QLabel("&Temperature")
        self.temp_label.setBuddy(self.temp_in)
        self.temp_out = QPlainTextEdit()
        self.roi_in = QInputDialog.TextInput()
        self.roi_label = QLabel("&Region of Interest:")
        self.roi_label.setBuddy(self.roi_in)
        self.roi_out = QPlainTextEdit()
        self.shutter_in = QInputDialog.IntInput()
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
        self.apply_button.clicked.connect(self.update)

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

        self.control_panel.setLayout(layout)


    def update(self):
        # update image
        cmap = self.ax.imshow(self.shm['img'].get_data(check=True), vmin=self.vmin, vmax=self.vmax)
        self.figure.colorbar(cmap, ax=self.ax)

        # fetch camera metadata
        #self.fps_out.setText(self.shm['fps'].get_data(check=True))
        self.fps_out.setPlainText(str(self.shm['fps'].get_data(check=True)))
        self.gain_out.setPlainText(str(self.shm['gain'].get_data(check=True)))
        self.temp_out.setPlainText(str(self.shm['temp'].get_data(check=True)))
        self.roi_out.setPlainText(str(self.shm['roi'].get_data(check=True)))

    def Apply(self):
        # change camera settings
        self.shm['fps'].set_data(self.fps_in.getDouble())
        self.shm['gain'].set_data(self.gain_in.getDouble())
        self.shm['set_temp'].set_data(self.temp_in.getDouble())
        self.shm['roi'].set_data(np.fromstring(self.roi.getText()))
        self.vmin = self.vmin_slider.getValue()
        self.vmax = self.vmax_slider.getValue()

if __name__=="__main__":
    #with open('shm.pkl', 'r') as f:
    #    shm = pickle.load('shm.pkl')
    shm = loadShm()

    app = QApplication(sys.argv)
    window = Viewer(shm)
    window.show()
    app.exec() 
