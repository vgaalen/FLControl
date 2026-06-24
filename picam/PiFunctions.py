import ctypes as ctypes
from picam.PiTypes import *
from picam.PiTypesMore import *

ptr = ctypes.pointer
ref = ctypes.byref

picamDll = '/opt/PrincetonInstruments/picam/runtime/libpicam.so.5.15.7'
try:
    picam = ctypes.cdll.LoadLibrary(picamDll)
    print("Picam Libary loaded")
except:
    print("Could not load Princeton Instruments DLL.  Make sure that Picam.dll is in the system path")


def returnError(value, err):
    if err == 0:
        return value
    else:
        mess = ReturnPicamError(err)
        return mess


def Picam_GetVersion():
    """ PICAM_API Picam_GetVersion( piint* major, piint* minor, piint* distribution, piint* released) """
    major, minor, distribution, released = piint(0), piint(0), piint(0), piint(0)
    err = picam.Picam_GetVersion(ctypes.byref(major), ctypes.byref(minor), ctypes.byref(distribution), ctypes.byref(released))
    return returnError((major.value, minor.value, distribution.value, released.value), err)


def Picam_IsLibraryInitialized():
    """ PICAM_API Picam_IsLibraryInitialized( pibln* inited ) """
    inited = pibln(False)
    err = picam.Picam_IsLibraryInitialized(ctypes.byref(inited))
    return returnError(inited.value, err)


def Picam_InitializeLibrary():
    """ PICAM_API Picam_InitializeLibrary( void ) """
    err = picam.Picam_InitializeLibrary()
    return returnError((),err)


def Picam_UninitializeLibrary():
    """ PICAM_API Picam_UninitializeLibrary( void ) """
    err = picam.Picam_UninitializeLibrary()
    return returnError((),err)


def Picam_DestroyString(s):
    """ PICAM_API Picam_DestroyString( const pichar* s ) """
    err = picam.Picam_DestroyString(s)
    return returnError((),err)


def Picam_GetEnumerationString(type, value, size=20):
    """ PICAM_API Picam_GetEnumerationString( PicamEnumeratedType type, piint value, const pichar** s) """
    s = (pichar * size)([""] * size)
    err = picam.Picam_GetEnumerationString(type, value, ref(s))
    return returnError(s.value, err)


def Picam_DestroyCameraIDs(id_array):
    """ PICAM_API Picam_DestroyCameraIDs( const PicamCameraID* id_array ) """
    err = picam.Picam_DestroyCameraIDs(id_array)
    return returnError((),err)


def Picam_GetAvailableCameraIDs():
    """ PICAM_API Picam_GetAvailableCameraIDs( const PicamCameraID** id_array, piint* id_count) """
    id_array = PicamCameraID(0)
    id_count = piint(0)
    err = picam.Picam_GetAvailableCameraIDs(ref(id_array), ref(id_count))
    if err == 0 and id_count.value > 0:
        id_array = (PicamCameraID * id_count.value)(*[PicamCameraID(0)] * id_count.value)
        err = picam.Picam_GetAvailableCameraIDs(ref(id_array), ref(id_count))
    return returnError((id_array, id_count), err)


def Picam_GetUnavailableCameraIDs():
    """ PICAM_API Picam_GetUnavailableCameraIDs( const PicamCameraID** id_array, piint* id_count) """
    id_array = PicamCameraID(0)
    id_count = piint(0)
    err = picam.Picam_GetUnavailableCameraIDs(ref(id_array), ref(id_count))
    if err == 0 and id_count>0:
        id_array = (PicamCameraID * id_count.value)(*[0]*id_count.value)
        err = picam.Picam_GetUnavailableCameraIDs(ref(id_array), ref(id_count))
    return returnError((id_array,id_count),err)


def Picam_IsCameraIDConnected(id):
    """ PICAM_API Picam_IsCameraIDConnected( const PicamCameraID* id, pibln* connected) """
    connected = pibln(False)
    err = picam.Picam_IsCameraIDConnected(id, ref(connected))
    return returnError(connected.value, err)


