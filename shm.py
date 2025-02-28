
import numpy as np

class SharedMemory:
    def __init__(self):
        self.img = None
        self.bg = None
        self.dit = None
        self.fps = None
        self.gain = None
        self.temp = None
        self.temp_setpoint = None
        self.bl = None
        self.roi = None
        self.mode = None
        self.shutter = None

# shm=dao.shm(f"/tmp/{shmName}.im.shm",buffer) 
#     shmBg=dao.shm(f"/tmp/{shmName}Bg.im.shm",buffer.astype(np.float32)*0)
#     shmDit=dao.shm(f"/tmp/{shmName}Dit.im.shm", np.zeros((1,1)).astype(np.float32))
#     shmFps=dao.shm(f"/tmp/{shmName}Fps.im.shm", np.zeros((1,1)).astype(np.float32))
#     shmGain=dao.shm(f"/tmp/{shmName}Gain.im.shm",np.zeros((1,1)).astype(np.float32))
#     shmTempSetPoint=dao.shm(f"/tmp/{shmName}TempSetPoint.im.shm",np.zeros((1,1)).astype(np.float32))
#     shmDetTemp = dao.shm(f"/tmp/{shmName}DetTemp.im.shm",np.zeros((1,1),dtype=np.float32))
#     shmBL = dao.shm(f"/tmp/{shmName}BL.im.shm", np.zeros((1,1)).astype(np.float32))
#     shmROI = dao.shm(f"/tmp/{shmName}ROI.im.shm", np.zeros((1,5), dtype=np.uint16))
#     shmMode = dao.shm(f"/tmp/{shmName}Mode.im.shm", np.zeros((1,1), dtype=np.uint16))
#     shmShutter = dao.shm(f"/tmp/{shmName}Shutter.im.shm", np.zeros((1,1), dtype=np.uint16))