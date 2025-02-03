"""
Script that safely turns off the camera.
This is done by warming it up to room-temperature and making sure that it is no longer capturing frames
"""

import FliSdk_V2
import time

def exit(context, message="", error=True):
    FliSdk_V2.FliCredTwo.SetTempSnakeSetPoint(context, 20)

    FliSdk_V2.Stop(context)

    res, temp = FliSdk_V2.FliCredTwo.GetTempSnake(context)
    print(res,temp)
    while temp < 15 or not res:
        time.sleep(1)
        res, temp = FliSdk_V2.FliCredTwo.GetTempSnake(context)
        print(res, temp)
    
    FliSdk_V2.Exit(context)

    if error:
        raise ValueError(message)
    else:
        print(message)

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
    FliSdk_V2.SetCamera(context, listOfCameras[cameraIndex])
    FliSdk_V2.SetMode(context, FliSdk_V2.Mode.Full)
    FliSdk_V2.Update(context)

    exit(context, error=False)