def Picam_IsCameraIDOpenElsewhere(id):
    """ PICAM_API Picam_IsCameraIDOpenElsewhere( const PicamCameraID* id, pibln* open_elsewhere) """
    open_elsewhere = pibln(False)
    err = picam.Picam_IsCameraIDOpenElsewhere(id, ref(open_elsewhere))
    return returnError(open_elsewhere.value, err)


def Picam_DestroyHandles(handle_array):
    """ PICAM_API Picam_DestroyHandles( const PicamHandle* handle_array ) """
    err = picam.Picam_DestroyHandles(handle_array)
    return returnError((),err)


def Picam_OpenFirstCamera():
    """ PICAM_API Picam_OpenFirstCamera( PicamHandle* camera ) """
    camera = PicamHandle()
    err = picam.Picam_OpenFirstCamera(ref(camera))
    return returnError(camera, err)


def Picam_OpenCamera(id):
    """ PICAM_API Picam_OpenCamera( const PicamCameraID* id, PicamHandle* camera) """
    camera = PicamHandle()
    err = picam.Picam_OpenCamera(id, ref(camera))
    return returnError(camera, err)


def Picam_CloseCamera(camera):
    """ PICAM_API Picam_CloseCamera( PicamHandle camera ) """
    err = picam.Picam_CloseCamera(camera)
    return returnError((), err)


def Picam_GetOpenCameras():
    """ PICAM_API Picam_GetOpenCameras( const PicamHandle** camera_array, piint* camera_count) """
    camera_array = (PicamHandle * 0)()
    camera_count = piint(0)
    err = picam.Picam_GetOpenCameras(ref(camera_array), ref(camera_count))
    return returnError((camera_array,camera_count), err)


def Picam_IsCameraConnected(camera):
    """ PICAM_API Picam_IsCameraConnected( PicamHandle camera, pibln* connected) """
    connected = pibln(False)
    err = picam.Picam_IsCameraConnected(camera, ref(connected))
    return returnError(connected.value, err)


def Picam_GetCameraID(camera):
    """ PICAM_API Picam_GetCameraID( PicamHandle camera, PicamCameraID* id) """
    id = PicamCameraID()
    err = picam.Picam_GetCameraID(camera, ref(id))
    return returnError(id, err)


def Picam_DestroyFirmwareDetails(firmware_array):
    """ PICAM_API Picam_DestroyFirmwareDetails( const PicamFirmwareDetail* firmware_array) """
    err = picam.Picam_DestroyFirmwareDetails(ref(firmware_array))
    return returnError((), err)


def Picam_GetFirmwareDetails(id):
    """ PICAM_API Picam_GetFirmwareDetails( const PicamCameraID* id, const PicamFirmwareDetail** firmware_array, piint* firmware_count) """
    firmware_array = PicamFirmwareDetail()
    firmware_count = piint(0)
    err = picam.Picam_GetFirmwareDetails(ref(id), ref(firmware_array), ref(firmware_count))
    if firmware_count.value > 1:
        firmware_array = (PicamFirmwareDetail * firmware_count.value)([b""] * firmware_count.value)
        err = picam.Picam_GetFirmwareDetails(ref(id), ref(firmware_array), ref(firmware_count))
    return returnError((firmware_array,firmware_count), err)


def Picam_DestroyModels(model_array):
    """ PICAM_API Picam_DestroyModels( const PicamModel* model_array ) """
    err = picam.Picam_DestroyModels(ref(model_array))
    return returnError((), err)


def Picam_GetAvailableDemoCameraModels(model_array, model_count):
    """ PICAM_API Picam_GetAvailableDemoCameraModels( const PicamModel** model_array, piint* model_count) """
    model_array = PicamModel()
    model_count = piint(0)
    err = picam.Picam_GetAvailableDemoCameraModels(ref(model_array), ref(model_count))
    if model_count.value > 1:
        model_array = (PicamModel * model_count.value)([0] * model_count.value)
        err = picam.Picam_GetAvailableDemoCameraModels(ref(model_array), ref(model_count))
    return returnError((model_array,model_count), err)


