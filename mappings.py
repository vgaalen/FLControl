
import numpy as np
from time import sleep
import ctypes

class PI_CAMERA:
    def __init__(self):
        import os
        from pathlib import Path
        libpath = Path("C:\\Program Files")
        os.add_dll_directory(libpath)

        import pylablib as pll
        pll.par["devices/dlls/picam"] = "C:\\Program Files\\Common Files\\Princeton Instruments\\Picam\\Runtime"
        from pylablib.devices import PrincetonInstruments

        cam_list = print(PrincetonInstruments.list_cameras())
        print(cam_list)
        self.cam_sn = input("Give the serial number of the desired camera\n")

        self.cam = PrincetonInstruments.PicamCamera(self.cam_sn)
        self.info = self.cam.get_device_info()
        self.name = f"PI {self.info.model} - {self.info.serial_number}"
        self.interface = self.info.interface

        self.translate = {'fps': 'Frame Rate Calculation',
                          'exptime': 'Exposure Time',
                          'roi': 'ROIs',
                          'readout_mode': 'ADC Quality',
                          'shutter_mode': 'Readout Control Mode',
                          'gain': 'ADC Analog Gain',
                          'temp-set': 'Sensor Temperature Set Point',
                          'temp-det': 'Sensor Temperature Reading',
                          'temp-status': 'Sensor Temperature Status',
                          'bit-depth': 'ADC Bit Depth'} # ['Sensor Temperature Status', 'Sensor Temperature Reading']
        
        self.readout_modes = self.cam.get_attribute('ADC Quality').values
        self.shutter_modes = self.cam.get_attribute('Readout Control Mode').values
        self.gain_modes = self.cam.get_attribute('ADC Analog Gain').values

    def set(self, attribute, value):
        print(self.cam.get_attribute(self.translate[attribute]).values)
        print(value)
        #self.cam.stop_acquisition()
        self.Stop()
        if attribute not in self.translate.keys():
            print(f"[Warning]: Unknown attribute, {attribute}")
            return
        if self.cam.get_attribute(self.translate[attribute]).writable:
            if type(value) in [int, float]:
                self.cam.set_attribute_value(self.translate[attribute], value)
            else:
                if value in self.cam.get_attribute(self.translate[attribute]).values or value == 'High Dynamic Range':
                    self.cam.set_attribute_value(self.translate[attribute], value)
                else:
                    print(f"[Warning]: {value} is not valid for parameter {self.translate[attribute]}. Options are {self.cam.get_attribute(self.translate[attribute]).values}")
        else:
            print(f"[Warning]: attribute '{self.translate[attribute]}' is not writable")
        #self.cam.start_acquisition()

    def get(self, attribute):
        return self.cam.get_attribute_value(self.translate[attribute])
    
    def set_roi(self, xmin, xmax, ymin, ymax, xbin=1, ybin=1):
        #self.cam.stop_acquisition()
        self.Stop()
        self.cam.set_roi(xmin, xmax, ymin, ymax, xbin, ybin)
        #self.cam.start_acquisition()
    
    def get_roi(self):
        roi = self.get('roi')
        print(roi[0])
        return f"x0:{roi[0].x}, w:{roi[0].width}, y0:{roi[0].y}, h:{roi[0].height}, x_bin:{roi[0].x_binning}, y_bin:{roi[0].y_binning}"
    
    def set_readout_mode(self, mode):
        self.Stop()
        if mode == 'High Speed':
            # self.set('readout_mode', mode)
            # self.set('bit-depth', '14 bits')
            # self.gain_modes = ['Low', 'High']
            settings = self.cam.get_all_attribute_values()
            print(settings[self.translate['readout_mode']], settings[self.translate['shutter_mode']],settings[self.translate['gain']])
            settings[self.translate['readout_mode']] = mode
            settings[self.translate['bit-depth']] = 14
            #settings[self.translate['shutter_mode']] = 'Rolling Shutter'
            #settings[self.translate['gain']] = ''#'Low'#'Medium#'High'#0#'HDR'
            self.cam.set_all_attribute_values(settings)
            print(self.cam.get_attribute(self.translate['gain']).values)
            print('done')
        elif mode == 'Low Noise':
            self.set('readout_mode', mode)
            self.set('bit-depth', 16)
            self.set('gain', 'Low')
            self.gain_modes = ['Low']
            # settings = self.cam.get_all_attribute_values()
            # print(settings[self.translate['readout_mode']], settings[self.translate['shutter_mode']],settings[self.translate['gain']])
            # settings[self.translate['readout_mode']] = mode
            # settings[self.translate['bit-depth']] = 16
            # #settings[self.translate['shutter_mode']] = 'Rolling Shutter'
            # settings[self.translate['gain']] = 'Low'#'Medium#'High'#0#'HDR'
            # self.cam.set_all_attribute_values(settings)
            # print(self.cam.get_attribute(self.translate['gain']).values)
            print('done')
        elif mode == 'High Dynamic Range':
            print("[Warning]: High Dynamic Range mode is unavailable")
            # self.set('readout_mode', mode)
            # self.set('bit-depth', 18)
            # self.set('shutter_mode', 'Rolling Shutter')
            # self.set('gain', 'High Dynamic Range')
            # self.gain_modes = ['']
            # print('done')
            # settings = self.cam.get_all_attribute_values()
            # print(settings[self.translate['readout_mode']], settings[self.translate['shutter_mode']],settings[self.translate['gain']])
            # settings[self.translate['readout_mode']] = mode
            # settings[self.translate['bit-depth']] = 18
            # settings[self.translate['shutter_mode']] = 'Rolling Shutter'
            # settings[self.translate['gain']] = ''#'Low'#'Medium#'High'#0#'HDR'
            # self.cam.set_all_attribute_values(settings)
            # print(self.cam.get_attribute(self.translate['gain']).values)
        else:
            print(f"[Warning]: {mode} is not valid for parameter {self.translate['readout_mode']}. Options are {self.cam.get_attribute(self.translate['readout_mode']).values}")
    
    def Stop(self):
        sleep(1)
        print(self.cam.acquisition_in_progress())
        if self.cam.acquisition_in_progress() == 1:
            self.cam.stop_acquisition()
            sleep(1)
        else:
            pass
    
    def Start(self):
        sleep(1)
        if self.cam.acquisition_in_progress() == 0:
            self.cam.start_acquisition()
            sleep(1)
        else:
            pass
        print(self.cam.get_attribute(self.translate['gain']).values)
    
    def Shutdown(self):
        while self.cam.is_opened():
            if True:
           # try:
                # TODO: Change for actual camera
                self.set('temp-set', 20.)
                self.Start()
                while np.abs(self.get('temp-set') - self.get('temp-det')) > 1:
                    print(self.get('temp-det'))
                    sleep(1)

                self.Stop()
                sleep(1)
                self.cam.close()                
                sleep(1)
            # except:
            #     pass
        return True

    def getImages(self, n) -> np.ndarray:
        if self.cam.acquisition_in_progress() == 0:
            return [0]
        buffer = [0]*n
        for i in range(n):
            self.cam.wait_for_frame()
            buffer[i] = self.cam.read_newest_image()
        return buffer
    
    def getImage(self):
        if self.cam.acquisition_in_progress() == 0:
            return [0]
        try:
            self.cam.wait_for_frame()
            img = self.cam.read_newest_image()
        except:
            return [0]
        
        if img is None:
            return [1, np.zeros((5,5))]
        else:
            return [1, img]
        
    def bias(self):
        min = self.cam.get_attribute(self.translate['exptime']).min
        self.set('exptime', min)
        return True

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

