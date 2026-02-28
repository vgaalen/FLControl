import numpy as np
from time import sleep

def interface(func):
    def wrapper(*args, **kwargs):
        try:
            for i in range(5):
                res = func(*args, **kwargs)
                if res is True or (type(res) in [list, tuple] and res[0] is True):
                    break
            return res
        except:
            print(f"[Warning] {func.__name__} returned negative result")
            return False, None
    return wrapper

def start_fli_cam():
    import sdk.FliSdk_V2 as FliSdk
    import ctypes
    context = FliSdk.Init()
    # call before DetectCameras or it fails for some reason ...
    grabbers_list = FliSdk.DetectGrabbers(context)
    for s in grabbers_list:
        print('- ' + s)
    cameras_list = FliSdk.DetectCameras(context)
    print(f"{len(cameras_list)} cameras detected")
    print("Select the camera")
    for k in range(len(cameras_list)):
        print(f"{k} : {cameras_list[k]}")
    print("select camera #:")
    cam_id = int(input())
    print(f"camera {cam_id} selected: {cameras_list[cam_id]}")

    # if camera is available
    if cameras_list[0] != 'Usb#' and len(cameras_list) >= 1:
        res = FliSdk.SetCamera(context, cameras_list[cam_id])
        FliSdk.Update(context)
    else:
        raise ConnectionError("No camera found...")

    if FliSdk.IsCblueOne(context):
        return Cblue(context, cameras_list[cam_id])
    elif FliSdk.IsCredOne(context):
        return Cred(context, FliSdk.FliCredOne, cameras_list[cam_id])
    elif FliSdk.IsCredTwo(context):
        return Cred2(context, FliSdk.FliCredTwo, cameras_list[cam_id])
    elif FliSdk.IsCredThree(context):
        return Cred(context, FliSdk.FliCredThree, cameras_list[cam_id])
    elif FliSdk.IsCred(context):
        return Cred(context, FliSdk.FliCred, cameras_list[cam_id])
    else:
        raise NotImplementedError("")

class FliCamera:
    def __init__(self, context, name="UNKNOWN"):
        import sdk.FliSdk_V2 as FliSdk
        import ctypes
        self.name = name
        self.context = context
        self._update_dims()

        self.getFps = cam_func(self, FliSdk.FliSerialCamera.GetFps)
        self.setFps = cam_func(self, FliSdk.FliSerialCamera.SetFps)
   
    def _update_dims(self):
        self.width, self.height = FliSdk.GetCurrentImageDimension(self.context)

    def Start(self):
        self.start()
        FliSdk.Start(self.context)
    
    def Stop(self):
        #self.stop()
        FliSdk.Stop(self.context)
    
    @interface
    def getRoi(self) -> tuple[True, list[int, int, int, int]]:
        res, isenabled, roi = FliSdk.GetCroppingState(self.context)
        w, h = FliSdk.GetCurrentImageDimension(self.context)
        if isenabled:
            return True, [1,roi.col1, roi.row1, roi.col2-roi.col1 + 1, roi.row2-roi.row1 + 1]
        else:
            return True, [0,0,0,w,h]
    
    @interface
    def setRoi(self, status, x0, y0, width, height) -> tuple[int, int, int, int]:
        if type(self) == Cred:
            if x0%32!=0 or y0%32!=0 or width%32!=0 or height%32!=0:
                print("[Warning] CRED cameras only allow cropping in multiples of 32")
                return 0
        print("setting roi")

        state = FliSdk.CroppingData()
        state['col1'] = x0
        state['col2'] = x0 + width
        state['row1'] = y0
        state['row2'] = y0 + height
        res = FliSdk.SetCroppingState(self.context, status, state)
        self._update_dims()
        print(res)
        return res
    
    @interface
    def getImages(self, n) -> np.ndarray:
        ArrayType = ctypes.c_uint16 * self.width * self.height
        currentfilling = FliSdk.GetBufferFilling(self.context)
        buffer = np.zeros((n, self.height, self.width))
        i = 0
        while i<n:
            if FliSdk.GetBufferFilling(self.context) > currentfilling:
                #buffer[i]=FliSdk.GetRawImageAsNumpyArray(self.context, -1)
                pointer = FliSdk.GetRawImage(self.context, currentfilling)
                pa = ctypes.cast(pointer, ctypes.POINTER(ArrayType))
                buffer[i] = np.frombuffer(pa.contents, dtype=np.uint16).reshape((self.height,self.width))
                i = i+1
                currentfilling += 1
        return True, buffer
    
    @interface
    def getImage(self):
        ArrayType = ctypes.c_uint16 * self.width * self.height
        pointer = FliSdk.GetRawImage(self.context, -1)
        pa = ctypes.cast(pointer, ctypes.POINTER(ArrayType))
        img = np.frombuffer(pa.contents, dtype=np.uint16).reshape((self.height,self.width))
        return img
    