def Picam_ConnectDemoCamera(model, serial_number):
    """ PICAM_API Picam_ConnectDemoCamera( PicamModel model, const pichar* serial_number, PicamCameraID* id) """
    id = PicamCameraID()
    err = picam.Picam_ConnectDemoCamera(model, ref(serial_number), ref(id))
    return returnError(id, err)


def Picam_DisconnectDemoCamera(id):
    """ PICAM_API Picam_DisconnectDemoCamera( const PicamCameraID* id ) """
    err = picam.Picam_DisconnectDemoCamera(ref(id))
    return returnError((), err)


def Picam_IsDemoCamera(id):
    """ PICAM_API Picam_IsDemoCamera( const PicamCameraID* id, pibln* demo) """
    demo = pibln(False)
    err = picam.Picam_IsDemoCamera(id, ref(demo))
    return returnError(demo.value, err)


def Picam_GetParameterIntegerValue(camera, parameter):
    """ PICAM_API Picam_GetParameterIntegerValue( PicamHandle camera, PicamParameter parameter, piint* value) """
    value = piint(0)
    err = picam.Picam_GetParameterIntegerValue(camera, parameter, ref(value))
    return returnError(value.value, err)


def Picam_SetParameterIntegerValue(camera, parameter, value):
    """ PICAM_API Picam_SetParameterIntegerValue( PicamHandle camera, PicamParameter parameter, piint value) """
    err = picam.Picam_SetParameterIntegerValue(camera, parameter, value)
    return returnError((), err)


def Picam_CanSetParameterIntegerValue(camera, parameter, value):
    """ PICAM_API Picam_CanSetParameterIntegerValue( PicamHandle camera, PicamParameter parameter, piint value, pibln* settable) """
    settable = pibln(False)
    err = picam.Picam_CanSetParameterIntegerValue(camera, parameter, value, ref(settable))
    return returnError(settable.value, err)


def Picam_GetParameterLargeIntegerValue(camera, parameter):
    """ PICAM_API Picam_GetParameterLargeIntegerValue( PicamHandle camera, PicamParameter parameter, pi64s* value) """
    value = pi64s(0)
    err = picam.Picam_GetParameterLargeIntegerValue(camera, parameter, ref(value))
    return returnError(value.value, err)


def Picam_SetParameterLargeIntegerValue(camera, parameter, value):
    """ PICAM_API Picam_SetParameterLargeIntegerValue( PicamHandle camera, PicamParameter parameter, pi64s value) """
    err = picam.Picam_SetParameterLargeIntegerValue(camera, parameter, value)
    return returnError((), err)


def Picam_CanSetParameterLargeIntegerValue(camera, parameter, value):
    """ PICAM_API Picam_CanSetParameterLargeIntegerValue( PicamHandle camera, PicamParameter parameter, pi64s value, pibln* settable) """
    settable = pibln(False)
    err = picam.Picam_CanSetParameterLargeIntegerValue(camera, parameter, value, ref(settable))
    return returnError(settable.value, err)


def Picam_GetParameterFloatingPointValue(camera, parameter):
    """ PICAM_API Picam_GetParameterFloatingPointValue( PicamHandle camera, PicamParameter parameter, piflt* value) """
    value = piflt(0.)
    err = picam.Picam_GetParameterFloatingPointValue(camera, parameter, ref(value))
    return returnError(value.value, err)


def Picam_SetParameterFloatingPointValue(camera, parameter, value):
    """ PICAM_API Picam_SetParameterFloatingPointValue( PicamHandle camera, PicamParameter parameter, piflt value) """
    err = picam.Picam_SetParameterFloatingPointValue(camera, parameter, value)
    return returnError((), err)


def Picam_CanSetParameterFloatingPointValue(camera, parameter, value):
    """ PICAM_API Picam_CanSetParameterFloatingPointValue( PicamHandle camera, PicamParameter parameter, piflt value, pibln* settable) """
    settable = pibln(False)
    err = picam.Picam_CanSetParameterFloatingPointValue(camera, parameter, value, ref(settable))
    return returnError(settable.value, err)


def Picam_DestroyRois(rois):
    """ PICAM_API Picam_DestroyRois( const PicamRois* rois ) """
    err = picam.Picam_DestroyRois(ref(rois))
    return returnError((), err)


