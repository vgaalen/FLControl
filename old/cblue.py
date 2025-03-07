#!/usr/bin/env -S ipython3 -i
#

"""CBlue camera daemon.
"""
import sys, os
import ctypes
import numpy as np
sys.path.append(os.getenv('FLISDK_DIR')+'/Python/lib')
import FliSdk_V2 as FliSdk
import time
#import dao
import threading
from time import sleep
import pickle
import polars as pl
from os.path import isfile
from shm import SharedMemory

def getRoi(context) -> tuple[int, int, int, int]:
    """Get current region-of-interest on the camera.
    """
    res, isenabled, roi = FliSdk.GetCroppingState(context)
    w, h = FliSdk.GetCurrentImageDimension(context)
    if isenabled:
        return [1,roi.col1, roi.row1, roi.col2-roi.col1 + 1, roi.row2-roi.row1 + 1]
    else:
        return  [0,0,0,w,h]

def getImage(context) -> np.ndarray:
    currentfilling = FliSdk.GetBufferFilling(context)
    n=0
    while n<1:
        if FliSdk.GetBufferFilling(context) != currentfilling:
            buffer=FliSdk.GetRawImageAsNumpyArray(context, -1)
            n=n+1
    return buffer

def setFps(context, fps):
    FliSdk.FliSerialCamera.SetFps(context, fps)

def setFps(context, fps):
    FliSdk.FliSerialCamera.SetFps(context, fps)
    time.sleep(0.05)
    getFps(context)
    
def getFps(context, disp=False) -> float:
    fps = float(FliSdk.FliSerialCamera.GetFps(context)[-1])
    if disp:
        print('Current FPS %.1f'%fps)
    return fps

def setTint(context, tInt):
    """Set the integration time, expressed in us.
    """
    if 'C-RED 3' in FliSdk.GetDetectedCameras(context)[0]:
        FliSdk.FliCredThree.SetTint(context, tInt)
    elif 'C-RED 2' in FliSdk.GetDetectedCameras(context)[0]:
        FliSdk.FliCredTwo.SetTint(context, tInt)
    elif 'C-BLUE 1' in FliSdk.GetDetectedCameras(context)[0]:
        FliSdk.FliCblueSfnc.SetExposureTime(context, tInt)
    else:
        print("Unsupported camera")
    time.sleep(0.05)
    getTint(context)
    
def getTint(context) -> float:
    tIntMin = 0
    tIntMax = 0
    tInt = 0
    if 'C-RED 3' in FliSdk.GetDetectedCameras(context)[0]:
        Tint = FliSdk.FliCredThree.GetTint(context)[-1]
        _, tIntMin, tIntMax = FliSdk.FliCredThree.GetTintRange(context)
    elif 'C-RED 2' in FliSdk.GetDetectedCameras(context)[0]:
        Tint = FliSdk.FliCredTwo.GetTint(context)[-1]
        _, tIntMin, tIntMax = FliSdk.FliCredTwo.GetTintRange(context)
    elif 'C-BLUE 1' in FliSdk.GetDetectedCameras(context)[0]:
        Tint = FliSdk.GetExposureTime(context)[-1]
        tIntMin = FliSdk.FliCblueSfnc.GetExposureTimeMin(context)[-1]
        tIntMax = FliSdk.FliCblueSfnc.GetExposureTimeMax(context)[-1]
    else:
        print("Unsupported camera")
    print('Intergration time range [%.2e, %.2e] us'%(tIntMin,tIntMax))
    print('Intergation time set to %.2e us'%Tint)
    return Tint

def setTemp(context, temp):
    if 'C-RED 3' in FliSdk.GetDetectedCameras(context)[0]:
        FliSdk.FliCredThree.SetSensorTemp(context, temp)
    elif 'C-RED 2' in FliSdk.GetDetectedCameras(context)[0]:
        FliSdk.FliCredTwo.SetSensorTemp(context, temp)
    elif 'C-BLUE 1' in FliSdk.GetDetectedCameras(context)[0]:
        #FliSdk.FliCblueOne.SetDeviceTemperatureSelector(context, temp)
        FliSdk.FliCblueOne.SetDeviceCoolingEnable(context, True)
        FliSdk.FliCblueOne.SetDeviceCoolingSetpoint(context, temp)
    else:
        print("Unsupported camera")
    time.sleep(0.05)
    #getTemp(context)
   

