"""
Script to execute the full runplan as defined in runplan.txt
"""
import numpy as np
# try:
#     import polars as pd
# except:
import pandas as pd
from datetime import datetime
from pathlib import Path
from time import sleep

#from Capture import Initialize, get_bias, get_dark
from Capture import capture

def execute(cam, runfile="runplan.csv", progress_func=None, exit_status_func=None):
    folder = f"data/{datetime.now():%Y%m%d}"
    Path(folder).mkdir(parents=True, exist_ok=True)
    print(folder)

    print(runfile)
    #with open(runfile, 'r') as f:
    #    print('a')
    plan = pd.read_csv(runfile)
    print(plan)
    n = len(plan)

    status = None
    for i,el in enumerate(plan.itertuples()):#rows(named=True)):
        progress_func(itt=i, range=n)
        if el.status:
            continue
        else:
            print(el)
            print(datetime.now())
            if el.type == "bias":
                if status!="covered":
                    input("Bias Frame: Place the cover on the camara and press Enter.")
                    status = "covered"
                
                print("Applying Camera Settings")
                cam.set('temp-set', el.temp)
                print(f'gain {el.gain}')
                cam.set('gain', el.gain)
                print('b')
                cam.bias()
                print('c')
                if np.abs(cam.get('temp-det') - el.temp) > 0.1:
                    while np.abs(cam.get('temp-det')[-1] - el.temp) > 0.1:
                        print("Cooling Down")
                        sleep(1)
                    print("Cooled Down")
                    sleep(5*60) # Sleep for an additional 5min to let the chip get into an equilibrium
                
                print(f"Starting Capture - {datetime.now()}")
                capture(cam, el.num_frames, file=folder+'/'+el.name+'.fits')
            elif el.type == "dark":
                if status!="covered":
                    input("Dark Frame: Place the cover on the camara and press Enter.")
                    status = "covered"
                cam.set('temp-set', el.temp)
                cam.set('gain', el.gain)
                cam.set('exptime', el.exptime)
                #cam.set(el.fps)
                if np.abs(cam.get('temp-det') - el.temp) > 0.1:
                    while np.abs(cam.get('temp-det') - el.temp) > 0.1:
                        sleep(1)
                    sleep(5*60) # Sleep for an additional 5min to let the chip get into an equilibrium

                print(f"Starting Capture - {datetime.now()}")
                capture(cam, el.num_frames, file=folder+'/'+el.name+'.fits')
            elif el.type == "flat":
                if status!=el.level:
                    input("Illuminate to level: ", el.level)
                    status = el.level
                cam.set('temp', el.temp)
                cam.set('gain', el.gain)
                cam.set('exptime', el.exptime)
                if np.abs(cam.get('temp-det') - el.temp) > 0.1:
                    while np.abs(cam.get('temp-det') - el.temp) > 0.1:
                        sleep(1)
                    sleep(5*60) # Sleep for an additional 5min to let the chip get into an equilibrium
                
                print(f"Starting Capture - {datetime.now()}")
                capture(cam, el.num_frames, file=folder+'/'+el.name+'.fits')
            else:
                raise NotImplementedError("")
            plan.loc[i, 'status'] = True
            plan.to_csv(runfile)
            print(el)
    exit_status_func("Complete")
    return 1