def Picam_GetParameterRoisValue(camera, parameter, num=4):
    """ PICAM_API Picam_GetParameterRoisValue( PicamHandle camera, PicamParameter parameter, const PicamRois** value) """
    value = PicamRois(num=4)
    err = picam.Picam_GetParameterRoisValue(camera, parameter, ref(value))
    return returnError(value, err)


def Picam_SetParameterRoisValue(camera, parameter, value):
    """ PICAM_API Picam_SetParameterRoisValue( PicamHandle camera, PicamParameter parameter, const PicamRois* value) """
    err = picam.Picam_SetParameterRoisValue(camera, parameter, value)
    return returnError((), err)


def Picam_CanSetParameterRoisValue(camera, parameter, value):
    """ PICAM_API Picam_CanSetParameterRoisValue( PicamHandle camera, PicamParameter parameter, const PicamRois* value, pibln* settable) """
    settable = pibln(False)
    err = picam.Picam_CanSetParameterRoisValue(camera, parameter, value, ref(settable))
    return returnError(settable.value, err)


def Picam_DestroyPulses(pulses):
    """ PICAM_API Picam_DestroyPulses( const PicamPulse* pulses ) """
    err = picam.Picam_DestroyPulses(pulses)
    return returnError((), err)


def Picam_GetParameterPulseValue(camera, parameter, value):
    """ PICAM_API Picam_GetParameterPulseValue( PicamHandle camera, PicamParameter parameter, const PicamPulse** value) """
    err = picam.Picam_GetParameterPulseValue(camera, parameter, value)
    err = ReturnPicamError(err)
    return err


def Picam_SetParameterPulseValue(camera, parameter, value):
    """ PICAM_API Picam_SetParameterPulseValue( PicamHandle camera, PicamParameter parameter, const PicamPulse* value) """
    err = picam.Picam_SetParameterPulseValue(camera, parameter, value)
    err = ReturnPicamError(err)
    return err


def Picam_CanSetParameterPulseValue(camera, parameter, value, settable):
    """ PICAM_API Picam_CanSetParameterPulseValue( PicamHandle camera, PicamParameter parameter, const PicamPulse* value, pibln* settable) """
    err = picam.Picam_CanSetParameterPulseValue(camera, parameter, value, settable)
    err = ReturnPicamError(err)
    return err


def Picam_DestroyModulations(modulations):
    """ PICAM_API Picam_DestroyModulations( const PicamModulations* modulations ) """
    err = picam.Picam_DestroyModulations(modulations)
    err = ReturnPicamError(err)
    return err


def Picam_GetParameterModulationsValue(camera, parameter, value):
    """ PICAM_API Picam_GetParameterModulationsValue( PicamHandle camera, PicamParameter parameter, const PicamModulations** value) """
    err = picam.Picam_GetParameterModulationsValue(camera, parameter, value)
    err = ReturnPicamError(err)
    return err


def Picam_SetParameterModulationsValue(camera, parameter, value):
    """ PICAM_API Picam_SetParameterModulationsValue( PicamHandle camera, PicamParameter parameter, const PicamModulations* value) """
    err = picam.Picam_SetParameterModulationsValue(camera, parameter, value)
    err = ReturnPicamError(err)
    return err


def Picam_CanSetParameterModulationsValue(camera, parameter, value, settable):
    """ PICAM_API Picam_CanSetParameterModulationsValue( PicamHandle camera, PicamParameter parameter, const PicamModulations* value, pibln* settable) """
    err = picam.Picam_CanSetParameterModulationsValue(camera, parameter, value, settable)
    err = ReturnPicamError(err)
    return err


def Picam_GetParameterIntegerDefaultValue(camera, parameter):
    """ PICAM_API Picam_GetParameterIntegerDefaultValue( PicamHandle camera, PicamParameter parameter, piint* value) """
    value = piint(0)
    err = picam.Picam_GetParameterIntegerDefaultValue(camera, parameter, ref(value))
    return returnError(value.value, err)


