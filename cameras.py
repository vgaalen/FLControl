import numpy as np
from typing import Literal

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
    def getExptime(self):
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
    def setExptime(self, exptime):
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

        # self.spot_x, self.spot_y = self.width/2, self.height/2
        self.spot_x, self.spot_y = 10*np.random.randn(2)+50

    def Start(self):
        pass

    def Stop(self):
        pass

    def shutdown(self):
        pass

    def getImage(self):
        from astropy.modeling.functional_models import Gaussian2D

        # self.spot_x = self.spot_x+10*np.random.randn()
        # self.spot_y = self.spot_y+10*np.random.randn()
        # while self.spot_x < 0 or self.spot_x > self.width or self.spot_y < 0 or self.spot_y > self.height:
        #     self.spot_x = self.spot_x + 1 * np.random.randn()
        #     self.spot_y = self.spot_y + 1 * np.random.randn()

        x, y = np.ogrid[:self.height, :self.width]
        xx, yy = np.meshgrid(x, y)
        img = Gaussian2D.evaluate(xx, yy, 10, self.spot_x, self.spot_y, 5, 5, 0)
        return img

    def getFps(self):
        return "DEMO"

    def getExptime(self):
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

    def setExptime(self, exptime):
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

def Start(interface, cam, interface: Literal["Demo", "FLI", "QHY", "Allied"]):
    if interface=="Demo":
        return DemoCam()
    elif interface == "FLI":
        from first_light import start_fli_cam
        return start_fli_cam()
    elif interface=="QHY":
        from qhy import QhyCam
        return QhyCam()
    elif interface=="Allied":
        from allied import AlliedCam
        # return AlliedCam(interface, cam)
        raise Exception("Invalid input")
    else:
        raise Exception("Invalid input")