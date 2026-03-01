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
        return self.cam.ExposureTime.get()

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
    def setTint(self, exptime):
        self.cam.ExposureTime.set(exptime)

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