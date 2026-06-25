import ctypes as ctypes

from picam.PiTypes import *

##### Some of the types defined dependent on an enum: PicamStringSize.  From picam.h we have the following:
"""
typedef enum PicamStringSize
{
    PicamStringSize_SensorName     =  64,
    PicamStringSize_SerialNumber   =  64,
    PicamStringSize_FirmwareName   =  64,
    PicamStringSize_FirmwareDetail = 256
} PicamStringSize;
"""
### Which is why I define the following:
PicamStringSize_SensorName = PicamStringSize_SerialNumber = PicamStringSize_FirmwareName = 64
PicamStringSize_FirmwareDetail = 256

"""
typedef struct PicamCameraID
{
    PicamModel          model;
    PicamComputerInterface computer_interface;
    pichar                 sensor_name[PicamStringSize_SensorName];
    pichar                 serial_number[PicamStringSize_SerialNumber];
} PicamCameraID;
"""
class PicamCameraID(ctypes.Structure):
    _fields_ = [("model", PicamModel),
                ("computer_interface", PicamComputerInterface),
                ("sensor_name", pichar * PicamStringSize_SensorName),
                ("serial_number", pichar * PicamStringSize_SerialNumber)]

# PicamHandle
PicamHandle = ctypes.c_void_p


# PicamFirmwareDetail
"""
typedef struct PicamFirmwareDetail
{
    pichar name[PicamStringSize_FirmwareName];
    pichar detail[PicamStringSize_FirmwareDetail];
} PicamFirmwareDetail;
"""

class PicamFirmwareDetail(ctypes.Structure):
    _fields_ = [("name", pichar * PicamStringSize_FirmwareName),
                ("detail", pichar * PicamStringSize_FirmwareDetail)]

##### Types defined on pp57-70 (chapter 4: Camera Parameter Values, Inofrmation, Constraints, and Commitment)
    ### Saving this for later!

##### Types defined on p76 (chapter 5: Camera Data Acquisition)

# PicamAvailableData
"""
typedef struct PicamAvailableData
{
    void* initial_readout;
    pi64s readout_count;
} PicamAvailableData;
"""
class PicamAvailableData(ctypes.Structure):
    _fields_ = [("initial_readout", ctypes.c_void_p), ("readout_count", pi64s)]

class PicamAvailableData2(ctypes.Structure):
    _fields_ = [ ( "initial_readout", ctypes.POINTER(type(ctypes.c_void_p()))), ("readout_count", pi64s)]

# PicamRoi
"""
typedef struct PicamRoi
{
    piint x;
    piint width;
    piint x_binning;
    piint y;
    piint height;
    piint y_binning;
} PicamRoi;
"""
class PicamRoi(ctypes.Structure):
    _fields_ = [("x", piint),
                ("width", piint),
                ("x_binning", piint),
                ("y", piint),
                ("height", piint),
                ("y_binning", piint)]
# PicamRois
"""                
typedef struct PicamRois
{
    PicamRoi* roi_array;
    piint     roi_count;
} PicamRois;
"""
class PicamRois(ctypes.Structure):
    _fields_ = [("roi_array", ctypes.POINTER(PicamRoi)),
                ("roi_count", piint)]
    def __init__(self, num):
        elems = (PicamRoi * num)()
        self.roi_array = ctypes.cast(elems,ctypes.POINTER(PicamRoi))
        self.roi_count = num

# PicamAcquisitionErrorsMask
"""
typedef enum PicamAcquisitionErrorsMask
{
    PicamAcquisitionErrorsMask_None           = 0x0,
    PicamAcquisitionErrorsMask_DataLost       = 0x1,
    PicamAcquisitionErrorsMask_ConnectionLost = 0x2
} PicamAcquisitionErrorsMask; /* (0x4) */
"""
PicamAcquisitionErrorsMask = ctypes.c_int

# PicamAcquisitionStatus
class PicamAcquisitionStatus(ctypes.Structure):
    _fields_ = [("running",pibln),
                ("errors",PicamAcquisitionErrorsMask),
                ("readout_rate",piflt)]

# PicamCollectionConstraint
class PicamCollectionConstraint(ctypes.Structure):
    _fields_ = [("scope", ctypes.c_void_p),
                ("severity", ctypes.c_void_p),
                ("values_array", ctypes.POINTER(piflt)),
                ("values_count", piint)]
    def __init__(self, num):
        elems = (piflt * num)()
        self.values_array = ctypes.cast(elems,ctypes.POINTER(piflt))