class Cblue(FliCamera):
    def __init__(self, context, name):
        super().__init__(context, name=name)
        self.getTint = cam_func(self, FliSdk.FliCblueSfnc.GetExposureTime)
        self.setTint = cam_func(self, FliSdk.FliCblueSfnc.SetExposureTime)
        self.getTemp = cam_func(self, FliSdk.FliCblueSfnc.GetDeviceTemperature)
        self.getTempSetpoint = cam_func(self, FliSdk.FliCblueOne.GetDeviceCoolingSetpoint)
        self.setTemp = cam_func(self, FliSdk.FliCblueOne.SetDeviceCoolingSetpoint)
        self.getGain = cam_func(self, FliSdk.FliCblueSfnc.GetGain)
        self.setGain = cam_func(self, FliSdk.FliCblueSfnc.SetGain)
        self.getMode = cam_func(self, FliSdk.FliCblueOne.GetUserSetSelector)
        self.setMode = cam_func(self, FliSdk.FliCblueOne.SetUserSetSelector)

        FliSdk.FliCblueOne.SetDeviceTemperatureSelector(self.context, 0) # set temperature location to sensor

        self.Shutters = {'Global': 0, 'Rolling': 1, 'GlobalReset': 2}
        self.Modes = {'Mono8': 0, 'Mono10': 1, 'Mono12': 2}

        # TODO: Binning, reboot
        # TODO: Get Temperature Setpoint

    def start(self):
        FliSdk.FliCblueOne.SetDeviceCoolingEnable(self.context, True)
        FliSdk.FliCblueOne.SetDeviceFanMode(self.context, True)
        FliSdk.FliCblueOne.SetGlowReduction(self.context, False)
        FliSdk.FliCblueOne.SetConversionEfficiency(self.context, 1)
        FliSdk.FliCblueSfnc.SetDeviceIndicatorMode(self.context, 0)
    
    @interface
    def shutdown(self):
        FliSdk.FliCblueSfnc.ExecuteAcquisitionStop(self.context)
        self.setTemp(20)
        while self.getTemp()[-1]<15:
            sleep(1)
        FliSdk.FliCblueSfnc.ExecuteDeviceShutdown(self.context)
        return True
    
    @interface
    def bias(self):
        res, min_exptime = FliSdk.FliCblueOne.GetExposureTimeMinReg(self.context)
        self.setTint(min_exptime)
        return True
    
    @interface
    def setRoi(self, status, x0, y0, w, h):
        status = [False]
        while np.sum(status) < len(status):
            status = []
            status.append(FliSdk.FliCblueOne.SetSparseMode(self.context, status))
            status.append(FliSdk.FliCblueOne.SetSparseWidth(self.context, w))
            status.append(FliSdk.FliCblueOne.SetSparseHeight(self.context, h))
            status.append(FliSdk.FliCblueOne.SetSparseOffsetX(self.context, x0))
            status.append(FliSdk.FliCblueOne.SetSparseOffsetY(self.context, y0))
        return True
    
    @interface
    def setShutter(self, shutter):
        if shutter in self.ShutterMap:
            res = FliSdk.FliCblueSfnc.GetSensorShutterMode(self.context, self.ShutterMap[shutter])
        else:
            raise NotImplementedError("")
        return True
    
    @interface
    def getShutter(self):
        res, val = FliSdk.FliCblueSfnc.GetSensorShutterMode(self.context)
        for key, ind in self.ShutterMap:
            if ind==val:
                return True, key
        return False
    
    @interface
    def setHdr(self, mode):
        if mode in self.HdrMap:
            res = FliSdk.FliCblueSfnc.SetPixelFormat(self.context, self.HdrMap[mode])
        else:
            raise NotImplementedError("")
        return True
   
    @interface
    def getHdr(self):
        res, val = FliSdk.FliCblueSfnc.GetPixelFormat(self.context)
        for key, ind in self.ShutterMap:
            if ind==val:
                return key
        return False


