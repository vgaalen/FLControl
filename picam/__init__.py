"""
@authors: Joe Lowney adapted by Joshua Stillerman (MIT) and Remon van Gaalen (INAF)
@copyright: 2026
@license: GNU GPL
"""

from picam.PiFunctions import *
from picam.PiParameterLookup import *
from picam.PiTypesMore import *
from picam.PiTypes import *

from ctypes import *
import numpy as np
import time
import threading
from time import sleep



class PiCam:
    def __init__(self):
        self.running = True
        self.capture_status = False
        self.latest_frame = np.zeros((1240,1240))

        self.name = f"picam"
        self.Shutters = {'N/A': 0}
        self.Modes = {'N/A': 0}
        self.width, self.height = 1240, 1240

        self.img_radius = None  # for cropping
        self.latest_frame = np.zeros((self.height, self.width))

        self.exptime = 0.

        Picam_InitializeLibrary()
        cams, num_cams = Picam_GetAvailableCameraIDs()
        print(num_cams)
        if num_cams.value == 0:
            print('Preparing to connect Demo Camera')
            model = ctypes.c_int(10)
            serial_number = ctypes.c_char_p(b'Demo Cam 1')
            PicamID = PicamCameraID()
            print('Demo camera connetcted with return value = ', Picam_ConnectDemoCamera(model, serial_number))
            print('\n')

        self.camera = Picam_OpenFirstCamera()
        self.camid = Picam_GetCameraID(self.camera)
        print(self.camid)
        print('Camera model is ', self.camid.model)
        print('Camera computer interface is ', self.camid.computer_interface)
        print('Camera sensor_name is ', self.camid.sensor_name)
        print('Camera serial number is', self.camid.serial_number)
        print(f"Connection Status: {Picam_IsCameraConnected(self.camera)}")
        print('\n')
        self.name = f"PICAM - {self.camid.model}"

        # failCount = piint()
        # paramsFailed = piint()
        # status = Picam_CommitParameters(self.camera, ptr(paramsFailed), ctypes.byref(failCount))
        # print("commit returned ", status, "failCount is ", failCount)

        readoutstride = Picam_GetParameterIntegerValue(self.camera, ctypes.c_int(PicamParameter_ReadoutStride))
        print("The readoutstride is %d" % readoutstride)

        self.readout_count = pi64s(1)
        self.readout_time_out = piint(100000)

        sz = readoutstride // 2
        DataArrayType = pi16u * sz
        self.DataArrayPointerType = ctypes.POINTER(pi16u * sz)

    def Start(self):
        self.capture_status = True
        loop = threading.Thread(target=self._loop)
        loop.start()

    def _loop(self):
        failCount = piint()
        paramsFailed = piint()
        status = Picam_CommitParameters(self.camera, ptr(paramsFailed), ctypes.byref(failCount))
        while self.capture_status:
            available = PicamAvailableData()#0, 0)
            errors = PicamAcquisitionErrorsMask()

            Picam_Acquire(self.camera, self.readout_count, self.readout_time_out, ctypes.byref(available), ctypes.byref(errors))

            DataPointer = ctypes.cast(available.initial_readout, self.DataArrayPointerType)
            self.latest_frame = np.array(DataPointer.contents).reshape((1024, 1024))

    def _loop2(self):
        while self.capture_status:
            Picam_StartAcquisition(self.camera)
            status = PicamAcquisitionStatus()
            print(Picam_IsAcquisitionRunning(self.camera))
            available = PicamAvailableData(0, 0)
            Picam_WaitForAcquisitionUpdate(self.camera, self.readout_time_out, ctypes.byref(available), ctypes.byref(status))
            DataPointer = ctypes.cast(available.initial_readout, self.DataArrayPointerType)
            self.latest_frame = np.array(DataPointer.contents).reshape((1024, 1024))

    def Stop(self):
        self.capture_status = False

    def shutdown(self):
        self.capture_status = False
        self.running = False
        sleep(1)
        Picam_UninitializeLibrary()

    def getImage(self):
        return self.latest_frame

    def getImages(self, N):
        frames = np.zeros((N, self.height, self.width), dtype=np.uint8)
        for i in range(N):
            frames[i] = self.getImage()
        return frames

    def getFps(self):
        return Picam_GetParameterFloatingPointValue(self.camera, PicamParameter_FrameRateCalculation)
    def getExptime(self):
        self.exptime = Picam_GetParameterFloatingPointValue(self.camera, PicamParameter_ExposureTime)
        return self.exptime
    def getGain(self):
        pass
    def getTemp(self):
        return f"{Picam_GetParameterFloatingPointValue(self.camera, PicamParameter_SensorTemperatureReading)}, {Picam_GetParameterIntegerValue(self.camera, PicamParameter_SensorTemperatureStatus)}"
    def getTempSetpoint(self):
        return Picam_GetParameterFloatingPointValue(self.camera, PicamParameter_SensorTemperatureSetPoint)
    def getRoi(self):
        pass
    def getShutter(self):
        pass
    def getHdr(self):
        pass
    def getMode(self):
        pass

    def setFps(self, fps):
        print("Framerate is not settable")
        return
    def setExptime(self, exptime):
        if self.capture_status:
            self.Stop()
        Picam_SetParameterFloatingPointValue(self.camera, PicamParameter_ExposureTime, piflt(float(exptime)))
        self.exptime = exptime
        return
    def setGain(self, gain):
        pass
    def setTemp(self, temp):
        print(Picam_SetParameterFloatingPointValue(self.camera, PicamParameter_SensorTemperatureSetPoint, piflt(float(temp))))
        return
    def setRoi(self, roi):
        pass
    def setHdr(self, hdr_mode):
        pass
    def setShutter(self, shutter):
        pass
    def setMode(self, mode):
        pass