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
from typing import Optional, Literal

plt.ion()

from Capture import capture
from Execute import execute, execute_monitoring
import cameras
from fitting import gaussian, com, _fourier_filtering

import pyqtgraph as pg

class CtrlGroup:
    # Set of QT elements to control and monitor a parameter
    def __init__(self, label: str, grid: QGridLayout, row: int, type: Optional[Literal["LineEdit", "ComboBox"]]="LineEdit", options: Optional[list[str]]=None, default: Optional[str]="?"):
        self.label = QLabel(label)
        self.type = type
        if type == "LineEdit":
            self.input = QLineEdit("")
        elif type == "ComboBox":
            self.input = QComboBox()
            self.input.addItems(options)
        self.output = QLabel(default)
        #self.label.setBuddy(self.input)
        #self.label.setBuddy(self.output)
        grid.addWidget(self.label, row, 0)
        grid.addWidget(self.input, row, 1)
        grid.addWidget(self.output, row, 2)

class SliderGroup:
    def __init__(self, label: str, slider_range: tuple, box, grid, row, default_value=0, function=None):
        self.slider = QSlider(Qt.Orientation.Horizontal, box)
        self.slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.slider.setRange(*slider_range)
        self.slider.setValue(default_value)
        if function is not None:
            self.slider.valueChanged.connect(function)
        self.label = QLabel(label)
        self.label.setBuddy(self.slider)
        self.output = QLabel(str(default_value))

        grid.addWidget(self.label, row, 0)
        grid.addWidget(self.slider, row, 1)
        grid.addWidget(self.output, row, 2)

class ButtonGroup:
    def __init__(self, label, function, grid, location):
        self.button = QPushButton(label)
        self.button.setDefault(True)
        self.button.clicked.connect(function)
        grid.addWidget(self.button, *location)