def getTemp(context,disp=False) -> float:
    if 'C-RED 3' in FliSdk.GetDetectedCameras(context)[0]:
        temp = FliSdk.FliCredThree.GetAllTemp(context)[4]
    elif 'C-RED 2' in FliSdk.GetDetectedCameras(context)[0]:
        temp = FliSdk.FliCredTwo.GetAllTemp(context)[4]
    elif 'C-BLUE 1' in FliSdk.GetDetectedCameras(context)[0]:
        #temp = FliSdk.FliCblueOne.GetDeviceCoolingSetpoint
        temp = FliSdk.FliCblueSfnc.GetDeviceTemperatrue(context)[1]
    else:
        print("Unsupported camera")
        temp = 0
    
    if disp:
        print('Current sensor temperature %.2f°C'%temp)
    else:
    	return temp

def getGain(context):
    if 'C-RED 3' in FliSdk.GetDetectedCameras(context)[0]:
        gain = FliSdk.FliCredThree.GetConversionGain(context)[1]
        print('Conversion gain is %s'%gain)
    elif 'C-BLUE 1' in FliSdk.GetDetectedCameras(context)[0]:
        gain = FliSdk.FliCblueSfnc.GetGain(context)[1]
    else:
        print('unsupported camera')
        gain = 0
    return gain

def setGain(context, gain):
    if 'C-RED 3' in FliSdk.GetDetectedCameras(context)[0]:
        if gain in ['low','medium','high']:
            FliSdk.FliCredThree.SetConversionGain(context,gain)
            print('Conversion gain set to %s'%FliSdk.FliCredThree.GetConversionGain(context)[1])
        else:
            print("Gain is not valid, it should be 'low', 'medium' or 'high'")
    elif 'C-BLUE 1' in FliSdk.GetDetectedCameras(context)[0]:
        if (type(gain)==float or type(gain)==int) and (gain>=0 and gain<=48):
            FliSdk.FliCblueSfnc.SetGain(context, gain)
        else:
            print("Gain is not valid, it should be in the range 0-48 dB")
    else:
        print('Unsupported camera')

def getBlackLevel(context):
    return FliSdk.FliCblueSfnc.GetBlackLevel(context)

def setRoi(context, status, x0, y0, w, h): #TODO: set region of interest
    FliSdk.FliCblueOne.SetSparseMode(context, status)
    FliSdk.FliCblueOne.SetSparseWidth(context, w)
    FliSdk.FliCblueOne.SetSparseHeight(context, h)
    FliSdk.FliCblueOne.SetSparseOffsetX(context, x0)
    FliSdk.FliCblueOne.SetSparseOffsetY(context, y0)
#	col1 = int(cx - w//2) 
#	col2 = int(cx + w//2)
#	row1 = int(cy - h//2)
#	row2 = int(cy + h//2)
#	if 'C-RED 3' in FliSdk.GetDetectedCameras(context)[0]:
#        FliSdk.FliCredThree.SetAgcRoi(context, col1, col2, row1, row2)
#    elif 'C-RED 2' in FliSdk.GetDetectedCameras(context)[0]:
#        FliSdk.FliCredTwo.SetAgcRoi(context, col1, col2, row1, row2)
#    else:
#        print("Unsupported camera")

def ROI_OFF(context):
    FliSdk.FliCblueOne.SetSparseMode(context, 0)

def setMode(context, mode):
    FliSdk.FliCblueOne.SetUserSetSelector(context, mode)

def getMode(context):
    return FliSdk.FliCblueOne.GetUserSetSelector(context)

def setShutter(context, shutter):
    FliSdk.FliCblueSfnc.SetSensorShutterMode(context, shutter)

def getShutter(context):
    return FliSdk.FliCblueSfnc.GetSensorShutterMode(context)
    
def imAcq(context, obj, shm):
    try:
        while 1:
            frame = getImage(obj)
            shm = frame #.set_data(frame)
    except KeyboardInterrupt:
        print()
        print('End of acquisition')

class CtrlLoop():
    def __init__(self, context, shm, get_func, set_func):
        self.context = context
        self.shm = shm
        self.get_func = get_func
        self.set_func = set_func

        self.get_running = False
        self.set_running = False

    def start(self, type="get", interval=1):
        if type=="get":
            self.get_running = True
            threading.Thread(target = self.shm, args = (self, interval))
        elif type=="set":
            self.set_running = True
            threading.Thread(target = self.shm, args = (self, interval))
        else:
            raise NotImplementedError("Not Implemented")

    def stop(self):
        self.get_running = False
        self.set_running = False

    def write_shm(self, interval):
        while self.set_running:
            val = self.get_func()
            #if val != 0:
            self.shm = val#.set_data(val)
            sleep(interval)

    def read_shm(self, interval):
        while self.get_running:
            val = self.shm#.get_data(check=True)
            if val != 0:
                self.set_value(val)
            sleep(interval)