def Picam_GetParameterLargeIntegerDefaultValue(camera, parameter):
    """ PICAM_API Picam_GetParameterLargeIntegerDefaultValue( PicamHandle camera, PicamParameter parameter, pi64s* value) """
    value = pi64s(0)
    err = picam.Picam_GetParameterLargeIntegerDefaultValue(camera, parameter, ref(value))
    return returnError(value.value, err)


def Picam_GetParameterFloatingPointDefaultValue(camera, parameter, value):
    """ PICAM_API Picam_GetParameterFloatingPointDefaultValue( PicamHandle camera, PicamParameter parameter, piflt* value) """
    value = piflt(0.)
    err = picam.Picam_GetParameterFloatingPointDefaultValue(camera, parameter, ref(value))
    return returnError(value.value, err)


def Picam_GetParameterRoisDefaultValue(camera, parameter, value):
    """ PICAM_API Picam_GetParameterRoisDefaultValue( PicamHandle camera, PicamParameter parameter, const PicamRois** value) """
    value = PicamRois(0)
    err = picam.Picam_GetParameterRoisDefaultValue(camera, parameter, ref(value))
    return returnError(value, err)


def Picam_GetParameterPulseDefaultValue(camera, parameter, value):
    """ PICAM_API Picam_GetParameterPulseDefaultValue( PicamHandle camera, PicamParameter parameter, const PicamPulse** value) """
    err = picam.Picam_GetParameterPulseDefaultValue(camera, parameter, value)
    err = ReturnPicamError(err)
    return err


def Picam_GetParameterModulationsDefaultValue(camera, parameter, value):
    """ PICAM_API Picam_GetParameterModulationsDefaultValue( PicamHandle camera, PicamParameter parameter, const PicamModulations** value) """
    err = picam.Picam_GetParameterModulationsDefaultValue(camera, parameter, value)
    err = ReturnPicamError(err)
    return err


def Picam_CanSetParameterOnline(camera, parameter):
    """ PICAM_API Picam_CanSetParameterOnline( PicamHandle camera, PicamParameter parameter, pibln* onlineable) """
    onlineable = pibln(False)
    err = picam.Picam_CanSetParameterOnline(camera, parameter, ref(onlineable))
    return returnError(onlineable.value, err)


def Picam_SetParameterIntegerValueOnline(camera, parameter, value):
    """ PICAM_API Picam_SetParameterIntegerValueOnline( PicamHandle camera, PicamParameter parameter, piint value) """
    err = picam.Picam_SetParameterIntegerValueOnline(camera, parameter, value)
    return returnError((), err)


def Picam_SetParameterFloatingPointValueOnline(camera, parameter, value):
    """ PICAM_API Picam_SetParameterFloatingPointValueOnline( PicamHandle camera, PicamParameter parameter, piflt value) """
    err = picam.Picam_SetParameterFloatingPointValueOnline(camera, parameter, value)
    return returnError((), err)


def Picam_SetParameterPulseValueOnline(camera, parameter, value):
    """ PICAM_API Picam_SetParameterPulseValueOnline( PicamHandle camera, PicamParameter parameter, const PicamPulse* value) """
    err = picam.Picam_SetParameterPulseValueOnline(camera, parameter, value)
    return returnError((), err)


def Picam_CanReadParameter(camera, parameter):
    """ PICAM_API Picam_CanReadParameter( PicamHandle camera, PicamParameter parameter, pibln* readable) """
    readable = pibln(False)
    err = picam.Picam_CanReadParameter(camera, parameter, readable)
    return returnError(readable.value, err)


def Picam_ReadParameterIntegerValue(camera, parameter):
    """ PICAM_API Picam_ReadParameterIntegerValue( PicamHandle camera, PicamParameter parameter, piint* value) """
    value = piint(0)
    err = picam.Picam_ReadParameterIntegerValue(camera, parameter, ref(value))
    return returnError(value.value, err)


def Picam_ReadParameterFloatingPointValue(camera, parameter):
    """ PICAM_API Picam_ReadParameterFloatingPointValue( PicamHandle camera, PicamParameter parameter, piflt* value) """
    value = piflt(0.)
    err = picam.Picam_ReadParameterFloatingPointValue(camera, parameter, ref(value))
    return returnError(value.value, err)


