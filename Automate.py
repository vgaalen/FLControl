# Import the .NET class library
import clr

import sys
import os

# Import System.IO for saving and opening files
from System.IO import *

# Import c compatible List and String
from System import String
from System.Collections.Generic import List

# Add needed dll references
sys.path.append(os.environ['LIGHTFIELD_ROOT'])
sys.path.append(os.environ['LIGHTFIELD_ROOT']+"\\AddInViews")
clr.AddReference('PrincetonInstruments.LightFieldViewV5')
clr.AddReference('PrincetonInstruments.LightField.AutomationV5')
clr.AddReference('PrincetonInstruments.LightFieldAddInSupportServices')

# PI imports
from PrincetonInstruments.LightField.Automation import Automation
from PrincetonInstruments.LightField.AddIns import CameraSettings
from PrincetonInstruments.LightField.AddIns import DeviceType

def add_available_devices():
    # Add first available device and return
    for device in experiment.AvailableDevices:
        print("\n\tAdding Device...")
        experiment.Add(device)
        return device

# create a C# compatible List of type String object
list1 = List[String]()

# add the command line option for an empty experiment
list1.Add("/empty")

# Create the LightField Application (true for visible)
auto = Automation(True, List[String](list1))

# Get experiment object
experiment = auto.LightFieldApplication.Experiment

# Check for device and inform user if one is needed
if (experiment.AvailableDevices.Count == 0):
    print("Device not found. Please add a device and try again.")
else:
    import sys
    def onError(exception_type, value, traceback):
        print("\n\tRemoving Device...")
        experiment.Remove(device)
        print(traceback.format_exc())
        print(f"[{exception_type}]: {value}")
    sys.excepthook = onError

    device = add_available_devices()





def set_value(setting, value):    
    # Check for existence before setting
    # gain, adc rate, or adc quality
    if experiment.Exists(setting):        
        print (String.Format(
            "{0}{1} to {2}", "Setting ",
            setting, value))
        
        experiment.SetValue(setting, value)
        
def print_setting(setting):
    # Check for existence before
    # getting gain, adc rate, or adc quality
    if experiment.Exists(setting):
        print(String.Format(
            '{0} {1} = {2}', "\tReading ",
            str(setting),
            experiment.GetValue(setting)))


print_setting(CameraSettings.AdcAnalogGain)

