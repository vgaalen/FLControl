import cv2
import numpy as np
import ctypes
from ctypes import *
from enum import Enum

from time import sleep

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

class CONTROL_ID(Enum):
    CONTROL_BRIGHTNESS = 0
    CONTROL_CONTRAST = 1
    CONTROL_WBR = 2
    CONTROL_WBB = 3
    CONTROL_WBG = 4
    CONTROL_GAMMA = 5
    CONTROL_GAIN = 6
    CONTROL_OFFSET = 7
    CONTROL_EXPOSURE = 8
    CONTROL_SPEED = 9
    CONTROL_TRANSFERBIT = 10
    CONTROL_CHANNELS = 11
    CONTROL_USBTRAFFIC = 12
    CONTROL_CURTEMP = 14
    CONTROL_CURPWM = 15
    CONTROL_MANULPWM = 16
    CONTROL_CFWPORT = 17
    CONTROL_COOLER = 18
    CONTROL_ST4PORT = 19
    CAM_COLOR = 20
    CAM_BIN1X1MODE = 21
    CAM_BIN2X2MODE = 22
    CAM_BIN3X3MODE = 23
    CAM_BIN4X4MODE = 24
    CAM_8BITS = 34
    CAM_16BITS = 35
    CAM_GPS = 36
    CONTROL_AMPV = 41
    CONTROL_CFWSLOTSNUM = 44
    CAM_SINGLEFRAMEMODE = 57
    CAM_LIVEVIDEOMODE = 58
    CAM_IS_COLOR = 59