def Picam_DestroyParameters(parameter_array):
    """ PICAM_API Picam_DestroyParameters( const PicamParameter* parameter_array ) """
    err = picam.Picam_DestroyParameters(parameter_array)
    return returnError((), err)


def Picam_GetParameters(camera, parameter_array, parameter_count):
    """ PICAM_API Picam_GetParameters( PicamHandle camera, const PicamParameter** parameter_array, piint* parameter_count) """
    err = picam.Picam_GetParameters(camera, parameter_array, parameter_count)
    err = ReturnPicamError(err)
    return err


def Picam_DoesParameterExist(camera, parameter):
    """ PICAM_API Picam_DoesParameterExist( PicamHandle camera, PicamParameter parameter, pibln* exists) """
    exists = pibln(False)
    err = picam.Picam_DoesParameterExist(camera, parameter, exists)
    return returnError(exists.value, err)


def Picam_IsParameterRelevant(camera, parameter):
    """ PICAM_API Picam_IsParameterRelevant( PicamHandle camera, PicamParameter parameter, pibln* relevant) """
    relevant = pibln(False)
    err = picam.Picam_IsParameterRelevant(camera, parameter, relevant)
    return returnError(relevant.value, err)


def Picam_GetParameterValueType(camera, parameter, type):
    """ PICAM_API Picam_GetParameterValueType( PicamHandle camera, PicamParameter parameter, PicamValueType* type) """
    err = picam.Picam_GetParameterValueType(camera, parameter, type)
    err = ReturnPicamError(err)
    return err


def Picam_GetParameterEnumeratedType(camera, parameter, type):
    """ PICAM_API Picam_GetParameterEnumeratedType( PicamHandle camera, PicamParameter parameter, PicamEnumeratedType* type) """
    err = picam.Picam_GetParameterEnumeratedType(camera, parameter, type)
    err = ReturnPicamError(err)
    return err


def Picam_GetParameterValueAccess(camera, parameter, access):
    """ PICAM_API Picam_GetParameterValueAccess( PicamHandle camera, PicamParameter parameter, PicamValueAccess* access) """
    err = picam.Picam_GetParameterValueAccess(camera, parameter, access)
    err = ReturnPicamError(err)
    return err


def Picam_GetParameterConstraintType(camera, parameter, type):
    """ PICAM_API Picam_GetParameterConstraintType( PicamHandle camera, PicamParameter parameter, PicamConstraintType* type) """
    err = picam.Picam_GetParameterConstraintType(camera, parameter, type)
    err = ReturnPicamError(err)
    return err


def Picam_DestroyCollectionConstraints(constraint_array):
    """ PICAM_API Picam_DestroyCollectionConstraints( const PicamCollectionConstraint* constraint_array) """
    err = picam.Picam_DestroyCollectionConstraints(constraint_array)
    err = ReturnPicamError(err)
    return err


def Picam_GetParameterCollectionConstraint(camera, parameter, category, constraint):
    """ PICAM_API Picam_GetParameterCollectionConstraint( PicamHandle camera, PicamParameter parameter, PicamConstraintCategory category, const PicamCollectionConstraint** constraint) """
    err = picam.Picam_GetParameterCollectionConstraint(camera, parameter, category, constraint)
    err = ReturnPicamError(err)
    return err


def Picam_DestroyRangeConstraints(constraint_array):
    """ PICAM_API Picam_DestroyRangeConstraints( const PicamRangeConstraint* constraint_array) """
    err = picam.Picam_DestroyRangeConstraints(constraint_array)
    err = ReturnPicamError(err)
    return err


def Picam_GetParameterRangeConstraint(camera, parameter, category, constraint):
    """ PICAM_API Picam_GetParameterRangeConstraint( PicamHandle camera, PicamParameter parameter, PicamConstraintCategory category, const PicamRangeConstraint** constraint) """
    err = picam.Picam_GetParameterRangeConstraint(camera, parameter, category, constraint)
    err = ReturnPicamError(err)
    return err


def Picam_DestroyRoisConstraints(constraint_array):
    """ PICAM_API Picam_DestroyRoisConstraints( const PicamRoisConstraint* constraint_array) """
    err = picam.Picam_DestroyRoisConstraints(constraint_array)
    err = ReturnPicamError(err)
    return err