def fpsCtrl(obj, shm):
    while 1:
        fps = shm#.get_data(check=True)[0,0]
        print(f"detection of new FPS : {fps} Hz, applying.")
        setFps(obj, fps)
        sleep(1)
	
def ditCtrl(obj, shm):
    while 1:
        dit = shm#.get_data(check=True)[0,0]
        print(f"detection of new DIT : {dit} s, applying.")
        setTint(obj, dit)
        sleep(1)

def tempCtrl(obj, shm):
    while 1:
        temp = shm#.get_data(check=True)[0,0]
        print(f"Temperature set to : {temp} °C, applying.")
        setTemp(obj, temp)
        sleep(1)

#def temp2Ctrl(obj, shm):


def blCtrl(context, obj, shm):
    while 1:
        bl = getBlackLevel(context)
        shm = np.array(bl)#.set_data(np.array(bl))
        sleep(1)

def gainCtrl(context, obj, shm):
    gain = getGain(context)
    while 1:
        if shm != gain:#.get_data(check=True)[0,0] != gain:
            setGain(context, shm)#.get_data(check=True)[0,0])
        sleep(1)

def roiCtrl(context, obj, shm):
    roi = shm#.get_data(check=True)
    while 1:
        if np.sum(roi)==0.:
            shm = getRoi(context)#.set_data(getRoi(context))
        elif np.any(roi != getRoi(context)):
            setRoi(*roi.tolist())
        sleep(1)



def Stop(context):
    FliSdk.FliCblueSfnc.ExecuteAcquisitionStop(context)

def Shutdown(context):
    Stop(context)
    setTemp(context, 20)
    while getTemp(context)<15:
        sleep(1)
    FliSdk.FliCblueSfnc.ExecuteDeviceShutdown(context)

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
    print("select name for the shared memory: ")

    shmName = input()
    shm = SharedMemory()

    # if camera is available
    if cameras_list[0]!='Usb#' and len(cameras_list)>=1:
        res = FliSdk.SetCamera(context, cameras_list[camId])
        FliSdk.Update(context)
    else:
        raise ConnectionError("No camera found...")

    # Set to capture raw-frames
    # Set temperature measure location

    FliSdk.FliCblueOne.SetDeviceFanMode(context, True)
    FliSdk.FliCblueOne.SetGlowReduction(context, False)
    FliSdk.FliCblueOne.SetConversionEfficiency(context, 1)

    FliSdk.Start(context)
    
    #shm = createShm(context)
    
    #FliSdk.FliSerialCamera.SendCommand(fli_obj, 'set led off')
    FliSdk.FliCred.EnableLed(context, False)

    acqThread = threading.Thread(target = imAcq, args = (context, shm))
    
    fps_ctrl = CtrlLoop(context, shm['fps'], getFps, setFps)
    dit_ctrl = CtrlLoop(context, shm['dit'], getTint, setTint)
    tempsetpoint_ctrl = CtrlLoop(context, shm['set_temp'], getTemp, setTemp)
    temp_ctrl = CtrlLoop(context, shm['temp'], getTemp, setTemp)
    gain_ctrl = CtrlLoop(context, shm['gain'], getGain, setGain)
    roi_ctrl = CtrlLoop(context, shm['roi'], getRoi, setRoi)
    mode_ctrl = CtrlLoop(context, shm['mode'], getMode, setMode)
    shutter_ctrl = CtrlLoop(context, shm['shutter'], getShutter, setShutter)

    for ctrl_loop in [fps_ctrl, dit_ctrl, tempsetpoint_ctrl, gain_ctrl, roi_ctrl, mode_ctrl, shutter_ctrl]:
        ctrl_loop.start(type="set")

    for ctrl_loop in [temp_ctrl]:
        ctrl_loop.start(type="get")

    acqThread.start()

    with open('context.pkl', 'wb') as f:
        pickle.dump(context, f)

    return context

def loadContext():
    with open('context.pkl', 'rb') as f:
        context = pickle.load(context, f)
    return context


if __name__=="__main__":
    context, shm = Start()