class QhyCam:
    def __init__(self):
        self.interface = cdll.LoadLibrary('.\\qhy\\qhyccd.dll')

        # get camera id
        self.interface.GetQHYCCDId.argtypes = [ctypes.c_uint32, ctypes.c_char_p]
        # get handle via camera id
        self.interface.OpenQHYCCD.argtypes = [ctypes.c_char_p]
        self.interface.OpenQHYCCD.restype = ctypes.c_void_p
        # close camera
        self.interface.CloseQHYCCD.argtypes = [ctypes.c_void_p]

        # read mode
        self.interface.GetQHYCCDNumberOfReadModes.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)]
        self.interface.GetQHYCCDReadModeName.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_char_p]
        self.interface.GetQHYCCDReadModeResolution.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
                                                        ctypes.POINTER(ctypes.c_uint32)]
        self.interface.SetQHYCCDReadMode.argtypes = [ctypes.c_void_p, ctypes.c_uint32]

        # set single stream mode or live stream mode
        self.interface.SetQHYCCDStreamMode.argtypes = [ctypes.c_void_p, ctypes.c_uint32]

        # initialize camera
        self.interface.InitQHYCCD.argtypes = [ctypes.c_void_p]

        # get camera chip information
        self.interface.GetQHYCCDChipInfo.argtypes = [ctypes.c_void_p,
                                            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
                                            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
                                            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
                                            ctypes.POINTER(ctypes.c_uint32)]
        # get parameters value
        self.interface.GetQHYCCDParam.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        self.interface.GetQHYCCDParam.restype = ctypes.c_double

        # set parameters
        self.interface.SetQHYCCDParam.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_double]
        # set debayer on or off, only for color camera
        self.interface.SetQHYCCDDebayerOnOff.argtypes = [ctypes.c_void_p, ctypes.c_bool]
        # set bin mode
        self.interface.SetQHYCCDBinMode.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        # set resolution and ROI
        self.interface.SetQHYCCDResolution.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                                                ctypes.c_uint32]

        # start single stream mode exposing
        self.interface.ExpQHYCCDSingleFrame.argtypes = [ctypes.c_void_p]
        # get single frame data
        self.interface.GetQHYCCDSingleFrame.argtypes = [ctypes.c_void_p,
                                                ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
                                                ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
                                                ctypes.POINTER(ctypes.c_uint8)]
        # cancel single exposing and camera will NOT output frame data
        self.interface.CancelQHYCCDExposingAndReadout.argtypes = [ctypes.c_void_p]

        # start live stream mode
        self.interface.BeginQHYCCDLive.argtypes = [ctypes.c_void_p]
        # get live frame data
        self.interface.GetQHYCCDLiveFrame.argtypes = [ctypes.c_void_p,
                                                ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
                                                ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
                                                ctypes.POINTER(ctypes.c_uint8)]
        # stop live stream mode
        self.interface.StopQHYCCDLive.argtypes = [ctypes.c_void_p]

        # convert image data
        self.interface.Bits16ToBits8.argtypes = [ctypes.c_void_p,
                                            ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint8),
                                            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint16, ctypes.c_uint16]

        ret = self.interface.InitQHYCCDResource()
        print("InitQHYCCDResource() ret =", ret)

        num = self.interface.ScanQHYCCD()
        print("ScanQHYCCD() num =", num)

        for index in range(num):
            print("index =", index)

            id_buffer = ctypes.create_string_buffer(40)
            ret = self.interface.GetQHYCCDId(index, id_buffer)
            result_id = id_buffer.value.decode("utf-8")
            print("GetQHYCCDId() ret =", ret, "id =", result_id)

            self.camhandle = self.interface.OpenQHYCCD(id_buffer)
            print("OpenQHYCCD() camhandle =", hex(self.camhandle))
            if self.camhandle != 0:
                break
        
        ret = self.interface.SetQHYCCDReadMode(self.camhandle, 0)
        print("SetQHYCCDReadMode() ret =", ret)

        ret = self.interface.SetQHYCCDStreamMode(self.camhandle, 0)
        print("SetQHYCCDStreamMode() ret =", ret)
        
        ret = self.interface.InitQHYCCD(self.camhandle)
        print("InitQHYCCD() ret =", ret)

        ret = self.interface.SetQHYCCDParam(self.camhandle, CONTROL_ID.CONTROL_TRANSFERBIT.value, 16.0)
        print("SetQHYCCDParam() 16 bits ret = ", ret)

        ret = self.interface.SetQHYCCDDebayerOnOff(self.camhandle, False)
        print("SetQHYCCDDebayerOnOff() false ret =", ret)
        
        chipW = ctypes.c_double()
        chipH = ctypes.c_double()
        imageW = ctypes.c_uint32()
        imageH = ctypes.c_uint32()
        pixelW = ctypes.c_double()
        pixelH = ctypes.c_double()
        imageB = ctypes.c_uint32()
        ret = self.interface.GetQHYCCDChipInfo(self.camhandle, byref(chipW), byref(chipH), byref(imageW), byref(imageH), byref(pixelW),
                                        byref(pixelH), byref(imageB))
        print("GetQHYCCDChipInfo() ret =", ret)
        print("GetQHYCCDChipInfo() chip  info =", chipW.value, "x", chipH.value, "mm")
        print("GetQHYCCDChipInfo() pixel info =", pixelW.value, "x", pixelH.value, "um")
        print("GetQHYCCDChipInfo() image info =", imageW.value, "x", imageH.value, imageB.value, "bits")
        self.width, self.height = imageW.value, imageH.value

        ret = self.interface.SetQHYCCDBinMode(self.camhandle, 1, 1)
        #print("SetQHYCCDBinMode() ret =", ret)

        ret = self.interface.SetQHYCCDResolution(self.camhandle, 0, 0, imageW.value, imageH.value)
        #print("SetQHYCCDResolution() ret =", ret)

        ret = self.interface.SetQHYCCDParam(self.camhandle, CONTROL_ID.CONTROL_EXPOSURE.value, 100000.0)
        #print("SetQHYCCDParam() exposure 20ms ret =", ret)

        ret = self.interface.SetQHYCCDParam(self.camhandle, CONTROL_ID.CONTROL_GAIN.value, 50.0)
        #print("SetQHYCCDParam() gain 40 ret =", ret)

        ret = self.interface.SetQHYCCDParam(self.camhandle, CONTROL_ID.CONTROL_OFFSET.value, 80.0)
        #print("SetQHYCCDParam() offset 60 ret =", ret)

        ret = self.interface.SetQHYCCDParam(self.camhandle, CONTROL_ID.CONTROL_USBTRAFFIC.value, 0.0)
        #print("SetQHYCCDParam() usbtraffic 0 ret =", ret)

        self.Shutters = {'N/A': 0}
        self.Modes = {'N/A': 0}
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
        pass

    def getImage(self):
        w = ctypes.c_uint32()
        h = ctypes.c_uint32()
        b = ctypes.c_uint32()
        c = ctypes.c_uint32()
        length = self.width * self.height * 4
        print("datasize =", length)
        imgdata = (ctypes.c_uint8 * length)()
        length = self.width * self.height
        imgdata_raw8 = (ctypes.c_uint8 * length)()

        ret = self.interface.ExpQHYCCDSingleFrame(self.camhandle)
        print("ExpQHYCCDSingleFrame() ret =", ret)

        ret = self.interface.GetQHYCCDSingleFrame(self.camhandle, byref(w), byref(h), byref(b), byref(c), imgdata)
        print("GetQHYCCDSingleFrame() ret =", ret, "w =", w.value, "h =", h.value, "b =", b.value, "c =", c.value,
            "data size =", int(w.value * h.value * b.value * c.value / 8))
        print("data =", imgdata[100000])
        return np.frombuffer(imgdata, dtype=np.uint16).reshape(-1,self.height,self.width)[0]

    def getFps(self):
        ret = self.interface.GetQHYCCDParam(self.camhandle, CONTROL_ID.CONTROL_SPEED.value)
        return ret

    def getExptime(self):
        ret = self.interface.GetQHYCCDParam(self.camhandle, CONTROL_ID.CONTROL_EXPOSURE.value)
        return ret

    def getGain(self):
        ret = self.interface.GetQHYCCDParam(self.camhandle, CONTROL_ID.CONTROL_GAIN.value)
        return ret

    def getTemp(self):
        ret = self.interface.GetQHYCCDParam(self.camhandle, CONTROL_ID.CONTROL_CURTEMP.value)
        return ret

    def getRoi(self):
        return "Not Supported"

    def getShutter(self):
        return "Not Supported"

    def getMode(self):
        return "Not Supported"

    def setFps(self, fps):
        ret = self.interface.SetQHYCCDParam(self.camhandle, CONTROL_ID.CONTROL_SPEED.value, float(fps))
        if ret == 0:
            return True
        return False

    def setExptime(self, exptime):
        ret = self.interface.SetQHYCCDParam(self.camhandle, CONTROL_ID.CONTROL_EXPOSURE.value, float(exptime))
        if ret == 0:
            return True
        return False

    def setGain(self, gain):
        ret = self.interface.SetQHYCCDParam(self.camhandle, CONTROL_ID.CONTROL_GAIN.value, 50.0)
        if ret == 0:
            return True
        return False

    def setTemp(self, temp):
        print("[Warning] Changing the temperature is not supported")
        return False

    def setRoi(self, roi):
        print("[Warning] Changing the Region of Interest is not supported")
        return False

    def setMode(self, hdr_mode):
        print("[Warning] Changing the HDR-mode is not supported")
        return False

    def setShutter(self, shutter):
        print("[Warning] Changing the shutter mode is not supported")
        return False