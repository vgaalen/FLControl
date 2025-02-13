import sys
print(sys.version)

FLControl_version = "v1"

import FliSdk_V2

from os import PathLike
from os.path import isdir
import time
from datetime import datetime
import ctypes
from typing import Optional
from pathlib import Path
import subprocess

from astropy.io import fits
import numpy as np

from Shutdown import exit
#def exit(context, mes, error=False):
#    print(error, mes)
#    if error:
#        raise ValueError("")

def check(status):
    if not status:
        print("Error while setting camera.")
        exit(context)
    return

def saferun(func, *args, tries: Optional[int]=2):
    try:
        res, *args = func(*args)
        i=0
        while not res and i<tries:
            res, *args = func(*args)
            i += 1
        if res:
            return args
        else:
            print(f"Error while running {func}.")
            exit(context)
    except:
        res = func(*args)
        i=0
        while not res and i<tries:
            res = func(*args)
            i += 1
        if res:
            return
        else:
            print(f"Error while running {func}.")
            exit(context)


def write_metadata():
    Path(f"data/").mkdir(parents=True, exist_ok=True)

    hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    url = subprocess.check_output(['git', 'remote', '-v']).decode('ascii').strip()
    url = [z for y in url.split("@") for z in y.split("(")][1][:-1]

    with open("data/readme.txt", 'w') as readme:
        readme.write("These results were generated using the following codebase:\n")
        readme.write(f"{url}/{hash}   -   {FLControl_version}")

    log("==============================\n")
    log(f"{'Starting Run':.^30}\n")
    log(f"{f'{datetime.now():%Y-%m-%d %H:%M}':.^30}\n")
    log("==============================\n")

def log(message):
    with open(f"data/log.txt", "a") as f:
        f.write(message)

def print2(message):
    print(message)
    log(message+"\n")

    

def write_fits(file: PathLike, array: np.ndarray, TimeStart: time.struct_time, TimeStop: time.struct_time, Temp: int, FPS: int,
               IntTime: float, Gain: float, HDR: bool, Note: str):
    hdr = fits.Header()
    hdr['TIME-OBS']= (f"{TimeStart:%Y-%m-%d %H:%M}", "Starting Time of Observation (local time)")
    hdr['TIME-END']= (f"{TimeStop:%Y-%m-%d %H:%M}", "End Time of Observation (local time)")
    hdr['TEMP-DET']= (f"{Temp+274.15}", "Detector Temperature in Kelvin") # Convert temperature to Kelvin
    hdr['FPS']= (f"{FPS}", "Framerate in Hz")
    hdr['EXP-TIME']= (f"{IntTime}", "Exposure Time in Seconds")
    hdr['GAIN']= (f"{Gain}", "Camera Gain Setting")
    hdr['HDR']=f"{HDR}"
    hdr['COMMENT']=Note

    hdu = fits.PrimaryHDU(data=array,header=hdr)
    hdu.writeto(file, overwrite=True)
    

def get_bias(context, file: PathLike, count: int, temp: int, gain: str):
    #res, max_fps = FliSdk_V2.FliCredTwo.GetMaxFpsUsb(context)
    #check(res)
    max_fps = saferun(FliSdk_V2.FliCredTwo.GetMaxFpsUsb, context)[0]
    get_frames(context, count, temp, max_fps, gain, file, comment="Bias Frames")


def get_dark(context, file: PathLike, count: int, fps: float, temp: int, gain: str):
    # res,max_fps = FliSdk_V2.FliCredTwo.GetMaxFpsUsb(context)
    # check(res)
    max_fps = saferun(FliSdk_V2.FliCredTwo.GetMaxFpsUsb, context)[0]
    print(max_fps, fps)
    if fps > max_fps:
        print("FPS higher than max allowed value")
        exit(context)   
    get_frames(context, count, temp, fps, gain, file, comment="Bias Frames")


