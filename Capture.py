import sys
print(sys.version)

FLControl_version = "v1"

import FliSdk_V2

from os import PathLike
from os.path import isdir
import time
import ctypes
from pathlib import Path
import subprocess

from astropy.io import fits
import numpy as np

from Shutdown import exit
#def exit(context, mes, error=False):
#    print(error, mes)
#    if error:
#        raise ValueError("")



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



def check(status):
    if not status:
        print("Error while setting camera.")
        exit(context)
    return

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
    log(f"{f'{time.gmtime():%Y-%m-%d %H:%M}':.^30}\n")
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
    hdr['TIME-OBS']=f"{TimeStart:%Y-%m-%d %H:%M}"
    hdr['TIME-END']=f"{TimeStop:%Y-%m-%d %H:%M}"
    hdr['TEMP-DET']=f"{Temp}"
    hdr['FPS']=f"{FPS}"
    hdr['EXP-TIME']=f"{IntTime}"
    hdr['GAIN']=f"{Gain}"
    hdr['HDR']=f"{HDR}"
    hdr['COMMENT']=Note

    hdu = fits.PrimaryHDU(data=array,header=hdr)
    hdu.writeto(file, overwrite=True)
    

def get_bias(context, file: PathLike, count: int, temp: int, gain: str):

    res, max_fps = FliSdk_V2.FliCredTwo.GetMaxFpsUsb(context)
    #max_fps = FliSdk_V2.FliSerialCamera.GetFpsMax(context)
    FliSdk_V2.FliSerialCamera.SetFps(context, max_fps)
    res, fps = FliSdk_V2.FliSerialCamera.GetFps(context)
    if np.abs(fps - max_fps) > 1:
        print(f"Camera FPS set to {fps}, instead of the desired {max_fps}. Exiting...")
        exit(context)
    print(f"FPS Set to {fps}")
    
    FliSdk_V2.FliCredTwo.EnableRawImages(context, True)
    FliSdk_V2.FliCredTwo.SetTempSnakeSetPoint(context, temp)

    get_frames(context, count, fps, gain, file, comment="Bias Frames")


def get_bias2(context, file: PathLike, count: int, temp:int, gain: str):
    FliSdk_V2.FliCredTwo.EnableRawImages(context, True)
    FliSdk_V2.FliCredTwo.SetTempSnakeSetPoint(context, temp)

    FliSdk_V2.FliCredTwo.SetConversionGain(context, gain)
    res, gain = FliSdk_V2.FliCredTwo.GetConversionGain(context)

    while FliSdk_V2.FliCredTwo.GetTempSnakeSetPoint(context) != FliSdk_V2.FliCredTwo.GetTempSnake(context):
        time.sleep(1) # Sleep until temp matches the setpoint
    res, temp = FliSdk_V2.FliCredTwo.GetTempSnake(context)

    TimeStart = time.gmtime()
    FliSdk_V2.FliCredTwo.BuildBiasHdrC1(context)
    TimeStop = time.gmtime()

    FliSdk_V2.FliCredTwo.SendBiasHdrC1File(context, "temp.fits")
    buffer = fits.open("temp.fits")[0].data
    write_fits(file, buffer, TimeStart, TimeStop, temp, 0, 0, gain, True, "Auto Bias Capture")

def get_dark(context, file: PathLike, count: int, fps: float, temp: int, gain: str):
    res,max_fps = FliSdk_V2.FliCredTwo.GetMaxFpsUsb(context)
    if fps > max_fps:
        print("FPS higher than max allowed value")
        exit(context)
    FliSdk_V2.FliSerialCamera.SetFps(context, fps)
    res,fps = FliSdk_V2.FliSerialCamera.GetFps(context)
    
    FliSdk_V2.FliCredTwo.EnableRawImages(context, True)
    FliSdk_V2.FliCredTwo.SetTempSnakeSetPoint(context, temp)

    get_frames(context, count, fps, gain, file, comment="Bias Frames")


