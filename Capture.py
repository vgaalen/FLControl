import sys
print(sys.version)

import FliSdk_V2

from os import PathLike
import time

from astropy.io import fits
import numpy as np



############
# Settings #
############
Temperature = -15 # C
Gain = "High"
FPS = 100
biasFrames = 100
darkFrames = 100

def check(status):
    if not status:
        print("Error while setting camera.")
        exit()
    return

def exit(errmes=""):
    FliSdk_V2.FliCredTwo.SetTempSnakeSetPoint(context, 20)
    res, temp = FliSdk_V2.FliCredTwo.GetTempSnake(context)
    while temp < 15 or not res:
        time.sleep(1)
        res, temp = FliSdk_V2.FliCredTwo.GetTempSnake(context)
    raise ValueError(errmes)
    

def write_fits(file: PathLike, array: np.ndarray, TimeStart: time.struct_time, TimeStop: time.struct_time, Temp: int, FPS: int,
               IntTime: float, Gain: float, HDR: bool, Note: str):
    hdr = fits.Header()
    hdr['TIME-OBS']=f"{TimeStart}"
    hdr['TIME-END']=f"{TimeStop}"
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
        exit()
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
        exit()
    FliSdk_V2.FliSerialCamera.SetFps(context, fps)
    res,fps = FliSdk_V2.FliSerialCamera.GetFps(context)
    
    FliSdk_V2.FliCredTwo.EnableRawImages(context, True)
    FliSdk_V2.FliCredTwo.SetTempSnakeSetPoint(context, temp)

    get_frames(context, count, fps, gain, file, comment="Bias Frames")


def get_frames(context, count: int, fps: int, gain: str, writeto:PathLike, comment=""):
    frame_capacity = FliSdk_V2.GetImagesCapacity(context)
    
    width, height = FliSdk_V2.GetCurrentImageDimension(context)
    buffer = np.zeros((count, width, height))

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
        # FliSdk_V2.Start(context) #### SWITCH TO EnableGrabN
        # time.sleep(fps*count)
        # FliSdk_V2.Stop(context)
        # for i in range(count):
        #     buffer[i] = FliSdk_V2.GetRawImage(context,-1*i)
        FliSdk_V2.EnableGrabN(context, count)
        FliSdk_V2.Start(context)
        while FliSdk_V2.IsGrabNFinished(context) == False:
            time.sleep(count/fps)
        FliSdk_V2.Stop(context)
#        for i in range(count):
#            buffer[i] = FliSdk_V2.GetRawImage(context,-1*i)
#        print(FliSdk_V2.GetAvailableSaveFormats(context)[1])
        res = FliSdk_V2.SaveBuffer(context,"./temp.fits", int(frame_capacity-count-1), int(frame_capacity-1)
        if not res:
            print("Lost Connection")
            exit("Lost Connection")
        buffer = fits.open("temp.fits")[0].data
    else:
        i = 0
        while i<count-frame_capacity:
            # FliSdk_V2.Start(context)
            # time.sleep(fps*frame_capacity)
            # FliSdk_V2.Stop(context)
            FliSdk_V2.EnableGrabN(context, frame_capacity)
            FliSdk_V2.Start(context)
            while FliSdk_V2.IsGrabNFinished(context) == False:
                time.sleep(frame_capacity/fps)
#            for j in range(frame_capacity):
#                buffer[i] = FliSdk_V2.GetRawImage(context,-1*j)
#                i+=1
            res = FliSdk_V2.SaveBuffer(context, 'temp.fits', int(frame_capacity-count-1, int(frame_capacity-1))
            if not res:
                print("Lost Connection")
                exit("Lost Connection")
            buffer[i:i+frame_capacity] = fits.open("temp.fits")[0].data
        # FliSdk_V2.Start(context)
        # time.sleep(fps*(count-i))
        # FliSdk_V2.Stop(context)
        FliSdk_V2.EnableGrabN(context, (count-i))
        FliSdk_V2.Start(context)
        while FliSdk_V2.IsGrabNFinished(context) == False:
            time.sleep((count-i)/fps)
#        for j in range(count-i):
#            buffer[i+j] = FliSdk_V2.GetRawImage(context,-1*j)
        print(FliSdk_V2.GetAvailableSaveFormats)
        res = FliSdk_V2.SaveBuffer(context, 'temp.fits', -1*count, -1)
        if not res:
            print("Lost Connection")
            exit("Lost Connection")
        buffer[i:] = fits.open("temp.fits")[0].data
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
        exit()
    print("Done.")
    print("List of detected grabber(s):")
    for s in listOfGrabbers:
        print("- " + s)

    print("Detection of cameras...")
    listOfCameras = FliSdk_V2.DetectCameras(context)
    if len(listOfCameras) == 0:
        print("No camera detected, exit.")
        exit()
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

    get_bias(context,'test_bias.fits', biasFrames, Temperature, Gain)
    get_dark(context, 'test_dark.fits', darkFrames, FPS, Temperature, Gain)

    exit()
