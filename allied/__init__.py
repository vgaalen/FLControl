import ctypes
import numpy as np
from vmbpy import Camera, Frame, Stream, AllocationMode

class AlliedCam:
    def __init__(self, interface, cam):

        self.interface = interface
        self.cam = cam
        self.name = "Allied Vision Goldeye"

        self.img_radius = 100 # for cropping

        self.features = self.cam.get_all_features()
        
        for feat in self.features:
            if feat.get_name() == "DeviceTemperature":
                self.temp = feat 
            elif feat.get_name() == "DeviceTemperatureSelector":
                self.temp_sel = feat 
            elif feat.get_name() == "SensorTemperatureTargetSetpoint":
                self.temp_setpoint = feat 
            elif feat.get_name() == "ExposureTime":
                self.exptime = feat
            elif feat.get_name() == "AcquisitionFrameRate":
                self.fps = feat
            elif feat.get_name() == "Gain":
                self.gain = feat
            elif feat.get_name() == "SensorGain":
                self.gain2 = feat
            # "SensorTemperatureControlState"  "stable"

#             /// Feature name   : LUTSelector
# /// Display name   : LUTSelector
# /// Tooltip        : Selects which look-up table to control.
# /// Description    : Selects which look-up table to control.
# /// SFNC Namespace : Standard
# /// Value          : Luminance

# /// Feature name   : NUCDatasetExposureTime
# /// Display name   : NUCDatasetExposureTime
# /// Tooltip        : Exposure time at acquisition of the data set indexed by NUCDatasetSelector. The data set should be selected, so that the actual exposure time setting corresponds to the reference value.
# /// Description    : Exposure time at acquisition of the data set indexed by NUCDatasetSelector. The data set should be selected, so that the actual exposure time setting corresponds to the reference value.
# /// SFNC Namespace : Custom
# /// Value          : 1000.0

# /// Feature name   : AcquisitionFrameRate
# /// Display name   : AcquisitionFrameRate
# /// Tooltip        : Frame rate, in frames per second. This is applicable when either the FrameStart trigger mode is disabled, or the FrameStart trigger source is FixedRate. Depending on the exposure duration, the camera may not achieve the frame rate set here.
# /// Description    : Frame rate, in frames per second. This is applicable when either the FrameStart trigger mode is disabled, or the FrameStart trigger source is FixedRate. Depending on the exposure duration, the camera may not achieve the frame rate set here.
# /// SFNC Namespace : Standard
# /// Value          : 37.8000378000378

# /// Feature name   : AcquisitionFrameRateLimit
# /// Display name   : AcquisitionFrameRateLimit
# /// Tooltip        : This is the maximum frame rate possible for the current exposure duration and image format.
# /// Description    : This is the maximum frame rate possible for the current exposure duration and image format.
# /// SFNC Namespace : Custom
# /// Value          : 41.63024020648599

# /// Feature name   : ExposureTime
# /// Display name   : ExposureTime
# /// Tooltip        : Exposure duration, in microseconds.
# /// Description    : Exposure duration, in microseconds.
# /// SFNC Namespace : Standard
# /// Value          : 10000.0


        self.Shutters = {'N/A': 0}
        self.Modes = {'N/A': 0}

        self.width, self.height = self.cam.Width.get(), self.cam.Height.get()

        self.frame = None
        self.getImage()

    def Start(self):
        # self.cam.start_streaming()
        stream = self.cam.get_streams()[0]
        stream.GVSPAdjustPacketSize.run()
        while not stream.GVSPAdjustPacketSize.is_done():
            pass
        
        # allocation_mode = AllocationMode.AllocAndAnnounceFrame

        # self.cam.start_streaming(handler=self.frame_handler,
                                    # buffer_count=10,allocation_mode=allocation_mode)
    
    def frame_handler(self, cam: Camera, stream: Stream, frame: Frame):
        cam.queue_frame(frame)
        self.frame = np.frombuffer(frame.get_buffer(), dtype=np.uint16).reshape((self.height, self.width))

    def Stop(self):
        self.cam.stop_streaming()

    def shutdown(self):
        pass

    def getImage(self):
        frame = self.cam.get_frame()
        pointer = frame.get_buffer()
        data = np.frombuffer(pointer, dtype=np.uint16).reshape(self.height, self.width)
        return data
    
    def getImages(self, nframes):
        buffer = np.zeros((nframes, self.height, self.width))
        for i in range(nframes):
            buffer[i] = self.getImage()
        return buffer
#         # if self.cam.is_streaming:
#         #     if self.frame is None:
#         #         self.frame = self.cam.get_frame()
#         #     self.cam.queue_frame(self.frame)
#         # else:
#         #     self.frame = self.cam.get_frame()

#         # ArrayType = ctypes.c_uint16 * self.width * self.height
#         # buffer = np.zeros((self.height, self.width))
#         # buffer = np.frombuffer(self.frame.get_buffer(), dtype=np.uint16).reshape((self.height, self.width))
#         # return buffer

#         for frame in self.cam.get_frame_generator(limit=1, timeout_ms=3000):
#             self.frame = np.frombuffer(frame.get_buffer(), dtype=np.uint16).reshape((self.height, self.width))
#         return self.frame


#     data = np.frombuffer(pointer, dtype=np.uint8)
#     fst_uint8, mid_uint8, lst_uint8 = np.reshape(data, (data.shape[0] // 3, 3)).astype(np.uint16).T
#     fst_uint12 = (fst_uint8 << 4) + (mid_uint8 >> 4)
#     snd_uint12 = (lst_uint8 << 4) + (np.bitwise_and(15, mid_uint8))
# return np.reshape(np.concatenate((fst_uint12[:, None], snd_uint12[:, None]), axis=1), 2 * fst_uint12.shape[0])

    def getFps(self):
        return self.fps.get()
    def getExptime(self):
        return self.exptime.get()/1000
    def getGain(self):
        return f"{self.gain.get()} dB"
    def getTemp(self):
        # DeviceTemperature
        return self.temp.get()
    def getTempSetpoint(self):
        return f"{self.temp_setpoint.get()}"
    def getRoi(self):
        pass
    def getShutter(self):
        pass
    def getMode(self):
        pass

    def setFps(self, fps):
        self.fps.set(float(fps))
    def setExptime(self, exptime):
        exptime = float(exptime)
        if exptime > 1000/self.fps.get():
            self.setFps(1000/exptime)
        self.exptime.set(float(exptime)*1000)
    def setGain(self, gain):
        self.gain.set(float(gain))
    def setTemp(self, temp):
        pass
    def setRoi(self, roi):
        pass
    def setMode(self, hdr_mode):
        pass
    def setShutter(self, shutter):
        pass