def get_frames(context, count: int, fps: int, gain: str, writeto:PathLike, comment=""):
    frame_capacity = FliSdk_V2.GetImagesCapacity(context)
    
    width, height = FliSdk_V2.GetCurrentImageDimension(context)
    buffer = np.zeros((count, height, width))
    ArrayType = ctypes.c_uint16 * width * height

    FliSdk_V2.FliCredTwo.SetConversionGain(context,gain)
    res, gain = FliSdk_V2.FliCredTwo.GetConversionGain(context)

    FliSdk_V2.FliCredTwo.SetHdrCalibrationOff(context)
    res, HDR = FliSdk_V2.FliCredTwo.GetHdrState(context)

    while np.abs(FliSdk_V2.FliCredTwo.GetTempSnakeSetPoint(context)[1] - FliSdk_V2.FliCredTwo.GetTempSnake(context)[1]) > 0.5:
        print("Cooling Down...")
        print(f"T = {FliSdk_V2.FliCredTwo.GetTempSnake(context)[1]}")
        time.sleep(1) # Sleep until temp matches the setpoint
    print("Temperature Setpoint Reached")
    res, temp = FliSdk_V2.FliCredTwo.GetTempSnake(context)
    
    print("Starting Capture...")
    TimeStart = time.gmtime()
    if count < frame_capacity:
        FliSdk_V2.EnableGrabN(context, count)
        FliSdk_V2.Start(context)
        while FliSdk_V2.IsGrabNFinished(context) == False:
            time.sleep(count/fps)
        FliSdk_V2.Stop(context)
        
        for i in range(count):
            pointer = FliSdk_V2.GetRawImage(context, -1*count+i)
            pa = ctypes.cast(pointer, ctypes.POINTER(ArrayType))
            buffer[i] = np.ndarray((height, width), dtype=np.uint16, buffer=pa.contents)
    else:
        i = 0
        while i<count-frame_capacity:
            FliSdk_V2.EnableGrabN(context, frame_capacity)
            FliSdk_V2.Start(context)
            while FliSdk_V2.IsGrabNFinished(context) == False:
                time.sleep(frame_capacity/fps)
            FliSdk_V2.Stop(context)

            for j in range(frame_capacity):
                pointer = FliSdk_V2.GetRawImage(context, -1*frame_capacity+j)
                pa = ctypes.cast(pointer, ctypes.POINTER(ArrayType))
                buffer[i+j] = np.ndarray((height, width), dtype=np.uint16, buffer=pa.contents)
            i += frame_capacity
	
        FliSdk_V2.EnableGrabN(context, (count-i))
        FliSdk_V2.Start(context)
        while FliSdk_V2.IsGrabNFinished(context) == False:
            time.sleep((count-i)/fps)
        FliSdk_V2.Stop(context)
        for j in range(count-i):
            pointer = FliSdk_V2.GetRawImage(context, -1*(count-i)+j)
            pa = ctypes.cast(pointer, ctypes.POINTER(ArrayType))
            buffer[i+j] = np.ndarray((height, width), dtype=np.uint16, buffer=pa.contents)

    TimeStop = time.gmtime()
    print("Done")

    write_fits(writeto, buffer, TimeStart, TimeStop, temp, fps,
               1/fps, gain, HDR, comment)


if __name__=="__main__":

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
    check(FliSdk_V2.SetCamera(context, listOfCameras[cameraIndex]))
    
    check(FliSdk_V2.SetMode(context, FliSdk_V2.Mode.Full))
    check(FliSdk_V2.Update(context))

    check(FliSdk_V2.FliCredTwo.SetTempSnakeSetPoint(context, Temperature))

    get_bias(context, bias_name, biasFrames, Temperature, Gain)
    get_dark(context, dark_name, darkFrames, FPS, Temperature, Gain)

    exit(context, "Clean Exit")
