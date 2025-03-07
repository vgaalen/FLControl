from time import sleep
from astropy.io import fits
from datetime import datetime
import numpy as np

#import dao
#from cblue import *

def capture(cam, nframes, progress_func):
    height, width = cam.getImage().shape
    temps = []
    buffer = np.zeros((nframes, height, width), dtype=np.uint16)
    timeStart = datetime.now()
    for i in range(nframes):
        # On CBlue no trigger is available, so we use timing
        sleep(exptime)
        progress_func(itt=i)

        buffer[i] = cam.getImage()
        temps.append(cam.getTemp())
    
    timeStop = datetime.now()
    # Write to fits
    hdr = fits.Header()
    hdr['TIME-OBS']= (f"{timeStart:%Y-%m-%d %H:%M}", "Starting Time of Observation (local time)")
    hdr['TIME-END']= (f"{timeStop:%Y-%m-%d %H:%M}", "End Time of Observation (local time)")
    hdr['TEMP-DET']= (f"{np.mean(temps)+274.15}", "Detector Temperature in Kelvin") # Convert temperature to Kelvin
    hdr['TEMP-MIN']= (f"{np.min(temps)+274.15}", "Minimum Temperature Reached in Kelvin")
    hdr['TEMP-MAX']= (f"{np.max(temps)+274.15}", "Maximum Temperature Reached in Kelvin")
    hdr['FPS']= (f"{cam.getFps()}", "Framerate in Hz")
    hdr['EXPTIME']= (f"{cam.getTint()}", "Exposure Time in Seconds")
    hdr['GAIN']= (f"{cam.getGain()}", "Camera Gain Setting")
    hdr['ROI']= (f"{cam.getRoi()}", "Region of Interest Setting [status, x-anchor, y-anchor, width, height]")
    #hdr['HDR']=f"{HDR}"
    #hdr['COMMENT']=Note
    hdu = fits.PrimaryHDU(data=buffer,header=hdr)
    hdu.writeto(f"CblueOne_{datetime.now()}", overwrite=True)
    return 1

if __name__=="__main__":
    import mappings

    shm = loadShm()
    if np.sum(shm['img'].get_data(check=True))==0.:
        print("CBlue Deamon is not running")
        print("Starting...")
        context, shm = Start()
    else:
        context = loadContext
    
    # Take user input for settings: nframes, exptime, temp, gain
    nframes = None
    while type(nframes) != int or nframes<0:
        nframes = input("Number of frames to record : ")
        try:
            nframes = int(nframes)
        except:
            print("Not an integer")

    exptime = None
    while type(exptime) not in [int, float] or exptime<0:
        exptime = input("Exposure time in seconds : ")
        try:
            exptime = float(exptime)
        except:
            print("Not a float")

    temp = None
    while type(temp) not in [int, float]:
        temp = input("Temperature Setpoint in degrees Celcius : ")
        try:
            temp = float(temp)
        except:
            print("Not a float")

    gain = None
    while type(gain) not in [int, float]:
        gain = input("Gain in dB : ")
        try:
            gain = float(gain)
        except:
            print("Not a float")

    # Check if camera initialised through cblue.py (otherwise start automatically?)
    # TODO
    # Start writing frames to disk
    mode = None
    while type(mode)!=int or mode < 0 or mode > 3:
       mode = input("""Set Camera Mode \n
       0 - Default 8-bit
       1 - Default 12-bit
       2 - High Sensitivity 8-bit
       3 - High Sensitivity 12-bit""")
       try:
           mode = int(mode)
       except:
           print("Not an integer")
    shm['mode'] = mode

    shutter = None
    while type(shutter)!=int or shutter<0 or shutter>2:
       shutter = input("""Set Camera Shutter Mode \n
       0 - Global Shutter
       1 - Rolling Shutter
       2 - GlobalReset (not recommended - leads to different exptime for each line""")
       try:
           shutter = int(shutter)
       except:
           print("Not an integer")
    shm['shutter'] = shutter

    # Set camera settings
    shm['dit'].set_data(np.array(exptime))
    shm['fps'].set_data(np.array(1/exptime)) # TODO: does the cblue support 100% exptime?
    shm['gain'].set_data(np.array(gain))
    shm['temp'].set_data(np.array(temp))

    capture(context, nframes)



    