# TODO Refactor FLI_Camera to use cam.get(attribute, value) format and convert into FLI sdk format

class FLI_CAMERA:
    def __init__(self, context, name="UNKNOWN"):
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
            return  True, [0,0,0,w,h]
    
    @interface
    def setRoi(self, status, x0, y0, width, height) -> tuple[int, int, int, int]:
        state = FliSdk.CroppingData()
        state['col1'] = x0
        state['col2'] = x0 + width
        state['row1'] = y0
        state['row2'] = y0 + height
        res = FliSdk.SetCroppingState(self.context, status, state)
        self._update_dims()
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
        return True, img
    

class CBLUE(FLI_CAMERA):
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

        self.ShutterMap = {'Global': 0, 'Rolling': 1, 'GlobalReset': 2}
        self.HdrMap = {'Mono8': 0, 'Mono10': 1, 'Mono12': 2}

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


class CRED(FLI_CAMERA):
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
        self.setHdr = cam_func(self, self.interface.EnableHdr, convert=bool)
        self.getHdr = cam_func(self, self.interface.GetHdrState)
        self.setBadpx = cam_func(self, self.interface.EnableBadPixel)
        self.getBadpx = cam_func(self, self.interface.GetBadPixelState)
        # TODO: Binning, reboot

        self.HdrMap = {'True': 1, 'False': 0}
        self.ShutterMap = {'Not Supported': 0}
    
    def start(self):
        self.interface.EnableRawImages(self.context, True)
        self.interface.EnableBadPixel(self.context, False)
        FliSdk.FliCred.EnableLed(self.context, False)

    @interface
    def shutdown(self):
        self.Stop()
        self.setTemp(20)
        while self.getTemp()<15:
            print(self.getTemp())
            sleep(1)
        return True
    
    @interface
    def bias(self):
        res1, max = self.interface.GetMaxFpsUsb(self.context)
        res2 = self.setFps(max)
        res3, min, max = self.interface.GetTintRange(self.context)
        res4 = self.setTint(min)
        return res1*res2*res3*res4
        
    
    def setRoi(self, status, x0, y0, w, h):
        #res = self.interface.SetCropping
        return [False]
        #self.interface.SetRoi(self.context, status, x0, y0, w, h)
    def getRoi(self):
        return [False]
        #self.interface.GetRoi(self.context)
    def getShutter(self):
        return [False]
        #raise NotImplementedError("")
    def setShutter(self):
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


class dao_func:
    def __init__(self, shm):
        self.shm
    
    def get(self):
        return self.shm.get_data(check=True)

    def set(self, data):
        return self.shm.set_data(data)


def Start():
    camera_interface = input("type 0 for picam camera, 1 for first light camera\n")
    if camera_interface == '0':
       return PI_CAMERA()
    elif camera_interface == '1':
        import sdk.FliSdk_V2 as FliSdk
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
        
        if FliSdk.IsCblueOne(context):
            return CBLUE(context, cameras_list[camId])
        elif FliSdk.IsCredOne(context):
            return CRED(context, FliSdk.FliCredOne, cameras_list[camId])
        elif FliSdk.IsCredTwo(context):
            return CRED(context, FliSdk.FliCredTwo, cameras_list[camId])
        elif FliSdk.IsCredThree(context):
            return CRED(context, FliSdk.FliCredThree, cameras_list[camId])
        elif FliSdk.IsCred(context):
            return CRED(context, FliSdk.FliCred, cameras_list[camId])
    else:
        raise NotImplementedError('')