def Picam_GetParameterRoisConstraint(camera, parameter, category, constraint):
    """ PICAM_API Picam_GetParameterRoisConstraint( PicamHandle camera, PicamParameter parameter, PicamConstraintCategory category, const PicamRoisConstraint** constraint) """
    err = picam.Picam_GetParameterRoisConstraint(camera, parameter, category, constraint)
    err = ReturnPicamError(err)
    return err


def Picam_DestroyPulseConstraints(constraint_array):
    """ PICAM_API Picam_DestroyPulseConstraints( const PicamPulseConstraint* constraint_array) """
    err = picam.Picam_DestroyPulseConstraints(constraint_array)
    err = ReturnPicamError(err)
    return err


def Picam_GetParameterPulseConstraint(camera, parameter, category, constraint):
    """ PICAM_API Picam_GetParameterPulseConstraint( PicamHandle camera, PicamParameter parameter, PicamConstraintCategory category, const PicamPulseConstraint** constraint) """
    err = picam.Picam_GetParameterPulseConstraint(camera, parameter, category, constraint)
    err = ReturnPicamError(err)
    return err


def Picam_DestroyModulationsConstraints(constraint_array):
    """ PICAM_API Picam_DestroyModulationsConstraints( const PicamModulationsConstraint* constraint_array) """
    err = picam.Picam_DestroyModulationsConstraints(constraint_array)
    err = ReturnPicamError(err)
    return err


def Picam_GetParameterModulationsConstraint(camera, parameter, category, constraint):
    """ PICAM_API Picam_GetParameterModulationsConstraint( PicamHandle camera, PicamParameter parameter, PicamConstraintCategory category, const PicamModulationsConstraint** constraint) """
    err = picam.Picam_GetParameterModulationsConstraint(camera, parameter, category, constraint)
    err = ReturnPicamError(err)
    return err


def Picam_AreParametersCommitted(camera):
    """ PICAM_API Picam_AreParametersCommitted( PicamHandle camera, pibln* committed) """
    committed = pibln(False)
    err = picam.Picam_AreParametersCommitted(camera, committed)
    return returnError(committed.value, err)


def Picam_CommitParameters(camera, failed_parameter_array, failed_parameter_count):
    """ PICAM_API Picam_CommitParameters( PicamHandle camera, const PicamParameter** failed_parameter_array, piint* failed_parameter_count) """
    err = picam.Picam_CommitParameters(camera, failed_parameter_array, failed_parameter_count)
    return returnError((), err)


def Picam_Acquire(camera, readout_count, readout_time_out, available, errors):
    """ PICAM_API Picam_Acquire( PicamHandle camera, pi64s readout_count, piint readout_time_out, PicamAvailableData* available, PicamAcquisitionErrorsMask* errors) """
    Picam_Acquire.argtypes = []
    Picam_Acquire.restype = piint
    err = picam.Picam_Acquire(camera, readout_count, readout_time_out, available, errors)
    return returnError((), err)


def Picam_StartAcquisition(camera):
    """ PICAM_API Picam_StartAcquisition( PicamHandle camera ) """
    err = picam.Picam_StartAcquisition(camera)
    return returnError((), err)


def Picam_StopAcquisition(camera):
    """ PICAM_API Picam_StopAcquisition( PicamHandle camera ) """
    err = picam.Picam_StopAcquisition(camera)
    return returnError((), err)


def Picam_IsAcquisitionRunning(camera):
    """ PICAM_API Picam_IsAcquisitionRunning( PicamHandle camera, pibln* running) """
    running = pibln(False)
    err = picam.Picam_IsAcquisitionRunning(camera, ref(running))
    return returnError(running.value, err)


def Picam_WaitForAcquisitionUpdate(camera, readout_time_out, available, status):
    """ PICAM_API Picam_WaitForAcquisitionUpdate( PicamHandle camera, piint readout_time_out, PicamAvailableData* available, PicamAcquisitionStatus* status) """
    Picam_WaitForAcquisitionUpdate.argtypes = []
    Picam_WaitForAcquisitionUpdate.restype = piint
    err = picam.Picam_WaitForAcquisitionUpdate(camera, readout_time_out, available, status)
    return returnError((), err)

