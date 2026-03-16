import cv2
import numpy as np
import ctypes
from ctypes import *
from enum import Enum

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

class QhyCam:
    def __init__(self):
        self.interface = cdll.LoadLibrary('.\\qhy\\qhyccd.dll')
        res = self.interface.InitQHYCCD()
        print(res)
        print(self.interface.GetQHYCCDChipInfo())

        self.Shutters = {'N/A': 0}
        self.Modes = {'N/A': 0}
        self.width, self.height = 0,0

        self.getImage()

    def Start(self):
        pass
        # try:
        #     self.cam.BeginLive()
        #     return True
        # except:
        #     print("[Warning] Failed to start live mode")
        #     return False

    def Stop(self):
        pass
        # try:
        #     self.cam.StopLive()
        #     return True
        # except:
        #     print("[Warning] Failed to stor live mode")
        #     return False

    def shutdown(self):
        self.cam.StopLive()
        sleep(1)
        self.cam.close()

    def getImage(self):
        self.interface.ExpQHYCCDSingleFrame()
        # TODO Convert the pointers that are returned to a numpy array containing the image
        print(self.interface.GetQHYCCDSingleFrame())
        #return self.interface.GetQHYCCDSingleFrame()
        return np.zeros((self.height,self.width))

    def getFps(self):
        #return #1/(0.001*self.cam.exposureMS)
        self.interface.ExpQHYCCDSingleFrame()
        # TODO Convert the pointers that are returned to a numpy array containing the image
        return self.interface.GetQHYCCDSingleFrame()

    def getExptime(self):
        return #self.cam.exposureMS

    def getGain(self):
        return "?"

    def getTemp(self):
        return "?"

    def getRoi(self):
        return "?"

    def getShutter(self):
        return "?"

    def getHdr(self):
        return "?"

    def setFps(self, fps):
        pass#self.cam.SetExposure(1000*1/fps)

    def setExptime(self, exptime):
        pass#self.cam.SetExposure(exptime)

    def setGain(self, gain):
        print("[Warning] Changing the gain is not supported")
        return False

    def setTemp(self, temp):
        print("[Warning] Changing the temperature is not supported")
        return False

    def setRoi(self, roi):
        print("[Warning] Changing the Region of Interest is not supported")
        return False

    def setHdr(self, hdr_mode):
        print("[Warning] Changing the HDR-mode is not supported")
        return False

    def setShutter(self, shutter):
        print("[Warning] Changing the shutter mode is not supported")
        return False