def get_frames(context, count: int, temp: float, fps: int, gain: str, writeto:PathLike, comment=""):
    saferun(FliSdk_V2.FliCredTwo.EnableRawImages,context, True)
    saferun(FliSdk_V2.FliCredTwo.SetTempSnakeSetPoint,context, temp)
    saferun(FliSdk_V2.FliSerialCamera.SetFps,context, fps)
    saferun(FliSdk_V2.FliCredTwo.SetConversionGain,context,gain)
    saferun(FliSdk_V2.FliCredTwo.SetHdrCalibrationOff,context)

    fps = saferun(FliSdk_V2.FliSerialCamera.GetFps,context)[0]
    gain = saferun(FliSdk_V2.FliCredTwo.GetConversionGain,context)[0]
    HDR = saferun(FliSdk_V2.FliCredTwo.GetHdrState,context)[0]
    frame_capacity = FliSdk_V2.GetImagesCapacity(context)
    print(fps,gain,HDR, frame_capacity)
    
    width, height = FliSdk_V2.GetCurrentImageDimension(context)
    buffer = np.zeros((count, height, width))
    ArrayType = ctypes.c_uint16 * width * height

    while np.abs(FliSdk_V2.FliCredTwo.GetTempSnakeSetPoint(context)[1] - FliSdk_V2.FliCredTwo.GetTempSnake(context)[1]) > 0.5:
        print(f"T = {FliSdk_V2.FliCredTwo.GetTempSnake(context)[1]}")
        if (FliSdk_V2.FliCredTwo.GetTempSnakeSetPoint(context)[1] - FliSdk_V2.FliCredTwo.GetTempSnake(context)[1]) > 0:
            print("Warming Up...")
        else:
            print("Cooling Down...")
        time.sleep(1) # Sleep until temp matches the setpoint
    print("Temperature Setpoint Reached")
    temp = saferun(FliSdk_V2.FliCredTwo.GetTempSnake,context)[0]
    
    print("Starting Capture...")
    TimeStart = datetime.now()
    print(TimeStart)
    #saferun(FliSdk_V2.Start,context)

    t1 = datetime.now()
    t2 = datetime.now()
    
    for i in range(count):
        saferun(FliSdk_V2.Start,context)
        time.sleep(1/fps+1)# - (t2-t1).seconds)
        saferun(FliSdk_V2.Stop,context)
        #t1 = datetime.now()
        #pointer = FliSdk_V2.GetRawImage(context, frame_capacity-count+i) ### PRODUCES ONLY 0's
        #pointer = FliSdk_V2.GetRawImage(context, -1*count+i) ### RETURNS IDENTICAL IMAGES
        pointer = FliSdk_V2.GetRawImage(context, -1)
        pa = ctypes.cast(pointer, ctypes.POINTER(ArrayType))
        # buffer[i] = np.ndarray((height, width), dtype=np.uint16, buffer=pa.contents)
        buffer[i] = np.frombuffer(pa.contents, dtype=np.uint16).reshape((height,width))
        #t2 = datetime.now() 

    #saferun(FliSdk_V2.Stop,context)
    TimeStop = datetime.now()
    print("Done")
    print(TimeStop)

    write_fits(writeto, buffer, TimeStart, TimeStop, temp, fps,
               1/fps, gain, HDR, comment)


def Initialize():
    context = FliSdk_V2.Init()

    print("Detection of grabbers...")
    listOfGrabbers = FliSdk_V2.DetectGrabbers(context)
    if len(listOfGrabbers) == 0:
        print("No grabber detected, exit.")
        exit(context)
    print("Done.")
    print("List of detected grabber(s):")
    for s in listOfGrabbers:
        print("- " + s)

    print("Detection of cameras...")
    listOfCameras = FliSdk_V2.DetectCameras(context)
    if len(listOfCameras) == 0:
        print("No camera detected, exit.")
        exit(context)
    print("Done.")
    print("List of detected camera(s):")
    i = 0
    for s in listOfCameras:
        print("- " + str(i) + " -> " + s)
        i = i + 1
    cameraIndex = int(input("Which camera to use? (0, 1, ...) "))
    print("Setting camera: " + listOfCameras[cameraIndex])
    saferun(FliSdk_V2.SetCamera,context, listOfCameras[cameraIndex])
    
    saferun(FliSdk_V2.SetMode,context, FliSdk_V2.Mode.Full)
    saferun(FliSdk_V2.Update,context)
    return context


if __name__=="__main__":

    ############
    # Settings #
    ############
    dark_name = "data/Dark.fits" # the file name (or absolute path) to write the dark images to
    bias_name = "data/Bias.fits"

    Temperature = -15 # C
    Gain = "High"
    FPS = 100
    biasFrames = 100
    darkFrames = 100

    context = Initialize()

    get_bias(context, bias_name, biasFrames, Temperature, Gain)
    get_dark(context, dark_name, darkFrames, FPS, Temperature, Gain)

    exit(context, "Clean Exit")
