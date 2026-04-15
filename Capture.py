from astropy.io import fits
from datetime import datetime
import numpy as np

def capture(cam, nframes, file=f"test.fits"):#:%Y%m%d-%H%M%S
    temps = []
    timeStart = datetime.now()
    exptime = cam.getExptime()
    print(exptime)

    temps.append(cam.getTemp())
    buffer = cam.getImages(nframes)
    
    timeStop = datetime.now()
    # Write to fits
    hdr = fits.Header()
    hdr['TIME-OBS']= (f"{timeStart:%Y-%m-%d %H:%M}", "Starting Time of Observation (local time)")
    hdr['TIME-END']= (f"{timeStop:%Y-%m-%d %H:%M}", "End Time of Observation (local time)")
    hdr['TEMP-DET']= (f"{np.mean(temps)}", "Detector Temperature in Celsius")
    hdr['TEMP-SET']= (f"{cam.getTempSetpoint()}", "Cooling Setpoint in Celsius")
    hdr['TEMP-MIN']= (f"{np.min(temps)}", "Minimum Temperature Reached in Celcius")
    hdr['TEMP-MAX']= (f"{np.max(temps)}", "Maximum Temperature Reached in Celcius")
    hdr['FPS']= (f"{cam.getFps()}", "Framerate in Hz")
    hdr['EXPTIME']= (f"{cam.getExptime()}", "Exposure Time in Milliseconds")
    hdr['GAIN']= (f"{cam.getGain()}", "Camera Gain Setting")
    hdr['ROI']= (f"{cam.getRoi()}", "Region of Interest Setting [status, x0, y0, width, height]")
    hdr['CAM_NAME']= (f"{cam.name}", "Camera Name")
    try:
        hdr['BADPX_CR']= (f"{cam.getBadpx()}", "State of Bad Pixel Correction")
    except:
        pass
    hdu = fits.PrimaryHDU(data=buffer,header=hdr)
    hdu.writeto(file, overwrite=True)
    return 1