## New additions from here
def Picam_RestoreParametersToDefaultValues(camera):
    """ PICAM_API Picam_RestoreParametersToDefaultValues(PicamHandle camera) """
    err = Picam_RestoreParametersToDefaultValues(camera)
    return returnError((), err)


def ReturnPicamError(errcode):
    """expects integer error code.  Returns string with description"""
    if (errcode == 0):
        err = "PicamError_None"
    elif (errcode == 4):
        err = "PicamError_UnexpectedError"
    elif (errcode == 3):
        err = "PicamError_UnexpectedNullPointer"
    elif (errcode == 35):
        err = "PicamError_InvalidPointer"
    elif (errcode == 39):
        err = "PicamError_InvalidCount"
    elif (errcode == 42):
        err = "PicamError_InvalidOperation"
    elif (errcode == 1):
        err = "PicamError_LibraryNotInitialized"
    elif (errcode == 5):
        err = "PicamError_LibraryAlreadyInitialized"
    elif (errcode == 16):
        err = "PicamError_InvalidEnumeratedType"
    elif (errcode == 17):
        err = "PicamError_EnumerationValueNotDefined"
    elif (errcode == 18):
        err = "PicamError_NotDiscoveringCameras"
    elif (errcode == 19):
        err = "PicamError_AlreadyDiscoveringCameras"
    elif (errcode == 34):
        err = "PicamError_NoCamerasAvailable"
    elif (errcode == 7):
        err = "PicamError_CameraAlreadyOpened"
    elif (errcode == 8):
        err = "PicamError_InvalidCameraID"
    elif (errcode == 9):
        err = "PicamError_InvalidHandle"
    elif (errcode == 15):
        err = "PicamError_DeviceCommunicationFailed"
    elif (errcode == 23):
        err = "PicamError_DeviceDisconnected"
    elif (errcode == 24):
        err = "PicamError_DeviceOpenElsewhere"
    elif (errcode == 6):
        err = "PicamError_InvalidDemoModel"
    elif (errcode == 21):
        err = "PicamError_InvalidDemoSerialNumber"
    elif (errcode == 22):
        err = "PicamError_DemoAlreadyConnected"
    elif (errcode == 40):
        err = "PicamError_DemoNotSupported"
    elif (errcode == 11):
        err = "PicamError_ParameterHasInvalidValueType"
    elif (errcode == 13):
        err = "PicamError_ParameterHasInvalidConstraintType"
    elif (errcode == 12):
        err = "PicamError_ParameterDoesNotExist"
    elif (errcode == 10):
        err = "PicamError_ParameterValueIsReadOnly"
    elif (errcode == 2):
        err = "PicamError_InvalidParameterValue"
    elif (errcode == 38):
        err = "PicamError_InvalidConstraintCategory"
    elif (errcode == 14):
        err = "PicamError_ParameterValueIsIrrelevant"
    elif (errcode == 25):
        err = "PicamError_ParameterIsNotOnlineable"
    elif (errcode == 26):
        err = "PicamError_ParameterIsNotReadable"
    elif (errcode == 28):
        err = "PicamError_InvalidParameterValues"
    elif (errcode == 29):
        err = "PicamError_ParametersNotCommitted"
    elif (errcode == 30):
        err = "PicamError_InvalidAcquisitionBuffer"
    elif (errcode == 36):
        err = "PicamError_InvalidReadoutCount"
    elif (errcode == 37):
        err = "PicamError_InvalidReadoutTimeOut"
    elif (errcode == 31):
        err = "PicamError_InsufficientMemory"
    elif (errcode == 20):
        err = "PicamError_AcquisitionInProgress"
    elif (errcode == 27):
        err = "PicamError_AcquisitionNotInProgress"
    elif (errcode == 32):
        err = "PicamError_TimeOutOccurred"
    elif (errcode == 33):
        err = "PicamError_AcquisitionUpdatedHandlerRegistered"
    elif (errcode == 41):
        err = "PicamError_InvalidNvramSection"
    else:
        err = "Unknown Error"
    return err

