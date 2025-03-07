import sdk.FliSdk_V2 as FliSdk
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

        FliSdk.FliCblueOne.SetDeviceTemperatureSelector(self.context, 0) # set temperature location to sensor

        self.ShutterMap = {'Global': 0, 'Rolling': 1, 'GlobalReset': 2}
        self.HdrMap = {'Mono8': 0, 'Mono10': 1, 'Mono12': 2}

        input()
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
    
    def setShutter(self, shutter):
        if shutter in self.ShutterMap:
            res = False
            while not res:
                res = FliSdk.FliCblueSfnc.GetSensorShutterMode(self.context, self.ShutterMap[shutter])
        else:
            raise NotImplementedError("")
    
    def getShutter(self):
        res = False
        while not res:
            res, val = FliSdk.FliCblueSfnc.GetSensorShutterMode(self.context)
        for key, ind in self.ShutterMap:
            if ind==val:
                return key
    
    def setHdr(self, mode):
        if mode in self.HdrMap:
            FliSdk.FliCblueSfnc.SetPixelFormat(self.context, self.HdrMap[mode])
        else:
            raise NotImplementedError("")
    
    def getHdr(self):
        res, val = FliSdk.FliCblueSfnc.GetPixelFormat(self.context)
        for key, ind in self.ShutterMap:
            if ind==val:
                return key



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
        #self.getShutter = cam_func(self, FliSdk.FliCblueSfnc.GetSensorShutterMode)
        #self.setShutter = cam_func(self, FliSdk.FliCblueSfnc.SetSensorShutterMode)
        self.setHdr = cam_func(self, self.interface.EnableHdr, convert=bool)
        self.getHdr = cam_func(self, self.interface.GetHdrState)
        # TODO: Binning, reboot

        self.HdrMap = {'True': 1, 'False': 0}
        self.ShutterMap = {'Not Supported': 0}
    
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
    def getRoi():
        raise NotImplementedError("")
    def getShutter():
        raise NotImplementedError("")
    def setShutter():
        raise NotImplementedError("")

# Seems like the is no reason to separate out Cred, CredOne, CredTwo, CredThree
# class CRED2(CRED):
#     def __init__(self, context)
#         interface = FliSdk.FliCredTwo
#         super().__init__(context, interface)

class DAO_CAM:
    def __init__(self, name="dao"):
        import dao
        
        self.shm = {
            #'img': dao.shm(f"/tmp/{name}.im.shm",buffer) # TODO: how to determine height, width here?
            'fps': dao.shm(f"/tmp/{name}Fps.im.shm", np.zeros((1,1)).astype(np.float32)),
            'exptime': dao.shm(f"/tmp/{name}Dit.im.shm", np.zeros((1,1)).astype(np.float32)),
            'gain': dao.shm(f"/tmp/{name}Gain.im.shm", np.zeros((1,1)).astype(np.float32)),
            'mode': dao.shm(f"/tmp/{name}Mode.im.shm", np.zeros((1,1)).astype(np.str_)),
            'shutter': dao.shm(f"/tmp/{name}Shutter.im.shm", np.zeros((1,1)).astype(np.str_)),
            'roi': dao.shm(f"/tmp/{name}Roi.im.shm", np.zeros((1,5)).astype(np.int16))
        }

        self.setFps = dao_func(self.shm['fps']).set
        self.getFps = dao_func(self.shm['fps']).get
        self.setTint = dao_func(self.shm['exptime']).set
        self.getTint = dao_func(self.shm['exptime']).get
        self.setGain = dao_func(self.shm['gain']).set
        self.getGain = dao_func(self.shm['gain']).get
        self.setMode = dao_func(self.shm['mode']).set
        self.getMode = dao_func(self.shm['mode']).get
        self.setShutter = dao_func(self.shm['shutter']).set
        self.getShutter = dao_func(self.shm['shutter']).get
        self.setRoi = dao_func(self.shm['roi']).set
        self.getRoi = dao_func(self.shm['roi']).get
        # TODO: HDR?, Binning, reboot
    
    def start(self):
        raise NotImplementedError
        # shm['running']=True
    def stop(self):
        raise NotImplementedError
        # shm['running']=False
    def shutdown(self):
        raise NotImplementedError


class cam_func:
    def __init__(self, cam, func, convert=False):
        self.func = func
        self.cam = cam
        self.convert = convert
    
    def __call__(self, *args, **kwargs):
        res = [False]
        while not res[0]:
            if self.convert is not False:
                res = [self.func(self.cam.context, *[self.convert(x) for x in args], **kwargs)]
            else:
                res = [self.func(self.cam.context, *args, **kwargs)]
        return res[1:].unpack()

class dao_func:
    def __init__(self, shm):
        self.shm
    
    def get(self):
        return self.shm.get_data(check=True)

    def set(self, data):
        return self.shm.set_data(data)


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
    elif FliSdk.IsCred(context):
        return CRED(context, FliSdk.FliCred)
    elif FliSdk.IsCredOne(context):
        return CRED(context, FliSdk.FliCredOne)
    elif FliSdk.IsCredTwo(context):
        return CRED(context, FliSdk.FliCredTwo)
    elif FliSdk.IsCredThree(context):
        return CRED(context, FliSdk.FliCredThree)