class Cred(FliCamera):
    def __init__(self, context, interface, name):
        super().__init__(context, name=name)
        self.interface = interface
        self.getTint = cam_func(self, self.interface.GetTint)
        self.setTint = cam_func(self, self.interface.SetTint)
        self.getTemp = cam_func(self, self.interface.GetSensorTemp)
        self.setTemp = cam_func(self, self.interface.SetSensorTemp)
        self.getTempSetpoint = cam_func(self, self.interface.GetTempSnakeSetPoint)
        self.getGain = cam_func(self, self.interface.GetConversionGain)
        self.setGain = cam_func(self, self.interface.SetConversionGain) 
        #self.getShutter = cam_func(self, FliSdk.FliCblueSfnc.GetSensorShutterMode)
        #self.setShutter = cam_func(self, FliSdk.FliCblueSfnc.SetSensorShutterMode)
        #self.setHdr = cam_func(self, self.interface.EnableHdr, convert=bool)
        #self.getHdr = cam_func(self, self.interface.GetHdrState)
        self.setBadpx = cam_func(self, self.interface.EnableBadPixel)
        self.getBadpx = cam_func(self, self.interface.GetBadPixelState)
        # TODO: Binning, reboot

        self.Shutters = {'Not Supported': 0}
        self.Modes = {'N/A': 0}
    
    def start(self):
        self.interface.EnableRawImages(self.context, True)
        self.interface.EnableBadPixel(self.context, False)
        FliSdk.FliCred.EnableLed(self.context, False)

    @interface
    def shutdown(self):
        self.Stop()
        # self.setTemp(20)
        # while self.getTemp()<15:
        #     print(self.getTemp())
        #     sleep(1)
        return True
    
    @interface
    def bias(self):
        res1, max = self.interface.GetMaxFpsUsb(self.context)
        res2 = self.setFps(max)
        res3, min, max = self.interface.GetTintRange(self.context)
        res4 = self.setTint(min)
        return res1*res2*res3*res4
        
    
    #def setRoi(self, status, x0, y0, w, h):
    #    #res = self.interface.SetCropping
    #    return [False]
    #    #self.interface.SetRoi(self.context, status, x0, y0, w, h)
    #def getRoi(self):
    #    #return [False]
    #    self.interface.GetRoi(self.context)
    def getShutter(self):
        return [False]
        #raise NotImplementedError("")
    def setShutter(self):
        raise NotImplementedError("")
    