class WidgetGallery(QDialog):
    def __init__(self, cam, parent=None):
        super(WidgetGallery, self).__init__(parent)
        self.cam = cam

        self.view = np.zeros((self.cam.height, self.cam.width))
        self.frameCounter = 0
        self.spot_x = 0
        self.spot_y = 0
        self.pos_x = None
        self.pos_y = None
        self.fitting_algorithm = gaussian

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
        self.setWindowTitle("FLControl - Live Viewer")

        self.Start()
        self.running = False

    def advanceProgressBar(self):
        curVal = self.progressBar.value()
        maxVal = self.progressBar.maximum()
        self.progressBar.setValue(curVal + (maxVal - curVal) // 100)

    def createViewGroupBox(self):
        self.ViewGroupBox = QGroupBox("Live Viewer")

        # self.figure = Figure(figsize=(5, 3))
        # self.canvas = FigureCanvas(self.figure)
        # self.ax = self.figure.subplots()
        # self.vmin = 0
        # self.vmax = 100
        # cmap = self.ax.imshow(np.zeros((100, 100)), vmin=self.vmin, vmax=self.vmax)
        # self.cbar = self.figure.colorbar(cmap, ax=self.ax)
        # # self.figure.show(block=False)

        self.canvas = pg.ImageView()
        self.canvas.setImage(self.view)

        self.mean_label = QLabel("Mean Pixel Value")
        self.mean_value = QLabel("?")

        self.frame_label = QLabel("Frame Counter")
        self.frame_value = QLabel("0")

        self.auto_scale_button = QPushButton("Auto Scale")
        self.auto_scale_button.setDefault(True)
        self.auto_scale_button.clicked.connect(self.auto_scale)

        layout = QGridLayout()
        layout.addWidget(self.canvas, 0, 0, 1, 5)
        layout.addWidget(self.mean_label, 1, 0)
        layout.addWidget(self.mean_value, 1, 1)
        layout.addWidget(self.frame_label, 1, 2)
        layout.addWidget(self.frame_value, 1, 3)
        layout.addWidget(self.auto_scale_button, 1, 4)

        self.target_position = CtrlGroup("Target Position 'x,y'", layout, 2, default="")
        self.target_apply = ButtonGroup("Set", self.add_target, layout, (2,2,1,3))

        #self.spot_label = QLabel("Spot Position: ")
        self.spot_label = QComboBox()
        self.spot_label.addItems(["CoM Fit", "Gaussian Fit"])
        self.spot_position = QLabel("?, ?")
        self.spot_delta = QLabel("")
        layout.addWidget(self.spot_label, 3, 0)
        layout.addWidget(self.spot_position, 3, 1)
        layout.addWidget(self.spot_delta, 3, 2, 1, 3)

        # Avg spot position
        self.avg_selector = QComboBox()
        self.avg_selector.addItems(["Avg 1", "Avg 2", "Avg 10", "Avg 100"])
        self.avg_abs = QLabel("?, ?")
        self.avg_delta = QLabel("?, ?")
        self.avg_buffer = np.zeros((1,2))
        self.avg_buffer_pointer = 0
        layout.addWidget(self.avg_selector, 4, 0)
        layout.addWidget(self.avg_abs, 4, 1)
        layout.addWidget(self.avg_delta, 4, 2, 1, 3)

        layout.setRowStretch(0, 1)
        self.ViewGroupBox.setLayout(layout)

    def createControlGroupBox(self):
        self.ControlGroupBox = QGroupBox("Control Panel")

        layout = QGridLayout()
        self.temp = CtrlGroup("Sensor Temperature", layout, 0)
        self.fps = CtrlGroup("FPS", layout, 1)
        self.exptime = CtrlGroup("Exposure Time", layout, 2)
        self.gain = CtrlGroup("Gain", layout, 3)
        self.mode = CtrlGroup("Readout Mode", layout, 4, type="ComboBox", options=list(self.cam.Modes.keys()))
        self.shutter = CtrlGroup("Shutter Mode", layout, 5, type="ComboBox", options=list(self.cam.Shutters.keys()))
        self.roi = CtrlGroup("Region of Interest", layout, 6)

        self.vmin_slider = SliderGroup("vmin", (0,20000),self.ControlGroupBox,layout,7,0,self.apply_vmin)
        self.vmax_slider = SliderGroup("vmax", (0,20000), self.ControlGroupBox, layout, 8, 10000, self.apply_vmax)

        self.apply_button = ButtonGroup("Apply", self.Apply, layout, (9,1))
        self.start_button = ButtonGroup("Start", self.Start, layout, (9,0))
        self.stop_button = ButtonGroup("Stop", self.Stop, layout, (9,2))
        self.shutdown_button = ButtonGroup("Shutdown", self.Shutdown, layout, (9,3))

        self.ControlGroupBox.setLayout(layout)

    def createCaptureControlGroupBox(self):
        self.CaptureGroupBox = QGroupBox("Control Panel")
        layout = QGridLayout()
        self.nframes = CtrlGroup("# of Frames", layout, 1)
        self.filename = CtrlGroup("Write to File", layout, 2, default=f"{datetime.now():%Y%m%d-%H%M%S}.fits")
        self.capture_button = ButtonGroup("Capture", self.Capture, layout, (3,1))
        self.execute_button = ButtonGroup("Execute", self.Execute, layout, (3,0))
        self.capture_status = QLabel(" ")
        layout.addWidget(self.capture_status, 3, 2)
        self.CaptureGroupBox.setLayout(layout)

    def createProgressBar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 10000)
        self.progressBar.setValue(0)

    def updateProgressBar(self, itt=None, range=None):
        if range is not None:
            self.progressBar.setRange(0, range)
        if itt is not None:
            self.progressBar.setValue(itt)

    def Start(self, interval=1):
        self.running = True
        self.context = self.cam.Start()
        self.loop = threading.Thread(target=self.Update)  # , args = (interval))
        self.loop.start()
        # self.Update()

    def Stop(self):
        self.running = False
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
            try:
                self.view = self.cam.getImage()
                self.frameCounter += 1
            except Exception as e:
                print(e)
                pass

            self.view[self.view==np.max(self.view)] = 0
            self.view[self.view<0.1*np.max(self.view)] = 0
            self.view = _fourier_filtering(self.view, radius=25)
            
            self.canvas.setImage(self.view.T, autoLevels=False, autoRange=False)
            self.mean_value.setText(str(np.mean(self.view)))
            self.frame_value.setText(str(self.frameCounter))

            # fetch camera metadata
            self.temp.output.setText(str(self.cam.getTemp()))
            self.fps.output.setText(str(self.cam.getFps()))
            self.exptime.output.setText(str(self.cam.getExptime()))
            self.gain.output.setText(str(self.cam.getGain()))
            self.shutter.output.setText(str(self.cam.getShutter()))
            self.mode.output.setText(str(self.cam.getMode()))
            self.roi.output.setText(str(self.cam.getRoi()))
            # sleep(interval)

            # find the spot
            self.spot_y, self.spot_x = self.fitting_algorithm(self.view) #gaussian(self.view)
            self.spot_position.setText(str(self.spot_x)+", "+str(self.spot_y))
            if self.pos_x is not None and self.pos_y is not None:
                self.spot_delta.setText(str(self.spot_x-self.pos_x)+", "+str(self.spot_y-self.pos_y))
            ax = self.canvas.getView()
            try:
                ax.removeItem(self.spot_mark1)
                ax.removeItem(self.spot_mark2)
            except AttributeError:
                pass
            self.spot_mark1 = pg.PlotCurveItem(x=[self.spot_x, self.spot_x], y=[0, self.cam.height - 1], pen='blue')
            self.spot_mark2 = pg.PlotCurveItem(x=[0, self.cam.width - 1], y=[self.spot_y, self.spot_y], pen='blue')
            ax.addItem(self.spot_mark1)
            ax.addItem(self.spot_mark2)

            if self.avg_buffer_pointer >= self.avg_buffer.shape[0]:
                self.avg_buffer_pointer = 0
            self.avg_buffer[self.avg_buffer_pointer] = [self.spot_x, self.spot_y]
            self.avg_buffer_pointer += 1
            self.avg_abs.setText(f"{np.mean(self.avg_buffer[:,0])}, {np.mean(self.avg_buffer[:,1])}")
            if self.pos_x is not None and self.pos_y is not None:
                self.avg_delta.setText(f"{np.mean(self.avg_buffer[:,0])-self.pos_x}, {np.mean(self.avg_buffer[:,1])-self.pos_y}")


    def Apply(self):
        # change camera settings
        for setting,func in zip([self.temp, self.fps, self.exptime, self.gain, self.mode, self.shutter, self.roi],
                                [self.cam.setTemp, self.cam.setFps, self.cam.setExptime, self.cam.setGain, self.cam.setMode, self.cam.setShutter, self.cam.setRoi]):
            if setting.type == "LineEdit":
                if setting.input.isModified():
                    value = setting.input.text()
                    try:
                        func(value)
                    except ValueError:
                        print(f"[Warning] Unable to update {setting.label}")
            else:
                value = setting.input.currentText()
                try:
                    func(value)
                except ValueError:
                    print(f"[Warning] Unable to update {setting.label}")
        
        avg_setting = self.avg_selector.currentText().split("Avg ")[-1]
        self.avg_buffer = np.zeros((int(avg_setting),2))

        if self.spot_label.currentText() == "CoM Fit":
            self.fitting_algorithm = com 
        elif self.spot_label.currentText() == "Gaussian Fit":
            self.fitting_algorithm = gaussian
        else:
            print("[Warning] Unknown Fitting Algorithm")


    def apply_vmin(self, value):
        self.vmin = value
        self.vmin_slider.output.setText(f"{value}")

    def apply_vmax(self, value):
        self.vmax = value
        self.vmax_slider.output.setText(f"{value}")

    def Capture(self):
        self.capture_status.setText("Recording")
        nframes = int(self.nframes.input.text())
        file = self.filename.input.text()
        self.updateProgressBar(itt=0, range=nframes)
        try:
            res = capture(self.cam, nframes, self.updateProgressBar, file=file)
            if res == 1:
                self.capture_status.setText("Complete")
                print("Complete")
                self.updateProgressBar(itt=nframes, range=nframes)
            else:
                self.capture_status.setText("Failed")
                print("Failed")
        except ValueError:
            self.capture_status.setText("Failed")
            print(f"Nframes has to be an integer: {nframes}")

    def Execute(self):
        self.capture_status.setText("Recording")
        self.updateProgressBar(itt=0)
        try:
            # res = execute(self.cam)
            thread = threading.Thread(target=execute_monitoring, args=[self.cam],
                                               kwargs={'progress_func': self.updateProgressBar,
                                                       'exit_status_func': self.capture_status.setText})
            thread.start()
        except ValueError:
            self.capture_status.setText("Failed")

    def auto_scale(self):
        print("set scale")
        img = self.cam.getImage()[1]
        self.vmin = np.mean(img) - 3 * np.std(img)
        self.vmax = np.mean(img) + 3 * np.std(img)

    def add_target(self):
        self.pos_x, self.pos_y = self.target_position.input.text().split(',')
        self.pos_x, self.pos_y = float(self.pos_x), float(self.pos_y)
        #pos_x = 50
        #pos_y = 50
        #size = 0.05
        #self.ax.plot([self.pos_x, self.pos_x], [self.pos_y-size*self.cam.height, self.pos_y+size*self.cam.height], color='red', linewidth=1)
        #self.ax.plot([self.pos_x-size*self.cam.width, self.pos_x+size*self.cam.width], [self.pos_y, self.pos_y], color='red', linewidth=1)

        ax = self.canvas.getView()
        try:
            ax.removeItem(self.target_mark1)
            ax.removeItem(self.target_mark2)
        except AttributeError:
            pass
        self.target_mark1 = pg.PlotCurveItem(x=[self.pos_x,self.pos_x], y=[0, self.cam.height-1], pen='red')
        self.target_mark2 = pg.PlotCurveItem(x=[0,self.cam.width-1], y=[self.pos_y, self.pos_y], pen='red')
        ax.addItem(self.target_mark1)
        ax.addItem(self.target_mark2)

        # try:
        #     self.canvas.draw()
        # except:
        #     pass


if __name__ == '__main__':
    import sys
    print("Starting AlignmentViewer")

    res = int(input("""Choose the camera type: 
    1: Demo
    2: First Light Imaging
    3: QHYCCD
    4: Allied Vision
    """))

    if res==4:
        import vmbpy
        interface = vmbpy.VmbSystem.get_instance()
        print("Loaded Vimba Interface")
        with interface:
            cams = interface.get_all_cameras()
            for cam in cams:
                print(cam)
            cam = cams[0]
            print("Loading Camera")
            with cam:
                print("Camera Loaded")
                cam = cameras.Start("Allied", interface=interface, cam=cam)
                app = QApplication(sys.argv)
                gallery = WidgetGallery(cam)
                gallery.show()
                sys.exit(app.exec())
    else:
        cam = cameras.Start(["Demo","FLI","QHY","Allied"][res-1])
        app = QApplication(sys.argv)
        gallery = WidgetGallery(cam)
        gallery.show()
        sys.exit(app.exec())
