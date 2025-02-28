import FliSdk_V2 as FliSdk
import numpy as np
from time import sleep

class FLI_CAMERA:
    def __init__(self, context):
        self.context = context
        self.getFps = cam_func(self, FliSdk.FliSerialCamera.GetFps)
        self.setFps = cam_func(self, FliSdk.FliSerialCamera.SetFps)

    def start(self):
        FliSdk.Start()
    
    def stop(self):
        FliSdk.Stop()
    
    def getRoi(self) -> tuple[int, int, int, int]:
        res, isenabled, roi = FliSdk.GetCroppingState(self.context)
        w, h = FliSdk.GetCurrentImageDimension(self.context)
        if isenabled:
            return [1,roi.col1, roi.row1, roi.col2-roi.col1 + 1, roi.row2-roi.row1 + 1]
        else:
            return  [0,0,0,w,h]
    
    def getImage(self) -> np.ndarray:
        currentfilling = FliSdk.GetBufferFilling(self.context)
        n=0
        while n<1:
            if FliSdk.GetBufferFilling(self.context) != currentfilling:
                buffer=FliSdk.GetRawImageAsNumpyArray(self.context, -1)
                n=n+1
        return buffer

class CBLUE(FLI_CAMERA):
    def __init__(self, context):
        super().__init__(context)
        self.getTint = cam_func(self, FliSdk.FliCblueSfnc.GetExposureTime)
        self.setTint = cam_func(self, FliSdk.FliCblueSfnc.SetExposureTime)
        self.getTemp = cam_func(self, FliSdk.FliCblueOne.GetDeviceCoolingSetpoint)
        self.setTemp = cam_func(self, FliSdk.FliCblueOne.SetDeviceCoolingSetpoint)
        self.getGain = cam_func(self, FliSdk.FliCblueSfnc.GetGain)
        self.setGain = cam_func(self, FliSdk.FliCblueSfnc.SetGain)
        self.getMode = cam_func(self, FliSdk.FliCblueOne.GetUserSetSelector)
        self.setMode = cam_func(self, FliSdk.FliCblueOne.SetUserSetSelector)
        self.getShutter = cam_func(self, FliSdk.FliCblueSfnc.GetSensorShutterMode)
        self.setShutter = cam_func(self, FliSdk.FliCblueSfnc.SetSensorShutterMode)
        # TODO: HDR?, Binning, reboot

    def start(self):
        FliSdk.FliCblueOne.SetDeviceCoolingEnable(self.context, True)
        FliSdk.FliCblueOne.SetDeviceFanMode(self.context, True)
        FliSdk.FliCblueOne.SetGlowReduction(self.context, False)
        FliSdk.FliCblueOne.SetConversionEfficiency(self.context, 1)
    
    def shutdown(self):
        FliSdk.FliCblueSfnc.ExecuteAcquisitionStop(self.context)
        self.setTemp(20)
        while self.getTemp()<15:
            sleep(1)
        FliSdk.FliCblueSfnc.ExecuteDeviceShutdown(self.context)
 
    def setRoi(self, status, x0, y0, w, h): #TODO: set region of interest
        status = [False]
        while np.sum(status) < len(status):
            status = []
            status.append(FliSdk.FliCblueOne.SetSparseMode(self.context, status))
            status.append(FliSdk.FliCblueOne.SetSparseWidth(self.context, w))
            status.append(FliSdk.FliCblueOne.SetSparseHeight(self.context, h))
            status.append(FliSdk.FliCblueOne.SetSparseOffsetX(self.context, x0))
            status.append(FliSdk.FliCblueOne.SetSparseOffsetY(self.context, y0))

class CRED(FLI_CAMERA):
    def __init__(self, context, interface):
        super().__init__(context)
        self.interface = interface
        self.getTint = cam_func(self, self.interface.GetTint)
        self.setTint = cam_func(self, self.interface.SetTint)
        self.getTemp = cam_func(self, self.interface.GetSensorTemp)
        self.setTemp = cam_func(self, self.interface.SetSensorTemp)
        self.getGain = cam_func(self, self.interface.GetConversionGain)
        self.setGain = cam_func(self, self.interface.SetConversionGain) 
        self.getShutter = cam_func(self, FliSdk.FliCblueSfnc.GetSensorShutterMode)
        self.setShutter = cam_func(self, FliSdk.FliCblueSfnc.SetSensorShutterMode)
        # TODO: HDR, Binning, reboot
    
    def start(self):
        #FliSdk.FliCred.EnableLed(self.context, False)
        self.interface.EnableRawImages(self.context, True)
    
    def shutdown(self):
        self.stop()
        self.setTemp(20)
        while self.getTemp()<15:
            sleep(1)
    
    def setRoi(self, status, x0, y0, w, h): #TODO: set region of interest
        raise NotImplementedError("This function is not available on CRED")

# Seems like the is no reason to separate out Cred, CredOne, CredTwo, CredThree
# class CRED2(CRED):
#     def __init__(self, context)
#         interface = FliSdk.FliCredTwo
#         super().__init__(context, interface)

class cam_func:
    def __init__(self, cam, func):
        self.func = func
        self.cam = cam
    
    def __call__(self, *args, **kwargs):
        res = [False]
        while not res[0]:
            res = [self.func(self.cam.context, *args, **kwargs)]
        return res[1:].unpack()


def Start():
    context = FliSdk.Init()
    # call before DetectCameras or it fails for some reason ...
    grabbers_list = FliSdk.DetectGrabbers(context)
    for s in grabbers_list:
        print('- '+s)
    cameras_list = FliSdk.DetectCameras(context)
    print(f"{len(cameras_list)} cameras detected")
    print("Select the camera")
    for k in range(len(cameras_list)):
        print(f"{k} : {cameras_list[k]}")
    print("select camera #:")
    camId = int(input())
    print(f"camera {camId} selected: {cameras_list[camId]}")

    # if camera is available
    if cameras_list[0]!='Usb#' and len(cameras_list)>=1:
        res = FliSdk.SetCamera(context, cameras_list[camId])
        FliSdk.Update(context)
    else:
        raise ConnectionError("No camera found...")
    
    if FliSdk.IsClueOne(context):
        return CBLUE(context)
    elif FliSdk.IsCred(context) or FliSdk.IsCredOne(context) or FliSdk.IsCredTwo(context) or FliSdk.IsCredThree(context):
        return CRED(context)