class Cred2(Cred):
    def __init__(self, context, interface, name):
        super().__init__(context, interface, name=name)
        self.Modes = {'CDS': 0, 'HDR': 1, 'HDR Extended': 2, 'IMRO 2': 3, 'IMRO 5': 4, 'IMRO 10': 5}
    
    def getRaw(self):
        return FliSdk.FliCredTwo.GetRawImagesState(self.context)

    def getHdr(self):
        IMRO = FliSdk.FliCredTwo.GetNbReadWoReset(self.context)
        HDR = FliSdk.FliCredTwo.GetHdrState(self.context)
        HDR_EXTENDED = FliSdk.FliCredTwo.GetHdrExtendedState(self.context)
        return True, [HDR, HDR_EXTENDED, IMRO]
    
    def setHdr(self, mode):
        print(mode)
        if mode == 'CDS':
            FliSdk.FliCredTwo.EnableHdr(self.context, False)
            FliSdk.FliCredTwo.EnableHdrExtended(self.context, False)
            FliSdk.FliCredTwo.SetNbReadWoReset(self.context, 1)
            self.interface.EnableRawImages(self.context, True)
            self.interface.EnableBadPixel(self.context, False)
        elif mode == "HDR":
            FliSdk.FliCredTwo.EnableHdr(self.context, True)
            FliSdk.FliCredTwo.EnableHdrExtended(self.context, False)
            FliSdk.FliCredTwo.SetNbReadWoReset(self.context, 1)
            self.interface.EnableRawImages(self.context, False)
            self.interface.EnableBadPixel(self.context, False)
        elif mode == "HDR Extended":
            FliSdk.FliCredTwo.EnableHdr(self.context, False)
            FliSdk.FliCredTwo.EnableHdrExtended(self.context, True)
            FliSdk.FliCredTwo.SetNbReadWoReset(self.context, 1)
            self.interface.EnableRawImages(self.context, False)
            self.interface.EnableBadPixel(self.context, False)
        elif mode == "IMRO 2":
            FliSdk.FliCredTwo.EnableHdr(self.context, False)
            FliSdk.FliCredTwo.EnableHdrExtended(self.context, False)
            FliSdk.FliCredTwo.SetNbReadWoReset(self.context, 2)
            self.interface.EnableRawImages(self.context, False)
            self.interface.EnableBadPixel(self.context, False)
        elif mode == "IMRO 5":
            FliSdk.FliCredTwo.EnableHdr(self.context, False)
            FliSdk.FliCredTwo.EnableHdrExtended(self.context, False)
            FliSdk.FliCredTwo.SetNbReadWoReset(self.context, 5)
            self.interface.EnableRawImages(self.context, False)
            self.interface.EnableBadPixel(self.context, False)
        elif mode == "IMRO 10":
            FliSdk.FliCredTwo.EnableHdr(self.context, False)
            FliSdk.FliCredTwo.EnableHdrExtended(self.context, False)
            FliSdk.FliCredTwo.SetNbReadWoReset(self.context, 10)
            self.interface.EnableRawImages(self.context, False)
            self.interface.EnableBadPixel(self.context, False)
        else:
            print(mode)
            #raise NotImplementedError(f"{mode}")

class cam_func:
    def __init__(self, cam, func, convert=False):
        self.func = func
        self.cam = cam
        self.convert = convert

    @interface
    def __call__(self, *args, **kwargs):
        state = False
        while not state:
            if self.convert is not False:
                res = self.func(self.cam.context, *[self.convert(x) for x in args], **kwargs)
            else:
                res = self.func(self.cam.context, *args, **kwargs)
            if type(res) == list or type(res) == tuple:
                state = res[0]
            else:
                state = res
        return res

class DaoCam:
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

class dao_func:
    def __init__(self, shm):
        self.shm
    
    def get(self):
        return self.shm.get_data(check=True)

    def set(self, data):
        return self.shm.set_data(data)

class QhyCam:
    def __init__(self):
        from qhyccd import qhyccd
        self.cam = qhyccd.qhyccd()

        self.Shutters = {'N/A': 0}
        self.Modes = {'N/A': 0}

        self.width, self.height = 0,0

    def Start(self):
        try:
            self.cam.BeginLive()
            return True
        except:
            print("[Warning] Failed to start live mode")
            return False

    def Stop(self):
        try:
            self.cam.StopLive()
            return True
        except:
            print("[Warning] Failed to stor live mode")
            return False

    def shutdown(self):
        self.cam.StopLive()
        sleep(1)
        self.cam.close()

    def getImage(self):
        return self.cam.getImage()

    def getFps(self):
        return 1/(0.001*self.cam.exposureMS)

    def getTint(self):
        return self.cam.exposureMS

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
        self.cam.SetExposure(1000*1/fps)

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

class AlliedCam:
    def __init__(self):
        import vmbpy
        vmb = vmbpy.VmbSystem.get_instance()
        with vmb:
            cams = vmb.get_all_cameras()
            for cam in cams:
                print(cam)
            self.cam = cams[0]

        self.Shutters = {'N/A': 0}
        self.Modes = {'N/A': 0}

        self.width, self.height = 0,0

    def Start(self):
        self.cam.start_streaming()

    def Stop(self):
        self.cam.stop_streaming()

    def shutdown(self):
        pass

    def getImage(self):
        if self.cam.is_streaming():
            return self.cam.queue_frame()
        else:
            return self.cam.get_frame()

    def getFps(self):
        pass
    def getTint(self):
        pass
    def getGain(self):
        pass
    def getTemp(self):
        pass
    def getRoi(self):
        pass
    def getShutter(self):
        pass
    def getHdr(self):
        pass
    def setFps(self, fps):
        pass
    def setGain(self, gain):
        pass
    def setTemp(self, temp):
        pass
    def setRoi(self, roi):
        pass
    def setHdr(self, hdr_mode):
        pass
    def setShutter(self, shutter):
        pass

class CamTemplate:
    # For reference when adding new cameras
    def __init__(self):
        self.Shutters = {'N/A': 0}
        self.Modes = {'N/A': 0}
        self.width, self.height = 0, 0
    def Start(self):
        pass
    def Stop(self):
        pass
    def shutdown(self):
        pass
    def getImage(self):
        pass
    def getFps(self):
        pass
    def getTint(self):
        pass
    def getGain(self):
        pass
    def getTemp(self):
        pass
    def getRoi(self):
        pass
    def getShutter(self):
        pass
    def getHdr(self):
        pass
    def setFps(self, fps):
        pass
    def setGain(self, gain):
        pass
    def setTemp(self, temp):
        pass
    def setRoi(self, roi):
        pass
    def setHdr(self, hdr_mode):
        pass
    def setShutter(self, shutter):
        pass

class DemoCam:
    def __init__(self):
        self.Shutters = {'N/A': 0}
        self.Modes = {'N/A': 0}
        self.width, self.height = 100, 100

    def Start(self):
        pass

    def Stop(self):
        pass

    def shutdown(self):
        pass

    def getImage(self):
        return np.zeros((self.height, self.width))

    def getFps(self):
        return "DEMO"

    def getTint(self):
        return "DEMO"

    def getGain(self):
        return "DEMO"

    def getTemp(self):
        return "DEMO"

    def getRoi(self):
        return "DEMO"

    def getShutter(self):
        return "DEMO"

    def getHdr(self):
        return "DEMO"

    def setFps(self, fps):
        print(f"Setting fps to {float(fps)}")
        return True

    def setGain(self, gain):
        return True

    def setTemp(self, temp):
        return True

    def setRoi(self, roi):
        return True

    def setHdr(self, hdr_mode):
        return True

    def setShutter(self, shutter):
        return True

def Start():
    res = int(input("""Choose the camera type: 
    1: Demo
    2: First Light Imaging
    3: QHYCCD
    4: Allied Vision
    """))
    if res == 1:
        return DemoCam()
    elif res == 2:
        return start_fli_cam()
    elif res == 3:
        return QhyCam()
    elif res == 4:
        return AlliedCam()
    else:
        raise Exception("Invalid input")